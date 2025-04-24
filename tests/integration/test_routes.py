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
    """Fixture providing a list of test songs."""
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
            'lineage': []
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
            'lineage': []
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
            'lineage': []
        }
    ]

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
    
    assert isinstance(body, dict)
    assert 'items' in body
    assert 'total' in body
    assert 'has_more' in body
    assert len(body['items']) == 1
    assert body['total'] == 1
    assert body['has_more'] == False
    assert body['items'][0]['title'] == test_song['title']
    assert body['items'][0]['artist'] == test_song['artist']

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

def test_list_songs_pagination(client, mock_dynamodb, test_songs):
    """Test pagination of song listing."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)

    # Test first page
    response = client('GET', '/songs', query_params={'limit': '2', 'offset': '0'})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['items']) == 2
    assert body['total'] == 3
    assert body['has_more'] == True

    # Test second page
    response = client('GET', '/songs', query_params={'limit': '2', 'offset': '2'})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['items']) == 1
    assert body['total'] == 3
    assert body['has_more'] == False

def test_list_songs_artist_filter(client, mock_dynamodb, test_songs):
    """Test filtering songs by artist."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)

    # Test artist filter
    response = client('GET', '/songs', query_params={'artist': 'Artist A'})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['items']) == 2
    assert body['total'] == 2
    assert body['has_more'] == False
    assert all(song['artist'] == 'Artist A' for song in body['items'])

def test_list_songs_artist_filter_with_pagination(client, mock_dynamodb, test_songs):
    """Test filtering songs by artist with pagination."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)

    # Test artist filter with pagination
    response = client('GET', '/songs', query_params={'artist': 'Artist A', 'limit': '1', 'offset': '0'})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['items']) == 1
    assert body['total'] == 2
    assert body['has_more'] == True
    assert body['items'][0]['artist'] == 'Artist A'

def test_invalid_pagination_parameters(client, mock_dynamodb):
    """Test handling of invalid pagination parameters."""
    # Test negative limit
    response = client('GET', '/songs', query_params={'limit': '-1'})
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'Invalid limit parameter'
    assert body['code'] == 'INVALID_LIMIT'

    # Test negative offset
    response = client('GET', '/songs', query_params={'offset': '-1'})
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'Invalid offset parameter'
    assert body['code'] == 'INVALID_OFFSET'

    # Test limit too large
    response = client('GET', '/songs', query_params={'limit': '101'})
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'Invalid limit parameter'
    assert body['code'] == 'INVALID_LIMIT'

def test_empty_artist_filter(client, mock_dynamodb, test_songs):
    """Test filtering with empty artist parameter."""
    # Create multiple songs
    for song in test_songs:
        client('POST', '/songs', song)

    # Test empty artist filter
    response = client('GET', '/songs', query_params={'artist': ''})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['items']) == 3
    assert body['total'] == 3
    assert body['has_more'] == False 