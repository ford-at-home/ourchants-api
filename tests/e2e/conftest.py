"""
Pytest configuration and fixtures for the end-to-end tests.

This module sets up the test environment with:
- A test client for making HTTP requests to the deployed API
"""

import pytest
import os
import boto3
from botocore.exceptions import ClientError

@pytest.fixture(scope='session')
def api_url():
    """Get the API URL."""
    client = boto3.client("apigatewayv2", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    try:
        apis = client.get_apis()
        for api in apis["Items"]:
            if "songs" in api["Name"].lower():
                return api["ApiEndpoint"]
        raise ValueError("Could not find Songs API in API Gateway v2")
    except ClientError as e:
        if e.response["Error"]["Code"] == "UnrecognizedClientException":
            raise Exception("AWS credentials not configured. Run 'aws configure' or set AWS env vars.") from e
        raise

@pytest.fixture
def test_song():
    """Create a test song object."""
    return {
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
        'lineage': [],
        's3_uri': 's3://ourchants-songs/test_song.mp3'
    } 