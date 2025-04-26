import json
import pytest
from api.app import lambda_handler

@pytest.fixture
def test_songs():
    return [
        {
            'title': 'Song 1',
            'artist': 'John Smith',
            's3_uri': 's3://ourchants-songs/song1.mp3'
        },
        {
            'title': 'Song 2',
            'artist': 'Johnny Smith',
            's3_uri': 's3://ourchants-songs/song2.mp3'
        },
        {
            'title': 'Song 3',
            'artist': 'Jane Smith',
            's3_uri': 's3://ourchants-songs/song3.mp3'
        },
        {
            'title': 'Song 4',
            'artist': 'John Doe',
            's3_uri': 's3://ourchants-songs/song4.mp3'
        }
    ]

def test_exact_artist_match(client, mock_dynamodb, test_songs):
    """Test that exact artist name matches work."""
    # Create test songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # Test exact match
    response = client('GET', '/songs', query_params={'artist_filter': 'John Smith'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 1
    assert result['items'][0]['artist'] == 'John Smith'

def test_partial_artist_match(client, mock_dynamodb, test_songs):
    """Test that partial artist name matches work."""
    # Create test songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # Test partial match with 'John'
    response = client('GET', '/songs', query_params={'artist_filter': 'John'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    # Should match all artists containing 'John'
    assert len(result['items']) == 3
    assert all('John' in song['artist'] for song in result['items'])

def test_case_insensitive_artist_match(client, mock_dynamodb, test_songs):
    """Test that artist name matching is case insensitive."""
    # Create test songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # Test case insensitive match
    response = client('GET', '/songs', query_params={'artist_filter': 'john smith'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    # Should match 'John Smith' due to case insensitivity
    assert len(result['items']) == 1
    assert result['items'][0]['artist'] == 'John Smith'

def test_empty_artist_filter(client, mock_dynamodb, test_songs):
    """Test that empty artist filter returns all songs."""
    # Create test songs
    for song in test_songs:
        client('POST', '/songs', song)
    
    # Test empty filter
    response = client('GET', '/songs', query_params={'artist_filter': ''})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 4
    assert result['total'] == 4 