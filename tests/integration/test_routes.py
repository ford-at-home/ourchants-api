"""
Integration tests for the API routes.

These tests verify that the API routes work correctly with the actual AWS services.
"""

import json
import pytest
from moto import mock_aws

def test_list_songs(client, mock_dynamodb, test_songs):
    """Test listing all songs."""
    # Create some test songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # List songs
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert len(body['items']) == len(test_songs)
    
    # Verify all songs are returned
    titles = {item['title'] for item in body['items']}
    expected_titles = {song['title'] for song in test_songs}
    assert titles == expected_titles

def test_create_song(client, mock_dynamodb, test_song):
    """Test creating a new song."""
    response = client('POST', '/songs', test_song)
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    assert 'song_id' in body
    assert body['title'] == test_song['title']
    assert body['artist'] == test_song['artist']

def test_create_song_missing_required(client, mock_dynamodb):
    """Test creating a song with missing required fields."""
    response = client('POST', '/songs', {})
    assert response['statusCode'] == 400
    
    body = json.loads(response['body'])
    assert 'error' in body

def test_get_song(client, mock_dynamodb, test_song):
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

def test_get_nonexistent_song(client, mock_dynamodb):
    """Test getting a song that doesn't exist."""
    response = client('GET', '/songs/nonexistent')
    assert response['statusCode'] == 404
    
    body = json.loads(response['body'])
    assert 'error' in body

def test_update_song(client, mock_dynamodb, test_song):
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

def test_update_nonexistent_song(client, mock_dynamodb, test_song):
    """Test updating a song that doesn't exist."""
    response = client('PUT', '/songs/nonexistent', test_song)
    assert response['statusCode'] == 404
    
    body = json.loads(response['body'])
    assert 'error' in body

def test_delete_song(client, mock_dynamodb, test_song):
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

def test_delete_nonexistent_song(client, mock_dynamodb):
    """Test deleting a song that doesn't exist."""
    response = client('DELETE', '/songs/nonexistent')
    assert response['statusCode'] == 404
    
    body = json.loads(response['body'])
    assert 'error' in body 