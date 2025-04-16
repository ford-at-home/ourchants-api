# OurChants API

A serverless REST API for managing song data using AWS Lambda and DynamoDB.

## Overview

OurChants API provides a serverless interface for storing and managing song metadata using DynamoDB as the backend database. The API is built using AWS Lambda and API Gateway, providing a scalable and cost-effective solution.

## Features

- Serverless architecture using AWS Lambda
- RESTful API endpoints via API Gateway
- DynamoDB backend for reliable data storage
- Create, read, update, and delete operations for songs
- Comprehensive test suite with AWS service mocking
- Infrastructure as Code using AWS CDK
- Robust error handling and logging

## API Endpoints

- `GET /songs`: List all songs
- `POST /songs`: Create a new song
- `GET /songs/<song_id>`: Get a specific song
- `PUT /songs/<song_id>`: Update a song
- `DELETE /songs/<song_id>`: Delete a song

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

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ourchants-api.git
   cd ourchants-api
   ```

2. Install dependencies:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Create .env file with:
   DYNAMODB_TABLE_NAME=ourchants-items
   ```

## Deployment

The infrastructure is managed using AWS CDK. To deploy:

1. Install CDK:
   ```bash
   npm install -g aws-cdk
   ```

2. Deploy the stack:
   ```bash
   cd api/cdk/songs_api
   cdk deploy
   ```

3. Test the deployment:
   ```bash
   ./test_api.sh
   ```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development instructions.

## Testing

The project includes a comprehensive test suite using pytest and moto for AWS mocking. Run tests with:
```bash
python -m pytest tests/ -v
```

For continuous test watching during development:
```bash
./watch_tests.sh
```

## Environment Variables

- `DYNAMODB_TABLE_NAME`: Name of the DynamoDB table (default: ourchants-items)

## Maintenance

### Updating the API

1. Make your changes to the Lambda code in `api/lambda/`
2. Run tests to ensure everything works
3. Deploy the changes:
   ```bash
   cd api/cdk/songs_api
   cdk deploy
   ```
4. Verify the deployment with `./test_api.sh`

### Troubleshooting

1. Check CloudWatch logs for the Lambda function
2. Verify DynamoDB table permissions
3. Ensure environment variables are set correctly
4. Check API Gateway configuration

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.