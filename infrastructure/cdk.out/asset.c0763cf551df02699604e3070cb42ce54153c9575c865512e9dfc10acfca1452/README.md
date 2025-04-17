# API Implementation

This directory contains the core API implementation code for the OurChants API.

## Directory Structure

```
api/
├── app.py              # Lambda handler and API Gateway integration
├── core/              # Core business logic
│   ├── api.py         # Main API implementation
│   ├── schemas.py     # Data validation schemas
│   └── responses.py   # HTTP response formatting
└── README.md          # This file
```

## Components

### Lambda Handler (`app.py`)

The Lambda handler is responsible for:
- Processing API Gateway events
- Routing requests to appropriate handlers
- Error handling and response formatting
- AWS service initialization

Key features:
- Comprehensive error handling
- Structured logging
- Input validation
- HTTP response formatting

### Core API (`core/api.py`)

The `SongsApi` class implements the core business logic:
- `list_songs()`: Retrieve all songs
- `create_song(data)`: Create a new song
- `get_song(song_id)`: Get a specific song
- `update_song(song_id, data)`: Update a song
- `delete_song(song_id)`: Delete a song

### Data Validation (`core/schemas.py`)

Uses Marshmallow for data validation:
- `SongSchema`: Validates song data
  - Required fields: title, artist, lyrics
  - Field validation rules
  - Serialization/deserialization

### Response Formatting (`core/responses.py`)

Standardizes API responses:
- `success(status_code, body)`: Format successful responses
- `error(status_code, message)`: Format error responses

## Usage

The API is designed to be run as an AWS Lambda function. Local testing can be done using the test suite:

```bash
python3 -m pytest tests/api/
```

## Development

1. Make changes to the API code
2. Run unit tests
3. Run integration tests
4. Deploy using the infrastructure stack

## Error Handling

The API implements comprehensive error handling:
- Validation errors (400 Bad Request)
- Not found errors (404 Not Found)
- Internal server errors (500 Internal Server Error)
- AWS service errors

## Logging

Structured logging is implemented throughout:
- Request details
- Error information
- Operation outcomes
- Performance metrics

## Dependencies

- `boto3`: AWS SDK for Python
- `marshmallow`: Data validation
- Other dependencies listed in `setup.py` 