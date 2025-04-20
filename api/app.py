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
    retries={'max_attempts': 3},
    connect_timeout=5,
    read_timeout=5
)

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
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'error': 'Invalid request format',
                    'details': 'The request is missing required HTTP method or path',
                    'code': 'INVALID_REQUEST'
                })
            }
        
        # Route handling
        if path == '/songs':
            if http_method == 'GET':
                songs = api.list_songs()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
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
                    bucket = body.get('bucket', os.getenv('S3_BUCKET'))
                    key = body.get('key')
                    
                    # Validate bucket name
                    is_valid_bucket, bucket_error = validate_bucket_name(bucket)
                    if not is_valid_bucket:
                        return {
                            'statusCode': 400,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                                'Access-Control-Allow-Headers': 'Content-Type'
                            },
                            'body': json.dumps({
                                'error': 'Invalid bucket name',
                                'details': bucket_error,
                                'code': 'INVALID_BUCKET_NAME'
                            })
                        }
                    
                    # Validate key
                    is_valid_key, key_error = validate_object_key(key)
                    if not is_valid_key:
                        return {
                            'statusCode': 400,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                                'Access-Control-Allow-Headers': 'Content-Type'
                            },
                            'body': json.dumps({
                                'error': 'Invalid object key',
                                'details': key_error,
                                'code': 'INVALID_OBJECT_KEY'
                            })
                        }
                    
                    # Check if bucket exists
                    try:
                        s3_client.head_bucket(Bucket=bucket)
                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', '')
                        if error_code in ['404', 'NoSuchBucket']:
                            return {
                                'statusCode': 404,
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'OPTIONS,POST',
                                    'Access-Control-Allow-Headers': 'Content-Type'
                                },
                                'body': json.dumps({
                                    'error': f'Bucket {bucket} not found',
                                    'details': 'The specified S3 bucket does not exist',
                                    'code': 'BUCKET_NOT_FOUND'
                                })
                            }
                        elif error_code in ['403', 'Forbidden']:
                            return {
                                'statusCode': 404,
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'OPTIONS,POST',
                                    'Access-Control-Allow-Headers': 'Content-Type'
                                },
                                'body': json.dumps({
                                    'error': f'Bucket {bucket} not found or access denied',
                                    'details': 'The specified S3 bucket does not exist or access is denied',
                                    'code': 'BUCKET_NOT_FOUND'
                                })
                            }
                        raise

                    # Check if object exists
                    try:
                        s3_client.head_object(Bucket=bucket, Key=key)
                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', '')
                        if error_code in ['404', 'NoSuchKey']:
                            return {
                                'statusCode': 404,
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'OPTIONS,POST',
                                    'Access-Control-Allow-Headers': 'Content-Type'
                                },
                                'body': json.dumps({
                                    'error': f'Object {key} not found in bucket {bucket}',
                                    'details': 'The specified S3 object does not exist in the bucket',
                                    'code': 'OBJECT_NOT_FOUND'
                                })
                            }
                        raise
                    
                    url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={
                            'Bucket': bucket,
                            'Key': key
                        },
                        ExpiresIn=3600
                    )
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
                    logger.error(f"Error generating pre-signed URL: {str(e)}")
                    return {
                        'statusCode': 500,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'OPTIONS,POST',
                            'Access-Control-Allow-Headers': 'Content-Type'
                        },
                        'body': json.dumps({
                            'error': 'Failed to generate pre-signed URL',
                            'details': str(e),
                            'code': 'INTERNAL_ERROR'
                        })
                    }
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