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

def test_create_song(client, mock_dynamodb, test_song):
    """Test creating a new song."""
    response = client('POST', '/songs', test_song)
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'song_id' in body
    assert body['title'] == test_song['title']
    assert body['artist'] == test_song['artist']
    assert body['lyrics'] == test_song['lyrics']

def test_get_song(client, mock_dynamodb, test_song):
    """Test getting a specific song."""
    # First create a song
    create_response = client('POST', '/songs', test_song)
    song_id = json.loads(create_response['body'])['song_id']
    
    # Then get the song
    response = client('GET', f'/songs/{song_id}')
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['song_id'] == song_id
    assert body['title'] == test_song['title']
    assert body['artist'] == test_song['artist']
    assert body['lyrics'] == test_song['lyrics']

def test_list_songs(client, mock_dynamodb):
    """Test listing songs when no songs exist."""
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert isinstance(body, list)
    assert len(body) == 0

def test_update_song(client, mock_dynamodb, test_song):
    """Test updating a song."""
    # First create a song
    create_response = client('POST', '/songs', test_song)
    song_id = json.loads(create_response['body'])['song_id']
    
    # Update the song
    updated_data = {
        'title': 'Updated Song',
        'artist': 'Updated Artist',
        'lyrics': 'Updated lyrics'
    }
    response = client('PUT', f'/songs/{song_id}', updated_data)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['song_id'] == song_id
    assert body['title'] == updated_data['title']
    assert body['artist'] == updated_data['artist']
    assert body['lyrics'] == updated_data['lyrics']

def test_delete_song(client, mock_dynamodb, test_song):
    """Test deleting a song."""
    # First create a song
    create_response = client('POST', '/songs', test_song)
    song_id = json.loads(create_response['body'])['song_id']
    
    # Delete the song
    response = client('DELETE', f'/songs/{song_id}')
    assert response['statusCode'] == 204
    
    # Verify the song is deleted
    get_response = client('GET', f'/songs/{song_id}')
    assert get_response['statusCode'] == 404 