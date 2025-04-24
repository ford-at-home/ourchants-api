"""
Core API logic for the Songs service.

This module contains the business logic for handling song operations,
independent of the API Gateway/Lambda implementation.
"""

import json
from uuid import uuid4
from typing import Dict, List, Optional, Any, Union
from marshmallow import ValidationError
from .schemas import song_schema, songs_schema
from botocore.exceptions import ClientError

class SongsApi:
    def __init__(self, table):
        """Initialize with a DynamoDB table."""
        self.table = table

    def _ensure_s3_uri(self, song_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure s3_uri is properly set in song data."""
        if not song_data.get('s3_uri'):
            # If no s3_uri is provided, construct one from the filename
            if song_data.get('filename'):
                song_data['s3_uri'] = f"s3://ourchants-songs/songs/{song_data['filename']}"
            else:
                song_data['s3_uri'] = ''  # Set empty string if no filename
        return song_data

    def list_songs(self, artist_filter: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """List songs with pagination support.
        
        Args:
            artist_filter: Optional artist name to filter by
            limit: Number of items per page (default: 20)
            offset: Number of items to skip (default: 0)
            
        Returns:
            Dict containing:
            - items: List of songs
            - total: Total number of songs matching the filter
            - has_more: Boolean indicating if there are more items
        """
        try:
            # Validate pagination parameters
            if limit < 1 or limit > 100:
                return {
                    'items': [],
                    'total': 0,
                    'has_more': False
                }
            
            if offset < 0:
                return {
                    'items': [],
                    'total': 0,
                    'has_more': False
                }
            
            # Build the scan parameters
            scan_params = {}
            
            if artist_filter:
                scan_params.update({
                    'FilterExpression': '#artist = :artist',
                    'ExpressionAttributeNames': {'#artist': 'artist'},
                    'ExpressionAttributeValues': {':artist': artist_filter}
                })
            
            # Get all items that match the filter
            response = self.table.scan(**scan_params)
            items = response.get('Items', [])
            
            # Get total count
            total = len(items)
            
            # Apply pagination
            paginated_items = items[offset:offset + limit] if items else []
            
            # Calculate has_more
            has_more = total > offset + limit
            
            # Ensure s3_uri is set for each item
            processed_items = [self._ensure_s3_uri(item) for item in paginated_items]
            
            return {
                'items': [song_schema.dump(item) for item in processed_items],
                'total': total,
                'has_more': has_more
            }
        except ClientError:
            return {
                'items': [],
                'total': 0,
                'has_more': False
            }

    def create_song(self, song_data: Dict[str, str]) -> Dict[str, Any]:
        """Create a new song."""
        # Ensure s3_uri is set
        song_data = self._ensure_s3_uri(song_data)
        
        # Validate and clean input data
        try:
            validated_data = song_schema.load(song_data)
        except ValidationError as e:
            raise ValidationError(e.messages)
            
        # Add UUID and save
        validated_data['song_id'] = str(uuid4())
        self.table.put_item(Item=validated_data)
        return song_schema.dump(validated_data)

    def get_song(self, song_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific song by ID."""
        response = self.table.get_item(Key={'song_id': song_id})
        item = response.get('Item')
        if item:
            # Ensure s3_uri is set
            item = self._ensure_s3_uri(item)
            return song_schema.dump(item)
        return None

    def update_song(self, song_id: str, song_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Update a song."""
        # First check if the song exists
        if not self.get_song(song_id):
            return None

        # Ensure s3_uri is set
        song_data = self._ensure_s3_uri(song_data)

        # Validate and clean input data
        try:
            validated_data = song_schema.load(song_data)
        except ValidationError as e:
            raise ValidationError(e.messages)
            
        # Build update expression
        update_expr = 'SET '
        expr_names = {}
        expr_values = {}
        
        for key, value in validated_data.items():
            if key != 'song_id':  # Don't update the primary key
                update_expr += f'#{key} = :{key}, '
                expr_names[f'#{key}'] = key
                expr_values[f':{key}'] = value
        
        update_expr = update_expr.rstrip(', ')
        
        try:
            response = self.table.update_item(
                Key={'song_id': song_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
                ReturnValues='ALL_NEW'
            )
            item = response.get('Attributes')
            if item:
                # Ensure s3_uri is set
                item = self._ensure_s3_uri(item)
                return song_schema.dump(item)
            return None
        except ClientError:
            return None

    def delete_song(self, song_id: str) -> None:
        """Delete a song."""
        self.table.delete_item(Key={'song_id': song_id}) 