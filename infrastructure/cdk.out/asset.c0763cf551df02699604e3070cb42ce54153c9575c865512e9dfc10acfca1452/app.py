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
    """Handle API Gateway requests."""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        http_method = event['httpMethod']
        path = event['path']
        
        # Route handling
        if path == '/songs':
            if http_method == 'GET':
                songs = api.list_songs()
                return success(200, songs)
            elif http_method == 'POST':
                song = api.create_song(json.loads(event['body']))
                return success(201, song)
        elif path.startswith('/songs/'):
            song_id = path.split('/')[-1]
            if http_method == 'GET':
                song = api.get_song(song_id)
                if not song:
                    return error(404, 'Song not found')
                return success(200, song)
            elif http_method == 'PUT':
                song = api.update_song(song_id, json.loads(event['body']))
                if not song:
                    return error(404, 'Song not found')
                return success(200, song)
            elif http_method == 'DELETE':
                api.delete_song(song_id)
                return success(204)
        
        return error(405, 'Method not allowed')
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return error(400, str(e.messages))
    except ClientError as e:
        logger.error(f"AWS error: {str(e)}")
        return error(500, str(e))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {str(e)}")
        return error(400, 'Invalid JSON in request body')
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return error(500, str(e)) 