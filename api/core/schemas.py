"""
Schemas for data validation in the Songs API.
"""

from marshmallow import Schema, fields, validate, EXCLUDE, pre_load, post_dump
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
    date = fields.String(allow_none=True)  # Store as string in DynamoDB
    filename = fields.String(allow_none=True)
    filepath = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    lineage = fields.List(fields.String(), allow_none=True)
    s3_uri = fields.String(required=True, validate=validate.Length(min=1))  # S3 URI is required

    class Meta:
        unknown = EXCLUDE  # Reject unknown fields
        ordered = True  # Keep field order consistent

    @pre_load
    def format_date(self, data, **kwargs):
        """Format date before loading."""
        if isinstance(data.get('date'), datetime):
            data['date'] = data['date'].strftime('%Y-%m-%d %H:%M:%S')
        return data

    @post_dump
    def ensure_defaults(self, data, **kwargs):
        """Ensure all fields have default values."""
        for field in self.fields:
            if field not in data:
                if field == 's3_uri':
                    # For s3_uri, use an empty string instead of None
                    data[field] = ''
                else:
                    data[field] = None
        if 'lineage' in data and data['lineage'] is None:
            data['lineage'] = []
        return data

# Create instances for reuse
song_schema = SongSchema()
songs_schema = SongSchema(many=True) 