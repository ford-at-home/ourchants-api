## Storage Components

### DynamoDB Table
- **Table Name**: `songs`
- **Primary Key**: `song_id` (String)
- **Attributes**:
  - `title` (String)
  - `artist` (String)
  - `album` (String)
  - `bpm` (String)
  - `composer` (String)
  - `version` (String)
  - `date` (String)
  - `filename` (String)
  - `filepath` (String)
  - `description` (String)
  - `lineage` (List of Strings)

### S3 Bucket
- **Bucket Name**: `ourchants-songs`
- **File Organization**: `songs/{song_id}/{filename}`
- **Supported Formats**: MP3, M4A
- **Access Control**: Private with pre-signed URLs
- **URL Expiration**: 1 hour (3600 seconds)

## API Endpoints

### Pre-signed URL Generation
- **Endpoint**: `POST /presigned-url`
- **Request Body**:
  ```json
  {
    "bucket": "string",
    "key": "string"
  }
  ```
- **Response**:
  ```json
  {
    "url": "string",
    "expiresIn": 3600
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing required fields
  - 404 Not Found: Bucket not found or access denied
  - 404 Not Found: Object not found

## Error Codes
- `MISSING_REQUIRED_FIELD`: Required field is missing in request
- `BUCKET_NOT_FOUND`: Specified bucket doesn't exist or access denied
- `OBJECT_NOT_FOUND`: Specified object doesn't exist in bucket 