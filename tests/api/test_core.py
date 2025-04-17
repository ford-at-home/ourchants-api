"""
Tests for the core API functionality.

These tests verify the business logic works correctly,
independent of the API Gateway/Lambda implementation.
"""

import pytest
from uuid import uuid4
from marshmallow import ValidationError
from api.core.api import SongsApi

def test_list_songs(mock_dynamodb, test_song):
    """Test listing all songs."""
    api = SongsApi(mock_dynamodb)
    
    # Create a song first
    api.create_song(test_song)
    
    # List songs
    songs = api.list_songs()
    assert len(songs) == 1
    assert songs[0]['title'] == test_song['title']
    assert songs[0]['artist'] == test_song['artist']

def test_create_song(mock_dynamodb, test_song):
    """Test creating a new song."""
    api = SongsApi(mock_dynamodb)
    song = api.create_song(test_song)
    assert 'song_id' in song
    assert song['title'] == test_song['title']
    assert song['artist'] == test_song['artist']
    assert song['album'] == test_song['album']
    assert song['bpm'] == test_song['bpm']
    assert song['composer'] == test_song['composer']
    assert song['version'] == test_song['version']
    assert song['date'] == test_song['date']
    assert song['filename'] == test_song['filename']
    assert song['filepath'] == test_song['filepath']
    assert song['description'] == test_song['description']
    assert song['lineage'] == test_song['lineage']

def test_create_song_missing_required(mock_dynamodb):
    """Test creating a song with missing required fields."""
    api = SongsApi(mock_dynamodb)
    with pytest.raises(ValidationError):
        api.create_song({})

def test_create_song_with_invalid_data(mock_dynamodb):
    """Test creating a song with invalid data."""
    api = SongsApi(mock_dynamodb)
    
    # Test with unknown fields
    with pytest.raises(ValidationError):
        api.create_song({'invalid': 'data'})
    
    # Test with missing required fields
    with pytest.raises(ValidationError):
        api.create_song({'title': 'Missing Artist'})
    
    # Test with empty strings
    with pytest.raises(ValidationError):
        api.create_song({
            'title': '',
            'artist': '',
            'lyrics': ''
        })

def test_get_song(mock_dynamodb, test_song):
    """Test getting a specific song."""
    api = SongsApi(mock_dynamodb)

    # First create a song
    created = api.create_song(test_song)
    song_id = created['song_id']

    # Then get the song
    song = api.get_song(song_id)
    assert song['song_id'] == song_id
    assert song['title'] == test_song['title']
    assert song['artist'] == test_song['artist']
    assert song['album'] == test_song['album']
    assert song['bpm'] == test_song['bpm']
    assert song['composer'] == test_song['composer']
    assert song['version'] == test_song['version']
    assert song['date'] == test_song['date']
    assert song['filename'] == test_song['filename']
    assert song['filepath'] == test_song['filepath']
    assert song['description'] == test_song['description']
    assert song['lineage'] == test_song['lineage']

def test_get_nonexistent_song(mock_dynamodb):
    """Test getting a song that doesn't exist."""
    api = SongsApi(mock_dynamodb)
    assert api.get_song('nonexistent') is None

def test_update_song(mock_dynamodb, test_song):
    """Test updating a song."""
    api = SongsApi(mock_dynamodb)

    # First create a song
    created = api.create_song(test_song)
    song_id = created['song_id']

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
    song = api.update_song(song_id, updated_data)
    assert song['song_id'] == song_id
    assert song['title'] == updated_data['title']
    assert song['artist'] == updated_data['artist']
    assert song['album'] == updated_data['album']
    assert song['bpm'] == updated_data['bpm']
    assert song['composer'] == updated_data['composer']
    assert song['version'] == updated_data['version']
    assert song['date'] == updated_data['date']
    assert song['filename'] == updated_data['filename']
    assert song['filepath'] == updated_data['filepath']
    assert song['description'] == updated_data['description']
    assert song['lineage'] == updated_data['lineage']

def test_update_nonexistent_song(mock_dynamodb, test_song):
    """Test updating a song that doesn't exist."""
    api = SongsApi(mock_dynamodb)
    assert api.update_song('nonexistent', test_song) is None

def test_update_song_with_invalid_data(mock_dynamodb, test_song):
    """Test updating a song with invalid data."""
    api = SongsApi(mock_dynamodb)
    
    # First create a song
    created = api.create_song(test_song)
    song_id = created['song_id']
    
    # Test with unknown fields
    with pytest.raises(ValidationError):
        api.update_song(song_id, {'invalid': 'data'})
    
    # Test with missing required fields
    with pytest.raises(ValidationError):
        api.update_song(song_id, {'title': 'Missing Artist'})
    
    # Test with empty strings
    with pytest.raises(ValidationError):
        api.update_song(song_id, {
            'title': '',
            'artist': '',
            'lyrics': ''
        })

def test_delete_song(mock_dynamodb, test_song):
    """Test deleting a song."""
    api = SongsApi(mock_dynamodb)
    
    # First create a song
    created = api.create_song(test_song)
    song_id = created['song_id']
    
    # Delete the song
    api.delete_song(song_id)
    
    # Verify it's gone
    assert api.get_song(song_id) is None 