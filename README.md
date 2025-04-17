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
   python3 -m pip install -r infrastructure/requirements.txt
   python3 -m pip install -r tests/requirements-test.txt
   
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

### Request/Response Examples

#### Create Song
```json
POST /songs
{
    "title": "21 Wairaitirai Suntarai snippet-?",
    "artist": "Muse",
    "album": "Muse",
    "bpm": "120",
    "composer": "Allah",
    "version": "del Tiempo",
    "date": "2012-04-06 09:36:00",
    "filename": "21_wairaitirai_suntarai_snippet-_.mp3",
    "filepath": "Media.localized/21_wairaitirai_suntarai_snippet-_.mp3",
    "description": "",
    "lineage": []
}
```

#### Response
```json
{
    "song_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "21 Wairaitirai Suntarai snippet-?",
    "artist": "Muse",
    "album": "Muse",
    "bpm": "120",
    "composer": "Allah",
    "version": "del Tiempo",
    "date": "2012-04-06 09:36:00",
    "filename": "21_wairaitirai_suntarai_snippet-_.mp3",
    "filepath": "Media.localized/21_wairaitirai_suntarai_snippet-_.mp3",
    "description": "",
    "lineage": []
}
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development guidelines, including:
- Local development setup
- Testing strategies
- Deployment procedures
- Troubleshooting guides

## Testing

The project includes three levels of testing:
1. Unit tests (`tests/api/`)
2. Integration tests (`tests/api/`)
3. End-to-end tests (`tests/e2e/`)

See the [tests/README.md](tests/README.md) for detailed testing information.

## Infrastructure

The API infrastructure is managed using AWS CDK. Key components:
- DynamoDB table for song storage
- Lambda function for API logic
- API Gateway for REST interface

See [infrastructure/README.md](infrastructure/README.md) for infrastructure details.

## API Documentation

The API is documented using the OpenAPI (Swagger) specification. You can find the complete API documentation in `api/swagger.yaml`. This documentation includes:

- Detailed endpoint descriptions
- Request/response schemas
- Authentication requirements
- Example requests and responses

To view the documentation in a user-friendly format:

1. Visit [Swagger Editor](https://editor.swagger.io/)
2. Copy the contents of `api/swagger.yaml`
3. Paste into the editor

Alternatively, you can use tools like `swagger-ui` to serve the documentation locally:

```bash
npm install -g swagger-ui-cli
swagger-ui-cli serve api/swagger.yaml
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.