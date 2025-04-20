"""
End-to-end tests for the deployed Songs API (HTTP API Gateway v2).

These tests:
1. Locate the deployed API using API Gateway v2
2. Make real HTTP requests to the API endpoints
3. Validate the full CRUD lifecycle for songs in DynamoDB
4. Fetch Lambda logs when tests fail
"""

import os
import json
import boto3
import pytest
import requests
import subprocess
from uuid import uuid4
from time import sleep
from datetime import datetime, timedelta
from pprint import pprint
from botocore.exceptions import ClientError

def get_api_url():
    """Locate the Songs HTTP API (v2) endpoint from AWS."""
    client = boto3.client("apigatewayv2", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    try:
        apis = client.get_apis()
        for api in apis["Items"]:
            if "songs" in api["Name"].lower():
                return api["ApiEndpoint"]
        raise ValueError("Could not find Songs API in API Gateway v2")
    except ClientError as e:
        if e.response["Error"]["Code"] == "UnrecognizedClientException":
            raise Exception("AWS credentials not configured. Run 'aws configure' or set AWS env vars.") from e
        raise

def test_presigned_url(api_url):
    """Test the pre-signed URL endpoint."""
    # Create a test file in S3
    s3 = boto3.client('s3')
    bucket = 'ourchants-songs'
    key = f'test-{uuid4()}.mp3'
    
    try:
        # Upload a test file
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=b'test content'
        )
        
        # Request pre-signed URL
        response = requests.post(
            f"{api_url}/presigned-url",
            json={
                "bucket": bucket,
                "key": key
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "expiresIn" in data
        assert data["expiresIn"] == 3600
        
        # Verify the URL works
        url_response = requests.get(data["url"])
        assert url_response.status_code == 200
        assert url_response.content == b'test content'
        
    finally:
        # Clean up
        try:
            s3.delete_object(Bucket=bucket, Key=key)
        except Exception as e:
            print(f"Error cleaning up test file: {e}")

def test_presigned_url_errors(api_url):
    """Test error cases for the pre-signed URL endpoint."""
    # Test missing key
    response = requests.post(
        f"{api_url}/presigned-url",
        json={}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "code" in data
    assert data["code"] == "MISSING_REQUIRED_FIELD"
    
    # Test non-existent bucket
    response = requests.post(
        f"{api_url}/presigned-url",
        json={
            "bucket": "non-existent-bucket",
            "key": "test.mp3"
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "code" in data
    assert data["code"] == "BUCKET_NOT_FOUND"
    
    # Test non-existent object
    response = requests.post(
        f"{api_url}/presigned-url",
        json={
            "bucket": "ourchants-songs",
            "key": "non-existent-object.mp3"
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "code" in data
    assert data["code"] == "OBJECT_NOT_FOUND"

def test_api_lifecycle(api_url, test_song):
    """Test full lifecycle: create → get → list → update → delete."""
    try:
        # Create song
        response = requests.post(f"{api_url}/songs", json=test_song)
        assert response.status_code == 201
        created_song = response.json()
        assert "song_id" in created_song
        song_id = created_song["song_id"]
        
        # Get song
        response = requests.get(f"{api_url}/songs/{song_id}")
        assert response.status_code == 200
        retrieved_song = response.json()
        assert retrieved_song["song_id"] == song_id
        
        # List songs
        response = requests.get(f"{api_url}/songs")
        assert response.status_code == 200
        songs = response.json()
        assert isinstance(songs, list)
        assert any(s["song_id"] == song_id for s in songs)
        
        # Update song
        updated_data = {**test_song, "title": "Updated Title"}
        response = requests.put(f"{api_url}/songs/{song_id}", json=updated_data)
        assert response.status_code == 200
        updated_song = response.json()
        assert updated_song["title"] == "Updated Title"
        
        # Delete song
        response = requests.delete(f"{api_url}/songs/{song_id}")
        assert response.status_code == 204
        
        # Verify deletion
        response = requests.get(f"{api_url}/songs/{song_id}")
        assert response.status_code == 404
        
    except AssertionError as e:
        # Get Lambda function name from API Gateway
        client = boto3.client("apigatewayv2", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        apis = client.get_apis()
        for api in apis["Items"]:
            if "songs" in api["Name"].lower():
                api_id = api["ApiId"]
                break
        else:
            raise ValueError("Could not find Songs API in API Gateway v2")
        
        # Get Lambda function name from API Gateway integration
        integrations = client.get_integrations(ApiId=api_id)
        for integration in integrations["Items"]:
            if integration["IntegrationType"] == "AWS_PROXY":
                lambda_arn = integration["IntegrationUri"].split(":")[-1]
                function_name = lambda_arn.split("/")[-1]
                break
        else:
            raise ValueError("Could not find Lambda integration for API")
        
        # Fetch and print logs
        logs = get_lambda_logs(function_name)
        print("\nLambda Logs:")
        print("=" * 80)
        print(logs)
        print("=" * 80)
        raise

def get_lambda_logs(function_name):
    """Fetch logs from CloudWatch for the Lambda function."""
    client = boto3.client("logs", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    log_group = f"/aws/lambda/{function_name}"
    
    try:
        response = client.get_log_events(
            logGroupName=log_group,
            limit=50
        )
        return "\n".join(event["message"] for event in response["events"])
    except ClientError as e:
        return f"Error fetching logs: {str(e)}"

@pytest.fixture
def api_url():
    """Get the API URL."""
    return get_api_url()

@pytest.fixture
def test_song():
    """Create a test song."""
    return {
        "title": f"Test Song {uuid4()}",
        "artist": "Test Artist",
        "album": "Test Album",
        "bpm": "120",
        "composer": "Test Composer",
        "version": "1.0",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": "test.mp3",
        "filepath": "Media/test.mp3",
        "description": "Test description",
        "lineage": ["original"],
        "s3_uri": "s3://ourchants-songs/test.mp3"
    }

def test_error_handling(api_url):
    """Verify 404 on bad ID."""
    res = requests.get(f"{api_url}/songs/nonexistent-id")
    assert res.status_code == 404

def test_concurrent_updates(api_url, test_song):
    """Simulate concurrent updates to the same song."""
    res = requests.post(f"{api_url}/songs", json=test_song)
    assert res.status_code == 201
    song_id = res.json()["song_id"]

    update_1 = {**test_song, "title": "Update One", "description": "First update"}
    update_2 = {**test_song, "title": "Update Two", "description": "Second update"}

    try:
        r1 = requests.put(f"{api_url}/songs/{song_id}", json=update_1)
        r2 = requests.put(f"{api_url}/songs/{song_id}", json=update_2)

        assert r1.status_code in [200, 409]
        assert r2.status_code in [200, 409]

        final = requests.get(f"{api_url}/songs/{song_id}").json()
        assert final["title"] in ["Update One", "Update Two"]
        assert final["description"] in ["First update", "Second update"]

    finally:
        requests.delete(f"{api_url}/songs/{song_id}")
