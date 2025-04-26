"""
Lambda handler for the Songs API.

This module handles API Gateway events and delegates to the core API logic.
"""

import json
import os
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from marshmallow import ValidationError
from core.api import SongsApi
from core.responses import success, error
from core.validation import validate_bucket_name, validate_object_key

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure S3 client with rate limiting
s3_config = Config(
    signature_version='s3v4',
    retries={
        'max_attempts': 3,
        'mode': 'adaptive',
        'total_max_attempts': 3
    },
    connect_timeout=5,
    read_timeout=5,
    max_pool_connections=50
)

def error_response(message: str, code: str, status_code: int = 400, details: dict = None) -> dict:
    """Return a standardized error response.
    
    Args:
        message: The error message to display
        code: The error code identifier
        status_code: The HTTP status code (default: 400)
        details: Additional error details (optional)
    """
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps({
            'error': message,
            'code': code
        })
    }
    
    if details:
        response['body'] = json.dumps({
            'error': message,
            'code': code,
            'details': details
        })
    
    return response

def lambda_handler(event, context):
    """Handle API Gateway HTTP API events."""
    try:
        # Initialize AWS clients inside the handler
        dynamodb = boto3.resource('dynamodb')
        s3_client = boto3.client('s3', config=s3_config)
        table = dynamodb.Table(os.getenv('DYNAMODB_TABLE_NAME'))
        api = SongsApi(table)
        
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract HTTP method and path from HTTP API event
        http_method = event.get('requestContext', {}).get('http', {}).get('method')
        path = event.get('requestContext', {}).get('http', {}).get('path')
        raw_body = event.get('body', '{}')
        
        # Parse body if it's a string
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except json.JSONDecodeError:
            body = {}
        
        if not http_method or not path:
            logger.error("Invalid event structure: missing method or path")
            return error_response("Invalid request format", "INVALID_REQUEST")
        
        # Handle CORS preflight requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }
        
        # Route requests based on path and method
        if path == '/songs':
            if http_method == 'GET':
                songs = api.list_songs()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type'
                    },
                    'body': json.dumps(songs)
                }
            elif http_method == 'POST':
                song = api.create_song(body)
                return {
                    'statusCode': 201,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(song)
                }
        elif path == '/presigned-url':
            if http_method == 'POST':
                try:
                    logger.info(f"Presigned URL request - Raw body: {raw_body}")
                    logger.info(f"Presigned URL request - Parsed body: {body}")
                    
                    # Ensure body is a dictionary and has a key
                    if not isinstance(body, dict) or not body:
                        logger.error("Presigned URL request - Invalid body format")
                        return error_response("Object key cannot be empty", "INVALID_OBJECT_KEY")
                    
                    key = body.get('key')
                    if not key:
                        logger.error("Presigned URL request - Missing key")
                        return error_response("Object key cannot be empty", "INVALID_OBJECT_KEY")
                    
                    bucket = body.get('bucket', os.getenv('S3_BUCKET'))
                    logger.info(f"Presigned URL request - Bucket: {bucket}, Key: {key}")
                    
                    # Validate bucket name
                    is_valid_bucket, bucket_error = validate_bucket_name(bucket)
                    if not is_valid_bucket:
                        logger.error(f"Presigned URL request - Invalid bucket: {bucket_error}")
                        return error_response("Invalid bucket name", "INVALID_BUCKET_NAME")
                    
                    # Validate key format
                    is_valid_key, key_error = validate_object_key(key)
                    if not is_valid_key:
                        logger.error(f"Presigned URL request - Invalid key: {key_error}")
                        return error_response("Invalid object key", "INVALID_OBJECT_KEY")
                    
                    # Check if bucket exists
                    try:
                        logger.info(f"Presigned URL request - Checking bucket existence: {bucket}")
                        s3_client.head_bucket(Bucket=bucket)
                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', '')
                        error_message = e.response.get('Error', {}).get('Message', '')
                        logger.error(f"Presigned URL request - Bucket check failed: {error_code} - {error_message}")
                        if error_code in ['404', 'NoSuchBucket']:
                            return error_response(
                                f"Bucket {bucket} not found",
                                "BUCKET_NOT_FOUND",
                                404,
                                {'bucket': bucket}
                            )
                        elif error_code in ['403', 'Forbidden']:
                            return error_response(
                                f"Bucket {bucket} not found or access denied",
                                "BUCKET_NOT_FOUND",
                                404,
                                {'bucket': bucket, 'reason': 'access_denied'}
                            )
                        elif error_code == 'ThrottlingException':
                            return error_response(
                                "Rate limit exceeded. Please try again later.",
                                "RATE_LIMIT_EXCEEDED",
                                429,
                                {'retry_after': 5}
                            )
                        raise

                    # Check if object exists
                    try:
                        logger.info(f"Presigned URL request - Checking object existence: {bucket}/{key}")
                        s3_client.head_object(Bucket=bucket, Key=key)
                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', '')
                        error_message = e.response.get('Error', {}).get('Message', '')
                        logger.error(f"Presigned URL request - Object check failed: {error_code} - {error_message}")
                        if error_code in ['404', 'NoSuchKey']:
                            return error_response(
                                f"Object {key} not found in bucket {bucket}",
                                "OBJECT_NOT_FOUND",
                                404,
                                {'bucket': bucket, 'key': key}
                            )
                        elif error_code == 'ThrottlingException':
                            return error_response(
                                "Rate limit exceeded. Please try again later.",
                                "RATE_LIMIT_EXCEEDED",
                                429,
                                {'retry_after': 5}
                            )
                        raise
                    
                    try:
                        logger.info(f"Presigned URL request - Generating URL for: {bucket}/{key}")
                        url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={
                                'Bucket': bucket,
                                'Key': key
                            },
                            ExpiresIn=3600
                        )
                        logger.info(f"Presigned URL request - Generated URL: {url}")
                        return {
                            'statusCode': 200,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                                'Access-Control-Allow-Headers': 'Content-Type'
                            },
                            'body': json.dumps({
                                'url': url,
                                'expiresIn': 3600
                            })
                        }
                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', '')
                        error_message = e.response.get('Error', {}).get('Message', '')
                        logger.error(f"Presigned URL request - URL generation failed: {error_code} - {error_message}")
                        if error_code == 'ThrottlingException':
                            return error_response(
                                "Rate limit exceeded. Please try again later.",
                                "RATE_LIMIT_EXCEEDED",
                                429,
                                {'retry_after': 5}
                            )
                        logger.error(f"Error generating pre-signed URL: {str(e)}")
                        return error_response(
                            "Failed to generate pre-signed URL",
                            "INTERNAL_ERROR",
                            500,
                            {'error_code': error_code}
                        )
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    error_message = e.response.get('Error', {}).get('Message', '')
                    logger.error(f"Presigned URL request - Unexpected error: {error_code} - {error_message}")
                    return error_response("Failed to generate pre-signed URL", "INTERNAL_ERROR", 500)
        elif path.startswith('/songs/'):
            song_id = path.split('/')[-1]
            if http_method == 'GET':
                song = api.get_song(song_id)
                if not song:
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Song not found'})
                    }
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(song)
                }
            elif http_method == 'PUT':
                song = api.update_song(song_id, body)
                if not song:
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Song not found'})
                    }
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(song)
                }
            elif http_method == 'DELETE':
                api.delete_song(song_id)
                return {
                    'statusCode': 204,
                    'headers': {
                        'Access-Control-Allow-Origin': '*'
                    }
                }
        
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e.messages)})
        }
    except ClientError as e:
        logger.error(f"AWS error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'code': 'INTERNAL_ERROR'
            })
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'code': 'INTERNAL_ERROR'
            })
        } 