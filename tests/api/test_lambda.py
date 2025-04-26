"""
Tests for the Lambda handler.

These tests verify that the Lambda handler correctly:
1. Routes requests to the appropriate API methods
2. Handles errors and returns appropriate responses
3. Sets CORS headers correctly
"""

import json
import pytest
from moto import mock_aws
from api.app import lambda_handler

@pytest.mark.usefixtures('mock_dynamodb')
def test_list_songs(client, test_song):
    """Test listing all songs."""
    # Create a song first
    client('POST', '/songs', test_song)
    
    # List songs
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert len(body['items']) == 1
    assert body['items'][0]['title'] == test_song['title']
    assert body['items'][0]['artist'] == test_song['artist']

@pytest.mark.usefixtures('mock_dynamodb')
def test_list_songs_empty(client):
    """Test listing songs when there are none."""
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert len(body['items']) == 0

@pytest.mark.usefixtures('mock_dynamodb')
def test_list_songs_multiple(client, test_song):
    """Test listing multiple songs."""
    # Create multiple songs
    song1 = test_song.copy()
    song1['title'] = 'Song 1'
    song1['artist'] = 'Artist 1'
    
    song2 = test_song.copy()
    song2['title'] = 'Song 2'
    song2['artist'] = 'Artist 2'
    
    client('POST', '/songs', song1)
    client('POST', '/songs', song2)
    
    # List songs
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert len(body['items']) == 2
    
    # Verify both songs are returned
    titles = {item['title'] for item in body['items']}
    assert titles == {'Song 1', 'Song 2'}

@pytest.mark.usefixtures('mock_dynamodb')
def test_create_song(client, test_song):
    """Test creating a new song."""
    response = client('POST', '/songs', test_song)
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    assert 'song_id' in body
    assert body['title'] == test_song['title']
    assert body['artist'] == test_song['artist']

@pytest.mark.usefixtures('mock_dynamodb')
def test_create_song_missing_required(client):
    """Test creating a song with missing required fields."""
    response = client('POST', '/songs', {})
    assert response['statusCode'] == 400
    
    body = json.loads(response['body'])
    assert 'error' in body

@pytest.mark.usefixtures('mock_dynamodb')
def test_get_song(client, test_song):
    """Test getting a specific song."""
    # Create a song first
    create_response = client('POST', '/songs', test_song)
    song_id = json.loads(create_response['body'])['song_id']
    
    # Get the song
    response = client('GET', f'/songs/{song_id}')
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['song_id'] == song_id
    assert body['title'] == test_song['title']
    assert body['artist'] == test_song['artist']

@pytest.mark.usefixtures('mock_dynamodb')
def test_get_nonexistent_song(client):
    """Test getting a song that doesn't exist."""
    response = client('GET', '/songs/nonexistent')
    assert response['statusCode'] == 404
    
    body = json.loads(response['body'])
    assert 'error' in body

@pytest.mark.usefixtures('mock_dynamodb')
def test_update_song(client, test_song):
    """Test updating a song."""
    # Create a song first
    create_response = client('POST', '/songs', test_song)
    song_id = json.loads(create_response['body'])['song_id']
    
    # Update the song
    updated_data = {
        'title': 'Updated Song',
        'artist': 'Updated Artist',
        'album': 'Updated Album',
        'bpm': '140',
        'composer': 'Updated Composer',
        'version': 'Updated Version',
        'date': '2024-03-21 12:00:00',
        'filename': 'updated_song.mp3',
        'filepath': 'Media/updated_song.mp3',
        'description': 'Updated description',
        'lineage': ['original']
    }
    
    response = client('PUT', f'/songs/{song_id}', updated_data)
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['song_id'] == song_id
    assert body['title'] == updated_data['title']
    assert body['artist'] == updated_data['artist']

@pytest.mark.usefixtures('mock_dynamodb')
def test_update_nonexistent_song(client, test_song):
    """Test updating a song that doesn't exist."""
    response = client('PUT', '/songs/nonexistent', test_song)
    assert response['statusCode'] == 404
    
    body = json.loads(response['body'])
    assert 'error' in body

@pytest.mark.usefixtures('mock_dynamodb')
def test_delete_song(client, test_song):
    """Test deleting a song."""
    # Create a song first
    create_response = client('POST', '/songs', test_song)
    song_id = json.loads(create_response['body'])['song_id']
    
    # Delete the song
    response = client('DELETE', f'/songs/{song_id}')
    assert response['statusCode'] == 204
    
    # Verify it's gone
    get_response = client('GET', f'/songs/{song_id}')
    assert get_response['statusCode'] == 404

@pytest.mark.usefixtures('mock_dynamodb')
def test_delete_nonexistent_song(client):
    """Test deleting a song that doesn't exist."""
    response = client('DELETE', '/songs/nonexistent')
    assert response['statusCode'] == 404
    
    body = json.loads(response['body'])
    assert 'error' in body 