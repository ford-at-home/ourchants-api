"""
Test configuration for the Songs API tests.

This module defines constants and configuration values used across test files:
- Test resource names (DynamoDB table, Lambda function, etc.)
- Test environment variables
- AWS region and credentials for testing

These values can be overridden using environment variables for different
test environments.
"""

import os

# Test resource names that should remain constant across CDK deployments
TEST_RESOURCES = {
    'DYNAMODB_TABLE_NAME': os.getenv('TEST_DYNAMODB_TABLE_NAME', 'ourchants-items-test'),
    'LAMBDA_FUNCTION_NAME': os.getenv('TEST_LAMBDA_FUNCTION_NAME', 'songs-api-test'),
    'API_GATEWAY_NAME': os.getenv('TEST_API_GATEWAY_NAME', 'songs-api-test'),
    'API_STAGE': os.getenv('TEST_API_STAGE', 'test')
}

# Test environment variables
TEST_ENV = {
    'AWS_REGION': 'us-east-1',
    'AWS_ACCESS_KEY_ID': 'testing',
    'AWS_SECRET_ACCESS_KEY': 'testing',
    'AWS_SECURITY_TOKEN': 'testing',
    'AWS_SESSION_TOKEN': 'testing'
} 