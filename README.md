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
  "song_id": "550e8400-e29b-41d4-a716-446655440000",
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
  "lineage": ["original"],
  "s3_uri": "s3://ourchants-songs/songs/amazing_grace.mp3"
}
```

#### Get Song
```json
GET /songs/550e8400-e29b-41d4-a716-446655440000
```

Response: 200 OK
```json
{
  "song_id": "550e8400-e29b-41d4-a716-446655440000",
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
  "lineage": ["original"],
  "s3_uri": "s3://ourchants-songs/songs/amazing_grace.mp3"
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
    "song_id": "550e8400-e29b-41d4-a716-446655440000",
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
    "lineage": ["original"],
    "s3_uri": "s3://ourchants-songs/songs/amazing_grace.mp3"
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
  "song_id": "550e8400-e29b-41d4-a716-446655440000",
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
  "lineage": ["original", "updated"],
  "s3_uri": "s3://ourchants-songs/songs/amazing_grace.mp3"
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

Response: 200 OK
```json
{
  "url": "https://ourchants-songs.s3.amazonaws.com/songs/amazing_grace.mp3?X-Amz-Algorithm=...",
  "expiresIn": 3600
}
```

Error Response (404 Not Found):
```json
{
  "error": "Bucket not found or access denied",
  "code": "BUCKET_NOT_FOUND"
}
```

## Storage

The API uses two main storage components:

1. **DynamoDB**: Stores song metadata and details
   - Table name: `songs`
   - Primary key: `song_id` (String)

2. **S3 Bucket**: Stores song files (MP3, M4A)
   - Bucket name: `ourchants-songs`
   - File organization: `songs/{song_id}/{filename}`
   - Pre-signed URLs: Generated for secure, time-limited access

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400 Bad Request: Invalid input data
- 404 Not Found: Resource not found
- 409 Conflict: Concurrent modification conflict
- 500 Internal Server Error: Server-side error

Error response format:
```json
{
  "error": "Error message description"
}
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development instructions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Usage

This project uses a Makefile to simplify common development tasks. Here are the available commands:

### Testing
```bash
make test-api        # Run API tests
make test-e2e        # Run end-to-end tests
make test-all        # Run all tests
```

### AWS Operations
```bash
make check-aws-credentials  # Verify AWS credentials
make check-aws-profiles    # List available AWS profiles
make deploy          # Deploy infrastructure
```

### Maintenance
```bash
make clean           # Clean up Python cache files
make help            # Show available commands
```