# Development Guide

## Prerequisites

- Python 3.8 or higher
- AWS credentials configured
- AWS CDK installed (`npm install -g aws-cdk`)
- pip (Python package manager)

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ourchants-api.git
cd ourchants-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with:
DYNAMODB_TABLE_NAME=ourchants-items
```

## Project Structure

```
api/
├── lambda/                 # Lambda function code
│   ├── app.py             # Main Lambda handler
│   └── routes/            # Route handlers
│       └── songs.py       # Song-related routes
├── cdk/                   # CDK infrastructure
│   └── songs_api/         # Songs API stack
│       ├── app.py         # CDK app entry point
│       └── songs_api_stack.py
├── tests/                 # Test suite
│   ├── conftest.py        # Test fixtures
│   ├── test_routes.py     # API tests
│   ├── test_integration.py # Integration tests
│   └── test_config.py     # Configuration tests
└── requirements.txt       # Python dependencies
```

## Code Organization

### Lambda Function

The Lambda function is organized into two main components:

1. `app.py`: Main Lambda handler
   - Handles API Gateway requests
   - Routes requests to appropriate handlers
   - Manages error handling and logging
   - Returns API Gateway formatted responses

2. `routes/songs.py`: Route handlers
   - Contains all CRUD operations for songs
   - Handles DynamoDB interactions
   - Implements business logic
   - Includes comprehensive error handling and logging

### CDK Infrastructure

The CDK stack (`songs_api_stack.py`) defines:
- DynamoDB table with `song_id` as partition key
- Lambda function with necessary permissions
- API Gateway with REST endpoints
- Environment variables for Lambda
- Note: Authentication is currently disabled (Cognito integration commented out)

## Testing

### Running Tests

1. Run all tests:
```bash
python -m pytest tests/ -v
```

2. Run tests with coverage:
```bash
python -m pytest tests/ --cov=.
```

3. Watch tests during development:
```bash
./watch_tests.sh
```

### Test Structure

The test suite includes:
- `tests/conftest.py`: Test fixtures and setup
- `tests/test_routes.py`: Unit tests for API endpoints
- `tests/test_integration.py`: Integration tests
- `tests/test_config.py`: Configuration tests

## API Endpoints

### GET /songs
Lists all songs in the database.

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
    "lineage": ["original"]
  }
]
```

### POST /songs
Creates a new song.

Request:
```json
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
  "lineage": ["original"]
}
```

### GET /songs/{song_id}
Retrieves a specific song.

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
  "lineage": ["original"]
}
```

### PUT /songs/{song_id}
Updates a song.

Request:
```json
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
  "lineage": ["original", "updated"]
}
```

### DELETE /songs/{song_id}
Deletes a song.

Response: 204 No Content

## Deployment

### Initial Deployment

1. Deploy the CDK stack:
```bash
cd api/cdk/songs_api
cdk deploy
```

2. Test the deployment:
```bash
./test_api.sh
```

### Updating the API

1. Make your changes to the Lambda code
2. Run tests to ensure everything works
3. Deploy the changes:
```bash
cd api/cdk/songs_api
cdk deploy
```
4. Verify the deployment with `./test_api.sh`

## Error Handling

The API implements comprehensive error handling:

1. **Lambda Handler**:
   - Logs all incoming requests
   - Catches and logs all exceptions
   - Returns appropriate HTTP status codes
   - Provides detailed error messages

2. **Route Handlers**:
   - Specific error handling for each operation
   - DynamoDB client errors are caught and logged
   - Input validation errors are handled
   - Resource not found errors return 404

## Troubleshooting

### Common Issues

1. **Lambda Timeouts**
   - Check CloudWatch logs for the Lambda function
   - Verify DynamoDB table permissions
   - Ensure environment variables are set correctly

2. **Test Failures**
   - Ensure all dependencies are installed
   - Check if pytest and moto are installed
   - Verify Python version (3.8+ required)

3. **CDK Deployment Issues**
   - Check AWS credentials
   - Verify CDK is installed
   - Check CloudFormation stack status

4. **API Gateway Issues**
   - Verify Lambda integration
   - Check method configurations
   - Ensure proper permissions

## Development Workflow

1. Create a new branch for your feature/fix
2. Make your changes
3. Run tests to ensure everything works
4. Create a pull request

## Monitoring and Logging

- CloudWatch Logs for Lambda function
- CloudWatch Metrics for API Gateway
- DynamoDB metrics for table performance

## Security Considerations

- IAM roles are scoped to minimum required permissions
- Environment variables for sensitive configuration
- API Gateway access logging enabled
- Note: Authentication is currently disabled (Cognito integration commented out) 