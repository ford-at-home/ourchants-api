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

@pytest.fixture(scope="module")
def api_url():
    """Fixture to resolve and cache the Songs API URL."""
    return get_api_url()

@pytest.fixture
def test_song():
    """Create a test song payload."""
    return {
        "title": f"Test Song {uuid4()}",
        "artist": "E2E Test Artist",
        "album": "Test Album",
        "bpm": "120",
        "composer": "Test Composer",
        "version": "1.0",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": "test_song.mp3",
        "filepath": "Media/test_song.mp3",
        "description": "A test song for end-to-end testing",
        "lineage": ["original"]
    }

def get_lambda_logs(function_name, start_time=None, end_time=None):
    """Fetch logs from CloudWatch for the Lambda function."""
    if start_time is None:
        start_time = datetime.utcnow() - timedelta(minutes=5)
    if end_time is None:
        end_time = datetime.utcnow()
    
    # Add a 10-second delay to ensure logs are available
    print("\nWaiting 10 seconds for logs to be available...")
    sleep(10)
    
    logs_client = boto3.client('logs')
    
    # Get log groups
    log_groups = logs_client.describe_log_groups(
        logGroupNamePrefix=f'/aws/lambda/{function_name}'
    )
    
    if not log_groups['logGroups']:
        return "No log groups found"
    
    log_group = log_groups['logGroups'][0]['logGroupName']
    
    # Get log streams
    log_streams = logs_client.describe_log_streams(
        logGroupName=log_group,
        orderBy='LastEventTime',
        descending=True,
        limit=5
    )
    
    if not log_streams['logStreams']:
        return "No log streams found"
    
    # Get events from the most recent log stream
    log_stream = log_streams['logStreams'][0]['logStreamName']
    events = logs_client.get_log_events(
        logGroupName=log_group,
        logStreamName=log_stream,
        startTime=int(start_time.timestamp() * 1000),
        endTime=int(end_time.timestamp() * 1000),
        limit=100
    )
    
    return "\n".join([event['message'] for event in events['events']])

def test_api_lifecycle(api_url, test_song):
    """Test full lifecycle: create → get → list → update → delete."""
    try:
        # Create
        res = requests.post(f"{api_url}/songs", json=test_song)
        assert res.status_code == 201, f"Create failed: {res.text}"
        created = res.json()
        song_id = created["song_id"]

        # Verify create
        for k in test_song:
            assert created[k] == test_song[k]
        assert "song_id" in created

        sleep(1)  # Allow for eventual consistency

        # Get
        res = requests.get(f"{api_url}/songs/{song_id}")
        assert res.status_code == 200
        assert res.json() == created

        # List
        res = requests.get(f"{api_url}/songs")
        assert res.status_code == 200
        all_songs = res.json()
        assert any(s["song_id"] == song_id for s in all_songs)

        # Update
        updated = {**test_song, "title": "Updated Song", "bpm": "140", "version": "2.0"}
        res = requests.put(f"{api_url}/songs/{song_id}", json=updated)
        assert res.status_code == 200
        updated_response = res.json()
        for k in updated:
            assert updated_response[k] == updated[k]
        assert updated_response["song_id"] == song_id

        # Delete
        res = requests.delete(f"{api_url}/songs/{song_id}")
        assert res.status_code == 204

        # Confirm deletion
        res = requests.get(f"{api_url}/songs/{song_id}")
        assert res.status_code == 404

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
