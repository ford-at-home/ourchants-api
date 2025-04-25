"""
Schemas for data validation in the Songs API.
"""

from marshmallow import Schema, fields, validate, EXCLUDE

class SongSchema(Schema):
    """Schema for validating song data."""
    song_id = fields.String()
    title = fields.String(required=True, validate=validate.Length(min=1))
    artist = fields.String(required=True, validate=validate.Length(min=1))
    album = fields.String(allow_none=True)
    bpm = fields.String(allow_none=True)
    composer = fields.String(allow_none=True)
    version = fields.String(allow_none=True)
    date = fields.String(allow_none=True)
    filename = fields.String(allow_none=True)
    filepath = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    lineage = fields.List(fields.String(), allow_none=True)
    s3_uri = fields.String(required=True, validate=validate.Length(min=1))

    class Meta:
        unknown = EXCLUDE

# Create instances for reuse
song_schema = SongSchema()
songs_schema = SongSchema(many=True) 