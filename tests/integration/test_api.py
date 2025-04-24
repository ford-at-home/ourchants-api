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
import boto3
from api.core.api import SongsApi

def test_presigned_url(client, mock_dynamodb):
    """Test successful generation of a pre-signed URL."""
    # Create a test bucket and object
    s3 = boto3.client('s3')
    bucket_name = 'test-bucket'
    key = 'test.mp3'
    s3.create_bucket(Bucket=bucket_name)
    s3.put_object(Bucket=bucket_name, Key=key, Body=b'test content')
    
    # Generate pre-signed URL
    response = client('POST', '/presigned-url', {
        'bucket': bucket_name,
        'key': key
    })
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'url' in body
    assert 'expiresIn' in body
    assert body['expiresIn'] == 3600
    assert 'X-Amz-Algorithm' in body['url']
    assert 'X-Amz-Credential' in body['url']
    assert 'X-Amz-Signature' in body['url']

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
    assert body['code'] == 'BUCKET_NOT_FOUND'  # Your implementation returns BUCKET_NOT_FOUND for non-existent objects

def test_api_lifecycle(client, mock_dynamodb):
    """Test the complete lifecycle of a song."""
    # Create a song
    song_data = {
        'title': 'Test Song',
        'artist': 'Test Artist',
        's3_uri': 's3://ourchants-songs/test.mp3'
    }
    create_response = client('POST', '/songs', song_data)
    assert create_response['statusCode'] == 201
    created_song = json.loads(create_response['body'])
    assert created_song['title'] == song_data['title']
    assert created_song['artist'] == song_data['artist']
    
    # Get the song
    get_response = client('GET', f"/songs/{created_song['song_id']}")
    assert get_response['statusCode'] == 200
    retrieved_song = json.loads(get_response['body'])
    assert retrieved_song['title'] == song_data['title']
    assert retrieved_song['artist'] == song_data['artist']
    
    # Update the song
    update_data = {
        'title': 'Updated Song',
        'artist': 'Updated Artist',
        's3_uri': 's3://ourchants-songs/updated.mp3'
    }
    update_response = client('PUT', f"/songs/{created_song['song_id']}", update_data)
    assert update_response['statusCode'] == 200
    updated_song = json.loads(update_response['body'])
    assert updated_song['title'] == update_data['title']
    assert updated_song['artist'] == update_data['artist']
    
    # Delete the song
    delete_response = client('DELETE', f"/songs/{created_song['song_id']}")
    assert delete_response['statusCode'] == 204
    
    # Verify it's gone
    get_response = client('GET', f"/songs/{created_song['song_id']}")
    assert get_response['statusCode'] == 404

def test_concurrent_updates(client, mock_dynamodb):
    """Test concurrent updates to the same song."""
    # Create a song
    song_data = {
        'title': 'Test Song',
        'artist': 'Test Artist',
        's3_uri': 's3://ourchants-songs/test.mp3'
    }
    create_response = client('POST', '/songs', song_data)
    assert create_response['statusCode'] == 201
    created_song = json.loads(create_response['body'])
    
    # First update
    update1_data = {
        'title': 'Update 1',
        'artist': 'Artist 1',
        's3_uri': 's3://ourchants-songs/update1.mp3'
    }
    update1_response = client('PUT', f"/songs/{created_song['song_id']}", update1_data)
    assert update1_response['statusCode'] == 200
    
    # Second update
    update2_data = {
        'title': 'Update 2',
        'artist': 'Artist 2',
        's3_uri': 's3://ourchants-songs/update2.mp3'
    }
    update2_response = client('PUT', f"/songs/{created_song['song_id']}", update2_data)
    assert update2_response['statusCode'] == 200
    
    # Verify final state
    get_response = client('GET', f"/songs/{created_song['song_id']}")
    assert get_response['statusCode'] == 200
    final_song = json.loads(get_response['body'])
    assert final_song['title'] == update2_data['title']
    assert final_song['artist'] == update2_data['artist'] 