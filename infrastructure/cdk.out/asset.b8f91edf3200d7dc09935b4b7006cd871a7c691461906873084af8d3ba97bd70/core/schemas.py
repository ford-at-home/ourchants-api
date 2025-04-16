"""
Schemas for data validation in the Songs API.
"""

from marshmallow import Schema, fields, validate

class SongSchema(Schema):
    """Schema for validating song data."""
    song_id = fields.String(dump_only=True)  # Read-only field
    title = fields.String(required=True, validate=validate.Length(min=1))
    artist = fields.String(required=True, validate=validate.Length(min=1))
    lyrics = fields.String(required=True, validate=validate.Length(min=1))

# Create instances for reuse
song_schema = SongSchema()
songs_schema = SongSchema(many=True) 