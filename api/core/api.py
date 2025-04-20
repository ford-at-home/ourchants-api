"""
Core API logic for the Songs service.

This module contains the business logic for handling song operations,
independent of the API Gateway/Lambda implementation.
"""

import json
from uuid import uuid4
from typing import Dict, List, Optional, Any
from marshmallow import ValidationError
from .schemas import song_schema, songs_schema
from botocore.exceptions import ClientError

class SongsApi:
    def __init__(self, table):
        """Initialize with a DynamoDB table."""
        self.table = table

    def list_songs(self) -> List[Dict[str, Any]]:
        """List all songs that have an s3_uri attribute."""
        response = self.table.scan()
        items = response.get('Items', [])
        # Filter for songs that have an s3_uri attribute
        items_with_s3_uri = [item for item in items if 's3_uri' in item]
        return songs_schema.dump(items_with_s3_uri)

    def create_song(self, song_data: Dict[str, str]) -> Dict[str, Any]:
        """Create a new song."""
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
        return song_schema.dump(item) if item else None

    def update_song(self, song_id: str, song_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Update a song."""
        # First check if the song exists
        if not self.get_song(song_id):
            return None

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
            return song_schema.dump(item) if item else None
        except ClientError:
            return None

    def delete_song(self, song_id: str) -> None:
        """Delete a song."""
        self.table.delete_item(Key={'song_id': song_id}) 