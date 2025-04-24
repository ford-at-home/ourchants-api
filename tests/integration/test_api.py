"""
Integration tests for the Songs API.

These tests verify that all API endpoints work correctly:
- GET /songs - List all songs with pagination and filtering
- POST /songs - Create a new song
- GET /songs/{id} - Get a specific song
- PUT /songs/{id} - Update a song
- DELETE /songs/{id} - Delete a song
- POST /presigned-url - Get a pre-signed URL for S3 access
"""

import json
import pytest
from pprint import pprint
from uuid import uuid4
from datetime import datetime

def test_presigned_url(client, mock_dynamodb, mock_s3):
    """Test the pre-signed URL endpoint."""
    # Create a test file in S3
    bucket = 'ourchants-songs'
    key = f'test-{uuid4()}.mp3'
    
    try:
        # Upload a test file
        mock_s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=b'test content'
        )
        
        # Request pre-signed URL
        response = client('POST', '/presigned-url', {
            'bucket': bucket,
            'key': key
        })
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'url' in body
        assert 'expiresIn' in body
        assert body['expiresIn'] == 3600
        
    finally:
        # Clean up
        try:
            mock_s3.delete_object(Bucket=bucket, Key=key)
        except Exception as e:
            print(f"Error cleaning up test file: {e}")

def test_presigned_url_errors(client, mock_dynamodb):
    """Test error cases for the pre-signed URL endpoint."""
    # Test missing key
    response = client('POST', '/presigned-url', {})
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'code' in body
    assert body['code'] == 'INVALID_OBJECT_KEY'
    
    # Test non-existent bucket
    response = client('POST', '/presigned-url', {
        'bucket': 'non-existent-bucket',
        'key': 'test.mp3'
    })
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'code' in body
    assert body['code'] == 'BUCKET_NOT_FOUND'
    
    # Test non-existent object
    response = client('POST', '/presigned-url', {
        'bucket': 'ourchants-songs',
        'key': 'non-existent-object.mp3'
    })
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'code' in body
    assert body['code'] == 'OBJECT_NOT_FOUND'

def test_api_lifecycle(client, mock_dynamodb, test_song):
    """Test full lifecycle: create → get → list → update → delete."""
    # Ensure s3_uri is included in test_song
    test_song['s3_uri'] = 's3://ourchants-songs/test-song.mp3'
    
    # Create song
    response = client('POST', '/songs', test_song)
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'song_id' in body
    assert 's3_uri' in body
    assert body['s3_uri'] is not None
    song_id = body['song_id']
    
    # Get song
    response = client('GET', f'/songs/{song_id}')
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['song_id'] == song_id
    assert 's3_uri' in body
    assert body['s3_uri'] is not None
    
    # List songs
    response = client('GET', '/songs')
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert isinstance(body, dict)
    assert 'items' in body
    assert any(s['song_id'] == song_id for s in body['items'])
    assert all('s3_uri' in s and s['s3_uri'] is not None for s in body['items'])
    
    # Update song
    updated_data = {**test_song, 'title': 'Updated Title'}
    response = client('PUT', f'/songs/{song_id}', updated_data)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['title'] == 'Updated Title'
    assert 's3_uri' in body
    assert body['s3_uri'] is not None
    
    # Delete song
    response = client('DELETE', f'/songs/{song_id}')
    assert response['statusCode'] == 204
    
    # Verify deletion
    response = client('GET', f'/songs/{song_id}')
    assert response['statusCode'] == 404

def test_concurrent_updates(client, mock_dynamodb, test_song):
    """Simulate concurrent updates to the same song."""
    # Create initial song
    response = client('POST', '/songs', test_song)
    assert response['statusCode'] == 201
    song_id = json.loads(response['body'])['song_id']

    update_1 = {**test_song, 'title': 'Update One', 'description': 'First update'}
    update_2 = {**test_song, 'title': 'Update Two', 'description': 'Second update'}

    try:
        r1 = client('PUT', f'/songs/{song_id}', update_1)
        r2 = client('PUT', f'/songs/{song_id}', update_2)

        assert r1['statusCode'] in [200, 409]
        assert r2['statusCode'] in [200, 409]

        final = json.loads(client('GET', f'/songs/{song_id}')['body'])
        assert final['title'] in ['Update One', 'Update Two']
        assert final['description'] in ['First update', 'Second update']

    finally:
        client('DELETE', f'/songs/{song_id}') 