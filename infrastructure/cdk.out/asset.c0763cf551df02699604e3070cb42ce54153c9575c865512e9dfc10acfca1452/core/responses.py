"""
HTTP response formatting for the API Gateway.
"""

import json
from typing import Any, Dict, Optional

def success(status_code: int = 200, body: Optional[Any] = None) -> Dict[str, Any]:
    """Create a successful response."""
    response = {'statusCode': status_code}
    if body is not None:
        response['body'] = json.dumps(body)
    return response

def error(status_code: int = 500, message: str = 'Internal server error') -> Dict[str, Any]:
    """Create an error response."""
    return {
        'statusCode': status_code,
        'body': json.dumps({'error': message})
    } 