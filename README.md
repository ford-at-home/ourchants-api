[![Deploy OurChants API](https://github.com/ford-at-home/ourchants-api/actions/workflows/deploy.yml/badge.svg)](https://github.com/ford-at-home/ourchants-api/actions/workflows/deploy.yml)

# OurChants API

A serverless REST API for managing song data, built with AWS Lambda, API Gateway, and DynamoDB.

## Overview

The OurChants API provides endpoints for managing songs, including their titles, artists, and lyrics. It's built using:

- AWS Lambda for serverless compute
- Amazon API Gateway for REST API management
- Amazon DynamoDB for data storage
- AWS CDK for infrastructure as code
- Python 3.8+ for implementation

## Project Structure

```
.
├── api/                # API implementation code
│   └── swagger.yaml   # OpenAPI/Swagger documentation
├── infrastructure/     # AWS CDK infrastructure code
├── tests/             # Test suites (unit, integration, e2e)
├── utilities/         # Helper scripts and tools
├── setup.py           # Python package configuration
└── songs.json         # Sample song data
```

See individual directory READMEs for detailed information about each component.

## Prerequisites

- Python 3.8 or higher
- AWS CLI configured with appropriate credentials
- Node.js and npm (for AWS CDK)
- AWS CDK CLI (`npm install -g aws-cdk`)

## Quick Start

1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Install dependencies:
   ```bash
   # Install Python dependencies
   python3 -m pip install -r requirements.txt
   
   # Install CDK globally
   npm install -g aws-cdk
   ```

3. Deploy the API:
   ```bash
   cd infrastructure
   ./deploy.sh
   ```

4. Run tests:
   ```bash
   # Run all tests
   python3 -m pytest tests/

   # Run specific test suites
   python3 -m pytest tests/api/        # Unit tests
   python3 -m pytest tests/e2e/        # End-to-end tests
   ```

## API Endpoints

- `GET /songs` - List all songs
- `POST /songs` - Create a new song
- `GET /songs/{song_id}` - Get a specific song
- `PUT /songs/{song_id}` - Update a song
- `DELETE /songs/{song_id}` - Delete a song
- `POST /presigned-url` - Generate a pre-signed URL for S3 object access

### Request/Response Examples

#### Create Song
```json
POST /songs
{
  "title": "Amazing Grace",
  "artist": "John Newton",
  "album": "Hymnal Volume 1",
  "bpm": "70",
  "composer": "John Newton",
  "version": "1.0",
  "date": "2024-04-17 08:46:12",
  "filename": "amazing_grace.mp3",
  "filepath": "Media/amazing_grace.mp3",
  "description": "Traditional hymn",
  "lineage": ["original"]
}
```

Response: 201 Created
```json
{
  "song_id": { "S": "550e8400-e29b-41d4-a716-446655440000" },
  "title": { "S": "Amazing Grace" },
  "artist": { "S": "John Newton" },
  "album": { "S": "Hymnal Volume 1" },
  "bpm": { "S": "70" },
  "composer": { "S": "John Newton" },
  "version": { "S": "1.0" },
  "date": { "S": "2024-04-17 08:46:12" },
  "filename": { "S": "amazing_grace.mp3" },
  "filepath": { "S": "Media/amazing_grace.mp3" },
  "description": { "S": "Traditional hymn" },
  "lineage": { "L": [{ "S": "original" }] },
  "s3_uri": { "S": "s3://ourchants-songs/songs/amazing_grace.mp3" }
}
```

#### Get Song
```json
GET /songs/550e8400-e29b-41d4-a716-446655440000
```

Response: 200 OK
```json
{
  "song_id": { "S": "550e8400-e29b-41d4-a716-446655440000" },
  "title": { "S": "Amazing Grace" },
  "artist": { "S": "John Newton" },
  "album": { "S": "Hymnal Volume 1" },
  "bpm": { "S": "70" },
  "composer": { "S": "John Newton" },
  "version": { "S": "1.0" },
  "date": { "S": "2024-04-17 08:46:12" },
  "filename": { "S": "amazing_grace.mp3" },
  "filepath": { "S": "Media/amazing_grace.mp3" },
  "description": { "S": "Traditional hymn" },
  "lineage": { "L": [{ "S": "original" }] },
  "s3_uri": { "S": "s3://ourchants-songs/songs/amazing_grace.mp3" }
}
```

#### List Songs
```json
GET /songs
```

Response: 200 OK
```json
[
  {
    "song_id": { "S": "550e8400-e29b-41d4-a716-446655440000" },
    "title": { "S": "Amazing Grace" },
    "artist": { "S": "John Newton" },
    "album": { "S": "Hymnal Volume 1" },
    "bpm": { "S": "70" },
    "composer": { "S": "John Newton" },
    "version": { "S": "1.0" },
    "date": { "S": "2024-04-17 08:46:12" },
    "filename": { "S": "amazing_grace.mp3" },
    "filepath": { "S": "Media/amazing_grace.mp3" },
    "description": { "S": "Traditional hymn" },
    "lineage": { "L": [{ "S": "original" }] },
    "s3_uri": { "S": "s3://ourchants-songs/songs/amazing_grace.mp3" }
  }
]
```

Note: Only songs with an s3_uri attribute will be returned in the list.

#### Update Song
```json
PUT /songs/550e8400-e29b-41d4-a716-446655440000
{
  "title": "Updated Amazing Grace",
  "artist": "John Newton",
  "album": "Hymnal Volume 1",
  "bpm": "72",
  "composer": "John Newton",
  "version": "1.1",
  "date": "2024-04-17 08:46:12",
  "filename": "amazing_grace.mp3",
  "filepath": "Media/amazing_grace.mp3",
  "description": "Updated traditional hymn",
  "lineage": ["original", "updated"]
}
```

Response: 200 OK
```json
{
  "song_id": { "S": "550e8400-e29b-41d4-a716-446655440000" },
  "title": { "S": "Updated Amazing Grace" },
  "artist": { "S": "John Newton" },
  "album": { "S": "Hymnal Volume 1" },
  "bpm": { "S": "72" },
  "composer": { "S": "John Newton" },
  "version": { "S": "1.1" },
  "date": { "S": "2024-04-17 08:46:12" },
  "filename": { "S": "amazing_grace.mp3" },
  "filepath": { "S": "Media/amazing_grace.mp3" },
  "description": { "S": "Updated traditional hymn" },
  "lineage": { "L": [{ "S": "original" }, { "S": "updated" }] },
  "s3_uri": { "S": "s3://ourchants-songs/songs/amazing_grace.mp3" }
}
```

#### Delete Song
```json
DELETE /songs/550e8400-e29b-41d4-a716-446655440000
```

Response: 204 No Content

#### Generate Pre-signed URL
```json
POST /presigned-url
{
  "bucket": "ourchants-songs",
  "key": "songs/amazing_grace.mp3"
}
```