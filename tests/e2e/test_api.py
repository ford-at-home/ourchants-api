"""
End-to-end tests for the deployed Songs API.

Only run after API has been successfully deployed.

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
from pprint import pprint
from botocore.exceptions import ClientError
from datetime import datetime

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
    """Create a test song fixture with all fields."""
    return {
        'title': f'Test Song {uuid4()}',
        'artist': 'E2E Test Artist',
        'album': 'Test Album',
        'bpm': '120',
        'composer': 'Test Composer',
        'version': '1.0',
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'filename': 'test_song.mp3',
        'filepath': 'Media/test_song.mp3',
        'description': 'A test song for end-to-end testing',
        'lineage': ['original']
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
    
    print("\n=== Created Song ===")
    pprint(song_data, indent=2, width=120)
    print("==================\n")
    
    # Verify all fields
    for field in test_song:
        assert song_data[field] == test_song[field], f"Field {field} does not match"
    assert 'song_id' in song_data
    
    # Give DynamoDB a moment to achieve consistency
    sleep(1)
    
    # 2. Get the song
    get_response = requests.get(f'{api_url}/songs/{song_id}')
    assert get_response.status_code == 200, f"Failed to get song. Response: {get_response.text}"
    retrieved_song = get_response.json()
    
    print("\n=== Retrieved Song ===")
    pprint(retrieved_song, indent=2, width=120)
    print("=====================\n")
    
    assert retrieved_song == song_data
    
    # 3. List all songs
    list_response = requests.get(f'{api_url}/songs')
    assert list_response.status_code == 200, f"Failed to list songs. Response: {list_response.text}"
    songs = list_response.json()
    
    print("\n=== All Songs ===")
    pprint(songs, indent=2, width=120)
    print("================\n")
    
    assert any(s['song_id'] == song_id for s in songs)
    
    # 4. Update the song with all fields
    updated_data = {
        'title': 'Updated E2E Test Song',
        'artist': 'Updated Test Artist',
        'album': 'Updated Test Album',
        'bpm': '140',
        'composer': 'Updated Test Composer',
        'version': '2.0',
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'filename': 'updated_test_song.mp3',
        'filepath': 'Media/updated_test_song.mp3',
        'description': 'An updated test song for end-to-end testing',
        'lineage': ['original', 'updated']
    }
    update_response = requests.put(
        f'{api_url}/songs/{song_id}',
        json=updated_data
    )
    assert update_response.status_code == 200, f"Failed to update song. Response: {update_response.text}"
    updated_song = update_response.json()
    
    print("\n=== Updated Song ===")
    pprint(updated_song, indent=2, width=120)
    print("===================\n")
    
    # Verify all updated fields
    for field in updated_data:
        assert updated_song[field] == updated_data[field], f"Updated field {field} does not match"
    assert updated_song['song_id'] == song_id
    
    # 5. Delete the song
    delete_response = requests.delete(f'{api_url}/songs/{song_id}')
    assert delete_response.status_code == 204, f"Failed to delete song. Response: {delete_response.text}"
    
    print("\n=== Song Deleted Successfully ===")
    print("==============================\n")
    
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
        update1 = {
            'title': 'Update 1',
            'artist': test_song['artist'],
            'album': test_song['album'],
            'description': 'First concurrent update'
        }
        update2 = {
            'title': 'Update 2',
            'artist': test_song['artist'],
            'album': test_song['album'],
            'description': 'Second concurrent update'
        }
        
        response1 = requests.put(f'{api_url}/songs/{song_id}', json=update1)
        response2 = requests.put(f'{api_url}/songs/{song_id}', json=update2)
        
        assert response1.status_code in [200, 409]  # Either success or conflict
        assert response2.status_code in [200, 409]  # Either success or conflict
        
        # Verify final state is consistent
        get_response = requests.get(f'{api_url}/songs/{song_id}')
        assert get_response.status_code == 200, f"Failed to get song. Response: {get_response.text}"
        final_state = get_response.json()
        
        print("\n=== Final State After Concurrent Updates ===")
        pprint(final_state, indent=2, width=120)
        print("=======================================\n")
        
        assert final_state['title'] in ['Update 1', 'Update 2']
        assert final_state['description'] in ['First concurrent update', 'Second concurrent update']
    
    finally:
        # Cleanup
        requests.delete(f'{api_url}/songs/{song_id}') 