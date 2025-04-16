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

@pytest.fixture(autouse=True)
def mock_dynamodb():
    """This fixture will automatically run for all tests"""
    with mock_aws():
        # Create the DynamoDB client and table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName='test-songs-table',  # Match the environment variable
            KeySchema=[{'AttributeName': 'song_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'song_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        yield table

# Import the app after setting up environment variables
from api.app import lambda_handler

@pytest.fixture
def client():
    """Create a test client for the API."""
    def invoke(method='GET', path='/', body=None):
        event = {
            'httpMethod': method,
            'path': path,
            'body': json.dumps(body) if body else None
        }
        return lambda_handler(event, None)
    return invoke

@pytest.fixture
def test_song():
    """Create a test song fixture."""
    return {
        'song_id': str(uuid4()),
        'title': 'Test Song',
        'artist': 'Test Artist',
        'lyrics': 'Test lyrics'
    } 