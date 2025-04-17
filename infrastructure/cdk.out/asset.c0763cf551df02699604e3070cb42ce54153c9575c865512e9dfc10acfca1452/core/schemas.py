"""
Schemas for data validation in the Songs API.
"""

from marshmallow import Schema, fields, validate, EXCLUDE
from datetime import datetime

class SongSchema(Schema):
    """Schema for validating song data."""
    song_id = fields.String()  # Allow song_id during loading and dumping
    title = fields.String(required=True, validate=validate.Length(min=1))
    artist = fields.String(required=True, validate=validate.Length(min=1))
    album = fields.String(allow_none=True)
    bpm = fields.String(allow_none=True)  # Keeping as string to match existing data
    composer = fields.String(allow_none=True)
    version = fields.String(allow_none=True)
    date = fields.DateTime(allow_none=True, format='%Y-%m-%d %H:%M:%S')
    filename = fields.String(allow_none=True)
    filepath = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    lineage = fields.List(fields.String(), allow_none=True)

    class Meta:
        unknown = EXCLUDE  # Reject unknown fields
        ordered = True  # Keep field order consistent

# Create instances for reuse
song_schema = SongSchema()
songs_schema = SongSchema(many=True) 