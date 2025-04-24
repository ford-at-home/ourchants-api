import pytest
import json
from api.core.api import SongsApi

def test_list_songs_pagination(client, mock_dynamodb):
    # Create test data
    test_songs = [
        {'song_id': '1', 'title': 'Song 1', 'artist': 'Artist A'},
        {'song_id': '2', 'title': 'Song 2', 'artist': 'Artist A'},
        {'song_id': '3', 'title': 'Song 3', 'artist': 'Artist B'},
        {'song_id': '4', 'title': 'Song 4', 'artist': 'Artist B'},
        {'song_id': '5', 'title': 'Song 5', 'artist': 'Artist C'}
    ]
    
    # Create songs using the client
    for song in test_songs:
        response = client('POST', '/songs', song)
        assert response['statusCode'] == 201
    
    # Test basic pagination
    response = client('GET', '/songs', query_params={'limit': '2', 'offset': '0'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 2
    assert result['total'] == 5
    assert result['has_more'] == True
    
    # Test offset
    response = client('GET', '/songs', query_params={'limit': '2', 'offset': '2'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 2
    assert result['total'] == 5
    assert result['has_more'] == True
    
    # Test last page
    response = client('GET', '/songs', query_params={'limit': '2', 'offset': '4'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 1
    assert result['total'] == 5
    assert result['has_more'] == False

def test_list_songs_artist_filter(client, mock_dynamodb):
    # Create test data
    test_songs = [
        {'song_id': '1', 'title': 'Song 1', 'artist': 'Artist A'},
        {'song_id': '2', 'title': 'Song 2', 'artist': 'Artist A'},
        {'song_id': '3', 'title': 'Song 3', 'artist': 'Artist B'},
        {'song_id': '4', 'title': 'Song 4', 'artist': 'Artist B'},
        {'song_id': '5', 'title': 'Song 5', 'artist': 'Artist C'}
    ]
    
    # Create songs using the client
    for song in test_songs:
        response = client('POST', '/songs', song)
        assert response['statusCode'] == 201
    
    # Test artist filter
    response = client('GET', '/songs', query_params={'artist_filter': 'Artist A'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 2
    assert result['total'] == 2
    assert all(song['artist'] == 'Artist A' for song in result['items'])
    
    # Test artist filter with pagination
    response = client('GET', '/songs', query_params={'artist_filter': 'Artist B', 'limit': '1', 'offset': '0'})
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 1
    assert result['total'] == 2
    assert result['has_more'] == True
    assert result['items'][0]['artist'] == 'Artist B'

def test_list_songs_invalid_pagination(client, mock_dynamodb):
    # Test invalid limit
    response = client('GET', '/songs', query_params={'limit': '0'})
    assert response['statusCode'] == 400
    result = json.loads(response['body'])
    assert result['error'] == 'Invalid limit parameter'
    assert result['details'] == 'limit must be between 1 and 100'
    assert result['code'] == 'INVALID_LIMIT'
    
    # Test invalid offset
    response = client('GET', '/songs', query_params={'offset': '-1'})
    assert response['statusCode'] == 400
    result = json.loads(response['body'])
    assert result['error'] == 'Invalid offset parameter'
    assert result['details'] == 'offset must be non-negative'
    assert result['code'] == 'INVALID_OFFSET'

def test_list_songs_empty_database(client, mock_dynamodb):
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    result = json.loads(response['body'])
    assert len(result['items']) == 0
    assert result['total'] == 0
    assert result['has_more'] == False 