"""
Pytest configuration and fixtures for the Songs API tests.

This module sets up the test environment with:
- Mocked AWS credentials for testing
- A test client for making Lambda invocations
- A mocked DynamoDB table for testing database operations

The fixtures defined here are automatically available to all test files.
"""

import pytest
import json
import sys
import os
import boto3
from moto import mock_aws
from uuid import uuid4

# Add the api directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

# Set environment variables for testing
os.environ['DYNAMODB_TABLE_NAME'] = 'test-songs-table'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def mock_dynamodb():
    """Create a mock DynamoDB table for testing."""
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

# Import the app after setting up environment variables
from api.app import lambda_handler

@pytest.fixture
def client(mock_dynamodb):
    """Create a test client."""
    def invoke(method, path, body=None):
        """Simulate API Gateway call."""
        event = {
            'httpMethod': method,
            'path': path,
            'body': json.dumps(body) if body else None
        }
        return lambda_handler(event, None)
    
    return invoke

@pytest.fixture
def test_song():
    """Create a test song object."""
    return {
        'song_id': str(uuid4()),
        'title': 'Test Song',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'bpm': '120',
        'composer': 'Test Composer',
        'version': 'Test Version',
        'date': '2024-03-20 12:00:00',  # Use string format
        'filename': 'test_song.mp3',
        'filepath': 'Media/test_song.mp3',
        'description': 'Test description',
        'lineage': []
    } 