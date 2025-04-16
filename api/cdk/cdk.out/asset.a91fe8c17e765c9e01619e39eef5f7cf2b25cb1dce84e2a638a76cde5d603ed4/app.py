"""
Main application for the Songs API.

This Lambda function handles all API Gateway requests for the Songs API:
- GET /songs - List all songs
- POST /songs - Create a new song
- GET /songs/<id> - Get a specific song
- PUT /songs/<id> - Update a song
- DELETE /songs/<id> - Delete a song

The function uses DynamoDB for storage and returns API Gateway formatted responses.
"""

import json
import logging
from routes.songs import (
    list_songs,
    create_song,
    get_song,
    update_song,
    delete_song
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Lambda function handler."""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        http_method = event['httpMethod']
        path = event['path']
        
        # Route handling
        if path == '/songs':
            if http_method == 'GET':
                return list_songs()
            elif http_method == 'POST':
                return create_song(event['body'])
        elif path.startswith('/songs/'):
            song_id = path.split('/')[-1]
            if http_method == 'GET':
                return get_song(song_id)
            elif http_method == 'PUT':
                return update_song(song_id, event['body'])
            elif http_method == 'DELETE':
                return delete_song(song_id)
        
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 