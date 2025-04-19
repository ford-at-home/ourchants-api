"""
Lambda handler for the Songs API.

This module handles API Gateway events and delegates to the core API logic.
"""

import json
import os
import logging
import boto3
from botocore.exceptions import ClientError
from marshmallow import ValidationError
from core.api import SongsApi
from core.responses import success, error

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE_NAME'))
api = SongsApi(table)

def lambda_handler(event, context):
    """Handle API Gateway HTTP API events."""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract HTTP method and path from HTTP API event
        http_method = event['requestContext']['http']['method']
        path = event['requestContext']['http']['path']
        body = event.get('body', '{}')
        
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
                song = api.create_song(json.loads(body))
                return {
                    'statusCode': 201,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(song)
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
                song = api.update_song(song_id, json.loads(body))
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
            'body': json.dumps({'error': str(e)})
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
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        } 