"""
End-to-end tests for the deployed Songs API.

These tests verify that the API works in the actual AWS environment by:
1. Finding the deployed API URL from AWS API Gateway
2. Making real HTTP requests to the API
3. Testing the full lifecycle of songs in DynamoDB
"""

import os
import json
import boto3
import pytest
import requests
from uuid import uuid4
from time import sleep
from botocore.exceptions import ClientError

def get_api_url():
    """Get the API URL from AWS API Gateway."""
    api_gateway = boto3.client('apigateway')
    
    try:
        # Get all REST APIs
        apis = api_gateway.get_rest_apis()
        
        # Find our Songs API
        for api in apis['items']:
            if 'songs' in api['name'].lower():  # More flexible matching
                api_id = api['id']
                
                # Get the stages
                stages = api_gateway.get_stages(restApiId=api_id)
                if not stages['item']:
                    continue  # Skip if no stages
                    
                # Use the first stage (usually 'prod' or 'dev')
                stage_name = stages['item'][0]['stageName']
                
                # Construct the API URL
                region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
                return f'https://{api_id}.execute-api.{region}.amazonaws.com/{stage_name}'
        
        raise ValueError("Could not find Songs API in API Gateway")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnrecognizedClientException':
            raise Exception("AWS credentials not configured. Please run 'aws configure' or set AWS environment variables.") from e
        raise

@pytest.fixture(scope='module')
def api_url():
    """Fixture to get and cache the API URL."""
    return get_api_url()

@pytest.fixture
def test_song():
    """Create a test song fixture."""
    return {
        'title': f'Test Song {uuid4()}',
        'artist': 'E2E Test Artist',
        'lyrics': 'Test lyrics for end-to-end testing'
    }

def test_api_lifecycle(api_url, test_song):
    """Test the complete lifecycle of a song in the API."""
    
    # 1. Create a new song
    create_response = requests.post(
        f'{api_url}/songs',
        json=test_song
    )
    assert create_response.status_code == 201, f"Failed to create song. Response: {create_response.text}"
    song_data = create_response.json()
    song_id = song_data['song_id']
    assert song_data['title'] == test_song['title']
    assert song_data['artist'] == test_song['artist']
    
    # Give DynamoDB a moment to achieve consistency
    sleep(1)
    
    # 2. Get the song
    get_response = requests.get(f'{api_url}/songs/{song_id}')
    assert get_response.status_code == 200, f"Failed to get song. Response: {get_response.text}"
    assert get_response.json() == song_data
    
    # 3. List all songs
    list_response = requests.get(f'{api_url}/songs')
    assert list_response.status_code == 200, f"Failed to list songs. Response: {list_response.text}"
    songs = list_response.json()
    assert any(s['song_id'] == song_id for s in songs)
    
    # 4. Update the song
    updated_data = {
        'title': 'Updated E2E Test Song',
        'artist': 'Updated Test Artist',
        'lyrics': 'Updated test lyrics'
    }
    update_response = requests.put(
        f'{api_url}/songs/{song_id}',
        json=updated_data
    )
    assert update_response.status_code == 200, f"Failed to update song. Response: {update_response.text}"
    updated_song = update_response.json()
    assert updated_song['song_id'] == song_id
    assert updated_song['title'] == updated_data['title']
    
    # 5. Delete the song
    delete_response = requests.delete(f'{api_url}/songs/{song_id}')
    assert delete_response.status_code == 204, f"Failed to delete song. Response: {delete_response.text}"
    
    # Verify deletion
    get_response = requests.get(f'{api_url}/songs/{song_id}')
    assert get_response.status_code == 404

def test_error_cases(api_url):
    """Test error handling in the API."""
    
    # Test invalid song ID
    get_response = requests.get(f'{api_url}/songs/not-a-valid-id')
    assert get_response.status_code == 404

def test_concurrent_operations(api_url, test_song):
    """Test concurrent operations on the same song."""
    
    # Create a song
    create_response = requests.post(
        f'{api_url}/songs',
        json=test_song
    )
    assert create_response.status_code == 201, f"Failed to create song. Response: {create_response.text}"
    song_id = create_response.json()['song_id']
    
    try:
        # Try two updates in quick succession
        update1 = {'title': 'Update 1', 'artist': test_song['artist'], 'lyrics': test_song['lyrics']}
        update2 = {'title': 'Update 2', 'artist': test_song['artist'], 'lyrics': test_song['lyrics']}
        
        response1 = requests.put(f'{api_url}/songs/{song_id}', json=update1)
        response2 = requests.put(f'{api_url}/songs/{song_id}', json=update2)
        
        assert response1.status_code in [200, 409]  # Either success or conflict
        assert response2.status_code in [200, 409]  # Either success or conflict
        
        # Verify final state is consistent
        get_response = requests.get(f'{api_url}/songs/{song_id}')
        assert get_response.status_code == 200, f"Failed to get song. Response: {get_response.text}"
        final_state = get_response.json()
        assert final_state['title'] in ['Update 1', 'Update 2']
    
    finally:
        # Cleanup
        requests.delete(f'{api_url}/songs/{song_id}') 