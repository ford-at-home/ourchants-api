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
from moto import mock_dynamodb2
from uuid import uuid4

# Add the lambda directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda'))
from app import lambda_handler

# Set environment variables for testing
os.environ['DYNAMODB_TABLE_NAME'] = 'test-songs-table'

# Set dummy AWS credentials for moto
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture(autouse=True)
def mock_dynamodb():
    """Create a mock DynamoDB table for testing."""
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName='test-songs-table',
            KeySchema=[{'AttributeName': 'song_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'song_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        yield table

@pytest.fixture
def client():
    """Create a test client for the API."""
    def invoke(method, path, body=None):
        event = {
            'httpMethod': method,
            'path': path,
        }
        if body:
            event['body'] = json.dumps(body)
        return lambda_handler(event, None)

    return invoke

@pytest.fixture
def test_song():
    """Create a test song fixture."""
    return {
        'title': 'Test Song',
        'artist': 'Test Artist',
        'lyrics': 'Test lyrics'
    } 