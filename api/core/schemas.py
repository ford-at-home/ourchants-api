"""
Schemas for data validation in the Songs API.
"""

from marshmallow import Schema, fields, validate, EXCLUDE

class SongSchema(Schema):
    """Schema for validating song data."""
    song_id = fields.String()  # Allow song_id during loading and dumping
    title = fields.String(required=True, validate=validate.Length(min=1))
    artist = fields.String(required=True, validate=validate.Length(min=1))
    lyrics = fields.String(required=True, validate=validate.Length(min=1))

    class Meta:
        unknown = EXCLUDE  # Reject unknown fields

# Create instances for reuse
song_schema = SongSchema()
songs_schema = SongSchema(many=True) 