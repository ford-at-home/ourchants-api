"""
Tests for the Songs API routes.

These tests verify that all API endpoints work correctly:
- GET /songs - List all songs
- POST /songs - Create a new song
- GET /songs/{id} - Get a specific song
- PUT /songs/{id} - Update a song
- DELETE /songs/{id} - Delete a song
"""

import json
import pytest
from pprint import pprint

def test_create_song(client, mock_dynamodb, test_song):
    """Test creating a new song."""
    response = client('POST', '/songs', test_song)
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'song_id' in body
    assert body['title'] == test_song['title']
    assert body['artist'] == test_song['artist']
    assert body['album'] == test_song['album']
    assert body['bpm'] == test_song['bpm']
    assert body['composer'] == test_song['composer']
    assert body['version'] == test_song['version']
    assert body['date'] == test_song['date']
    assert body['filename'] == test_song['filename']
    assert body['filepath'] == test_song['filepath']
    assert body['description'] == test_song['description']
    assert body['lineage'] == test_song['lineage']

def test_get_song(client, mock_dynamodb, test_song):
    """Test getting a specific song."""
    # First create a song
    create_response = client('POST', '/songs', test_song)
    song_id = json.loads(create_response['body'])['song_id']
    
    # Then get the song
    response = client('GET', f'/songs/{song_id}')
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    
    print("\n=== Example of a single song from DynamoDB ===")
    pprint(body, indent=2, width=120)
    print("============================================\n")
    
    assert body['song_id'] == song_id
    assert body['title'] == test_song['title']
    assert body['artist'] == test_song['artist']
    assert body['album'] == test_song['album']
    assert body['bpm'] == test_song['bpm']
    assert body['composer'] == test_song['composer']
    assert body['version'] == test_song['version']
    assert body['date'] == test_song['date']
    assert body['filename'] == test_song['filename']
    assert body['filepath'] == test_song['filepath']
    assert body['description'] == test_song['description']
    assert body['lineage'] == test_song['lineage']

def test_list_songs(client, mock_dynamodb, test_song):
    """Test listing all songs."""
    # First create a song
    client('POST', '/songs', test_song)
    
    # Then list songs
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    
    print("\n=== Example of songs list from DynamoDB ===")
    pprint(body, indent=2, width=120)
    print("=========================================\n")
    
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]['title'] == test_song['title']
    assert body[0]['artist'] == test_song['artist']

def test_get_nonexistent_song(client, mock_dynamodb):
    """Test getting a song that doesn't exist."""
    response = client('GET', '/songs/nonexistent')
    assert response['statusCode'] == 404

def test_update_song(client, mock_dynamodb, test_song):
    """Test updating a song."""
    # First create a song
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
    
    print("\n=== Example of updated song from DynamoDB ===")
    pprint(body, indent=2, width=120)
    print("==========================================\n")
    
    assert body['song_id'] == song_id
    assert body['title'] == updated_data['title']
    assert body['artist'] == updated_data['artist']
    assert body['album'] == updated_data['album']
    assert body['bpm'] == updated_data['bpm']
    assert body['composer'] == updated_data['composer']
    assert body['version'] == updated_data['version']
    assert body['date'] == updated_data['date']
    assert body['filename'] == updated_data['filename']
    assert body['filepath'] == updated_data['filepath']
    assert body['description'] == updated_data['description']
    assert body['lineage'] == updated_data['lineage']

def test_delete_song(client, mock_dynamodb, test_song):
    """Test deleting a song."""
    # First create a song
    create_response = client('POST', '/songs', test_song)
    song_id = json.loads(create_response['body'])['song_id']
    
    # Delete the song
    response = client('DELETE', f'/songs/{song_id}')
    assert response['statusCode'] == 204
    
    # Verify it's gone
    get_response = client('GET', f'/songs/{song_id}')
    assert get_response['statusCode'] == 404 