# Scripts Directory

This directory contains utility scripts for managing and maintaining the OurChants API.

## DynamoDB Management Scripts

### `fix_dynamodb_schema.py`
Main script for maintaining DynamoDB data consistency. It:
- Ensures proper type handling for all fields
- Maintains the lineage field as a list type
- Handles the SDK's representation format correctly
- Updates items in batches with proper error handling

### `verify_schema_fix.py`
Verification script that analyzes the current state of DynamoDB data. It:
- Checks field type distributions
- Verifies proper DynamoDB type usage
- Identifies any problematic patterns
- Reports on data consistency

### `count_items.py`
Simple utility to count items in the DynamoDB table.

## S3 Management Scripts

### `update_s3_uris.py`
Updates S3 URIs in the DynamoDB table. It:
- Generates proper S3 URIs for song files
- Updates the s3_uri field in DynamoDB
- Handles batch updates with error recovery

## AWS Lambda Management

### `get_lambda_logs.py`
Utility for retrieving and analyzing Lambda function logs. It:
- Fetches logs for specific Lambda functions
- Filters logs by time range
- Formats log output for readability

## Usage

All scripts should be run from the project root directory:

```bash
python3 scripts/<script_name>.py
```

## Important Notes

1. **DynamoDB Data Representation**:
   - The AWS SDK wraps all values in type descriptors (S, N, L, M, etc.)
   - This is normal and should not be "fixed" or simplified
   - The M->S->S pattern in responses is just the SDK's way of representing data

2. **Best Practices**:
   - Always use the SDK's type system
   - Don't try to manipulate the SDK's representation
   - Use proper extraction and formatting methods

3. **Error Handling**:
   - All scripts include proper error handling
   - Failed operations are logged for debugging
   - Batch operations continue even if some items fail

## Dependencies

These scripts require:
- Python 3.8+
- boto3
- AWS credentials configured
- Appropriate IAM permissions

## See Also

- [DynamoDB Documentation](../docs/dynamodb.md)
- [API Specification](../SPECIFICATION.md)
- [Development Guide](../DEVELOPMENT.md) 