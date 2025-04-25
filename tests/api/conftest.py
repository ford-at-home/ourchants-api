"""
Pytest configuration and fixtures for unit tests.

This module sets up the test environment with:
- Basic test fixtures for unit testing
- No AWS service mocking (that's for integration tests)

The key difference between this and integration tests is that:
- Unit tests use simple in-memory mocks
- No actual AWS services are involved
- Tests are faster and more isolated
- Focus on testing individual functions

Important Notes:
1. DynamoDB SDK Representation:
   - The AWS SDK wraps all values in type descriptors (S, N, L, M, etc.)
   - This is normal and should not be "fixed" or simplified
   - The M->S->S pattern in responses is just the SDK's way of representing data
"""

import pytest
import json
import sys
import os
import boto3
from moto import mock_aws

# Add the api directory to the Python path so we can import our app code
# This is necessary because the tests are in a different directory than the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

@pytest.fixture
def test_song():
    """
    Create a test song object.
    
    This fixture provides a standard test song that can be used across multiple tests.
    It includes all the fields that a real song would have in our database.
    
    Returns:
        dict: A dictionary representing a song with all required fields
    """
    return {
        'song_id': 'test-song-id',  # Fixed ID for predictable testing
        'title': 'Test Song',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'bpm': '120',
        'composer': 'Test Composer',
        'version': 'Test Version',
        'date': '2024-03-20 12:00:00',
        'filename': 'test_song.mp3',
        'filepath': 'Media/test_song.mp3',
        'description': 'Test description',
        'lineage': [],  # Empty list for new songs
        's3_uri': 's3://ourchants-songs/test_song.mp3'  # S3 location of the song file
    }

@pytest.fixture
def client():
    """
    Create a test client for making API calls.
    
    This fixture provides a simple function that simulates API Gateway calls
    by directly invoking the lambda_handler function.
    
    Returns:
        function: A function that takes method, path, and body parameters
    """
    from api.app import lambda_handler
    
    def invoke(method, path, body=None):
        """
        Simulate an API Gateway call.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            path (str): API path
            body (dict, optional): Request body
            
        Returns:
            dict: Response from the lambda_handler
        """
        event = {
            'requestContext': {
                'http': {
                    'method': method,
                    'path': path
                }
            },
            'body': json.dumps(body) if body else None
        }
        return lambda_handler(event, None)
    
    return invoke

@pytest.fixture
def mock_dynamodb():
    """
    Create a mock DynamoDB table for testing.
    
    This fixture uses moto to create a mock DynamoDB table that:
    - Has the same schema as our real table
    - Supports all DynamoDB operations
    - Is isolated from other tests
    
    Returns:
        Table: A mock DynamoDB table
    """
    with mock_aws():
        # Create mock DynamoDB resource
        dynamodb = boto3.resource('dynamodb')
        
        # Create test table
        table = dynamodb.create_table(
            TableName='test-songs-table',
            KeySchema=[
                {'AttributeName': 'song_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'song_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield table 