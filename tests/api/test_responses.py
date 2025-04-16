"""
Tests for HTTP response formatting.
"""

import json
from api.core.responses import success, error

def test_success_with_body():
    """Test successful response with body."""
    data = {'key': 'value'}
    response = success(200, data)
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == data

def test_success_without_body():
    """Test successful response without body."""
    response = success(204)
    assert response['statusCode'] == 204
    assert 'body' not in response

def test_error_response():
    """Test error response."""
    response = error(404, 'Not found')
    assert response['statusCode'] == 404
    assert json.loads(response['body']) == {'error': 'Not found'}

def test_default_error():
    """Test default error response."""
    response = error()
    assert response['statusCode'] == 500
    assert json.loads(response['body']) == {'error': 'Internal server error'} 