"""
Route handlers for the Songs API.

This module contains all the route handlers for the Songs API endpoints:
- GET /songs - List all songs
- POST /songs - Create a new song
- GET /songs/<id> - Get a specific song
- PUT /songs/<id> - Update a song
- DELETE /songs/<id> - Delete a song
"""

import json
import os
import boto3
import logging
from uuid import uuid4
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_table():
    """Get DynamoDB table."""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table_name = os.getenv('DYNAMODB_TABLE_NAME')
    if not table_name:
        raise ValueError("DYNAMODB_TABLE_NAME environment variable is not set")
    return dynamodb.Table(table_name)

def list_songs():
    """List all songs."""
    try:
        table = get_table()
        response = table.scan()
        return {
            'statusCode': 200,
            'body': json.dumps(response.get('Items', []))
        }
    except ClientError as e:
        logger.error(f"Error listing songs: {str(e)}")
        raise

def create_song(body):
    """Create a new song."""
    try:
        table = get_table()
        song_data = json.loads(body)
        song_data['song_id'] = str(uuid4())
        table.put_item(Item=song_data)
        return {
            'statusCode': 201,
            'body': json.dumps(song_data)
        }
    except ClientError as e:
        logger.error(f"Error creating song: {str(e)}")
        raise

def get_song(song_id):
    """Get a specific song by ID."""
    try:
        table = get_table()
        response = table.get_item(Key={'song_id': song_id})
        item = response.get('Item')
        if item is None:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Song not found'})
            }
        return {
            'statusCode': 200,
            'body': json.dumps(item)
        }
    except ClientError as e:
        logger.error(f"Error getting song: {str(e)}")
        raise

def update_song(song_id, body):
    """Update a song."""
    try:
        table = get_table()
        song_data = json.loads(body)
        
        # Build update expression
        update_expr = 'SET '
        expr_names = {}
        expr_values = {}
        
        for key, value in song_data.items():
            if key != 'song_id':  # Don't update the primary key
                update_expr += f'#{key} = :{key}, '
                expr_names[f'#{key}'] = key
                expr_values[f':{key}'] = value
        
        update_expr = update_expr.rstrip(', ')
        
        response = table.update_item(
            Key={'song_id': song_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'])
        }
    except ClientError as e:
        logger.error(f"Error updating song: {str(e)}")
        raise

def delete_song(song_id):
    """Delete a song."""
    try:
        table = get_table()
        table.delete_item(Key={'song_id': song_id})
        return {
            'statusCode': 204,
            'body': ''
        }
    except ClientError as e:
        logger.error(f"Error deleting song: {str(e)}")
        raise 