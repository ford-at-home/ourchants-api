"""
Tests for the presigned-url endpoint.

These tests verify that the presigned-url endpoint:
- Validates bucket and key names
- Handles missing or invalid parameters
- Generates valid pre-signed URLs
- Handles non-existent buckets and objects
"""

import json
import pytest
from moto import mock_aws
import boto3

def test_generate_presigned_url_success(client, mock_s3):
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

def test_generate_presigned_url_default_bucket(client, mock_s3):
    """Test using default bucket from environment."""
    # Create a test bucket and object
    s3 = boto3.client('s3')
    bucket_name = 'ourchants-songs'  # Should match S3_BUCKET env var
    key = 'test.mp3'
    s3.create_bucket(Bucket=bucket_name)
    s3.put_object(Bucket=bucket_name, Key=key, Body=b'test content')
    
    # Generate pre-signed URL without specifying bucket
    response = client('POST', '/presigned-url', {
        'key': key
    })
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'url' in body
    assert 'expiresIn' in body

def test_invalid_bucket_name(client):
    """Test validation of invalid bucket names."""
    test_cases = [
        ('', "Bucket name cannot be empty"),
        ('a', "Bucket name must be between 3 and 63 characters long"),
        ('a' * 64, "Bucket name must be between 3 and 63 characters long"),
        ('InvalidBucket', "Bucket name can only contain lowercase letters, numbers, dots, and hyphens, and must start and end with a letter or number"),
        ('invalid.bucket.name..', "Bucket name can only contain lowercase letters, numbers, dots, and hyphens, and must start and end with a letter or number"),
        ('192.168.1.1', "Bucket name cannot be formatted as an IP address")
    ]
    
    for bucket, expected_error in test_cases:
        response = client('POST', '/presigned-url', {
            'bucket': bucket,
            'key': 'test.mp3'
        })
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Invalid bucket name'
        assert body['code'] == 'INVALID_BUCKET_NAME'

def test_invalid_object_key(client):
    """Test validation of invalid object keys."""
    test_cases = [
        ('', "Object key cannot be empty"),
        ('a' * 1025, "Object key cannot exceed 1024 characters"),
        ('test\x00file.mp3', "Object key cannot contain control characters"),
        ('test//file.mp3', "Object key cannot contain consecutive slashes")
    ]
    
    for key, expected_error in test_cases:
        response = client('POST', '/presigned-url', {
            'bucket': 'test-bucket',
            'key': key
        })
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Object key cannot be empty'
        assert body['code'] == 'INVALID_OBJECT_KEY'

def test_nonexistent_bucket(client, mock_s3):
    """Test handling of non-existent bucket."""
    response = client('POST', '/presigned-url', {
        'bucket': 'nonexistent-bucket',
        'key': 'test.mp3'
    })
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['error'] == 'Bucket nonexistent-bucket not found'
    assert body['code'] == 'BUCKET_NOT_FOUND'
    assert 'bucket' in body['details']

def test_nonexistent_object(client, mock_s3):
    """Test handling of non-existent object."""
    # Create a test bucket
    s3 = boto3.client('s3')
    bucket_name = 'test-bucket'
    s3.create_bucket(Bucket=bucket_name)
    
    response = client('POST', '/presigned-url', {
        'bucket': bucket_name,
        'key': 'nonexistent.mp3'
    })
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['error'] == 'Object nonexistent.mp3 not found in bucket test-bucket'
    assert body['code'] == 'OBJECT_NOT_FOUND'
    assert 'bucket' in body['details']
    assert 'key' in body['details']

def test_invalid_json(client):
    """Test handling of invalid JSON in request body."""
    response = client('POST', '/presigned-url', 'invalid json')
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'Object key cannot be empty'
    assert body['code'] == 'INVALID_OBJECT_KEY'

def test_cors_headers(client, mock_s3):
    """Test that CORS headers are present in responses."""
    # Create a test bucket and object
    s3 = boto3.client('s3')
    bucket_name = 'test-bucket'
    key = 'test.mp3'
    s3.create_bucket(Bucket=bucket_name)
    s3.put_object(Bucket=bucket_name, Key=key, Body=b'test content')
    
    # Test successful response
    response = client('POST', '/presigned-url', {
        'bucket': bucket_name,
        'key': key
    })
    
    assert response['statusCode'] == 200
    headers = response['headers']
    assert headers['Access-Control-Allow-Origin'] == '*'
    assert headers['Access-Control-Allow-Methods'] == 'OPTIONS,POST'
    assert headers['Access-Control-Allow-Headers'] == 'Content-Type'
    
    # Test error response
    response = client('POST', '/presigned-url', {
        'bucket': 'invalid',
        'key': key
    })
    
    assert response['statusCode'] == 404
    headers = response['headers']
    assert headers['Access-Control-Allow-Origin'] == '*'
    assert headers['Access-Control-Allow-Methods'] == 'OPTIONS,POST'
    assert headers['Access-Control-Allow-Headers'] == 'Content-Type' 