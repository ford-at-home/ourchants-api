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
from api.core.api import SongsApi

@pytest.fixture
def test_songs():
    """Create test song data."""
    return [
        {
            'title': 'Song 1',
            'artist': 'Artist A',
            'album': 'Album 1',
            'bpm': '120',
            'composer': 'Composer 1',
            'version': '1.0',
            'date': '2024-03-20 12:00:00',
            'filename': 'song1.mp3',
            'filepath': 'Media/song1.mp3',
            'description': 'Test song 1',
            'lineage': [],
            's3_uri': 's3://ourchants-songs/song1.mp3'
        },
        {
            'title': 'Song 2',
            'artist': 'Artist A',
            'album': 'Album 1',
            'bpm': '130',
            'composer': 'Composer 1',
            'version': '1.0',
            'date': '2024-03-20 12:00:00',
            'filename': 'song2.mp3',
            'filepath': 'Media/song2.mp3',
            'description': 'Test song 2',
            'lineage': [],
            's3_uri': 's3://ourchants-songs/song2.mp3'
        },
        {
            'title': 'Song 3',
            'artist': 'Artist B',
            'album': 'Album 2',
            'bpm': '140',
            'composer': 'Composer 2',
            'version': '1.0',
            'date': '2024-03-20 12:00:00',
            'filename': 'song3.mp3',
            'filepath': 'Media/song3.mp3',
            'description': 'Test song 3',
            'lineage': [],
            's3_uri': 's3://ourchants-songs/song3.mp3'
        }
    ]

def test_create_song(client, mock_dynamodb, test_songs):
    """Test creating a new song."""
    song = test_songs[0]
    response = client('POST', '/songs', song)
    assert response['statusCode'] == 201
    result = json.loads(response['body'])
    assert result['title'] == song['title']
    assert result['artist'] == song['artist']
    assert 'song_id' in result

def test_get_song(client, mock_dynamodb, test_songs):
    """Test retrieving a song."""
    # Create a song first
    song = test_songs[0]
    create_response = client('POST', '/songs', song)
    created_song = json.loads(create_response['body'])
    
    # Get the song
    response = client('GET', f"/songs/{created_song['song_id']}")
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert result['title'] == song['title']
    assert result['artist'] == song['artist']

def test_list_songs(client, mock_dynamodb, test_songs):
    """Test listing all songs."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # List songs
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 3
    assert result['total'] == 3
    assert not result['has_more']

def test_get_nonexistent_song(client, mock_dynamodb):
    """Test retrieving a non-existent song."""
    response = client('GET', '/songs/nonexistent')
    assert response['statusCode'] == 404

def test_update_song(client, mock_dynamodb, test_songs):
    """Test updating a song."""
    # Create a song first
    song = test_songs[0]
    create_response = client('POST', '/songs', song)
    created_song = json.loads(create_response['body'])
    
    # Update the song
    update_data = {
        'title': 'Updated Title',
        'artist': 'Updated Artist',
        's3_uri': 's3://ourchants-songs/updated.mp3'
    }
    response = client('PUT', f"/songs/{created_song['song_id']}", update_data)
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert result['title'] == update_data['title']
    assert result['artist'] == update_data['artist']

def test_delete_song(client, mock_dynamodb, test_songs):
    """Test deleting a song."""
    # Create a song first
    song = test_songs[0]
    create_response = client('POST', '/songs', song)
    created_song = json.loads(create_response['body'])
    
    # Delete the song
    response = client('DELETE', f"/songs/{created_song['song_id']}")
    assert response['statusCode'] == 204
    
    # Verify it's gone
    get_response = client('GET', f"/songs/{created_song['song_id']}")
    assert get_response['statusCode'] == 404

def test_list_songs_pagination(client, mock_dynamodb, test_songs):
    """Test pagination of song list."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # Test first page
    response = client('GET', '/songs', query_params={'limit': '2', 'offset': '0'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 2
    assert result['total'] == 3
    assert result['has_more']
    
    # Test second page
    response = client('GET', '/songs', query_params={'limit': '2', 'offset': '2'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 1
    assert result['total'] == 3
    assert not result['has_more']

def test_list_songs_artist_filter(client, mock_dynamodb, test_songs):
    """Test filtering songs by artist."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # Test artist filter
    response = client('GET', '/songs', query_params={'artist_filter': 'Artist A'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 2
    assert result['total'] == 2
    assert all(song['artist'] == 'Artist A' for song in result['items'])

def test_list_songs_artist_filter_with_pagination(client, mock_dynamodb, test_songs):
    """Test filtering songs by artist with pagination."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # Test artist filter with pagination
    response = client('GET', '/songs', query_params={'artist_filter': 'Artist A', 'limit': '1', 'offset': '0'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 1
    assert result['total'] == 2
    assert result['has_more']
    assert result['items'][0]['artist'] == 'Artist A'

def test_invalid_pagination_parameters(client, mock_dynamodb):
    """Test invalid pagination parameters."""
    # Test invalid limit
    response = client('GET', '/songs', query_params={'limit': '0'})
    assert response['statusCode'] == 400
    result = json.loads(response['body'])
    assert result['error'] == 'Invalid limit parameter'
    assert result['code'] == 'INVALID_LIMIT'
    
    # Test invalid offset
    response = client('GET', '/songs', query_params={'offset': '-1'})
    assert response['statusCode'] == 400
    result = json.loads(response['body'])
    assert result['error'] == 'Invalid offset parameter'
    assert result['code'] == 'INVALID_OFFSET'

def test_empty_artist_filter(client, mock_dynamodb, test_songs):
    """Test filtering with empty artist parameter."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # Test empty artist filter
    response = client('GET', '/songs', query_params={'artist_filter': ''})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 3
    assert result['total'] == 3
    assert not result['has_more'] 