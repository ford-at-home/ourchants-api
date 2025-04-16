"""
Tests for the core API functionality.

These tests verify the business logic works correctly,
independent of the API Gateway/Lambda implementation.
"""

import pytest
from uuid import uuid4
from marshmallow import ValidationError
from api.core.api import SongsApi

def test_list_songs(mock_dynamodb):
    """Test listing songs when no songs exist."""
    api = SongsApi(mock_dynamodb)
    songs = api.list_songs()
    assert isinstance(songs, list)
    assert len(songs) == 0

def test_create_song(mock_dynamodb, test_song):
    """Test creating a new song."""
    api = SongsApi(mock_dynamodb)
    song = api.create_song(test_song)
    assert 'song_id' in song
    assert song['title'] == test_song['title']
    assert song['artist'] == test_song['artist']
    assert song['lyrics'] == test_song['lyrics']

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
    assert song['lyrics'] == test_song['lyrics']

def test_get_nonexistent_song(mock_dynamodb):
    """Test getting a song that doesn't exist."""
    api = SongsApi(mock_dynamodb)
    song = api.get_song('nonexistent')
    assert song is None

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
        'lyrics': 'Updated lyrics'
    }
    song = api.update_song(song_id, updated_data)
    assert song['song_id'] == song_id
    assert song['title'] == updated_data['title']
    assert song['artist'] == updated_data['artist']
    assert song['lyrics'] == updated_data['lyrics']

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
    
    # Verify the song is deleted
    song = api.get_song(song_id)
    assert song is None 