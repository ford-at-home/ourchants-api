# OurChants API Specification

## Storage Components

### DynamoDB Table
- **Table Name**: `songs`
- **Primary Key**: `song_id` (String)
- **Attributes**:
  - `title` (String, required)
  - `artist` (String, required)
  - `album` (String, optional)
  - `bpm` (String, optional)
  - `composer` (String, optional)
  - `version` (String, optional)
  - `date` (String, optional)
  - `filename` (String, optional)
  - `filepath` (String, optional)
  - `description` (String, optional)
  - `lineage` (List of Strings, optional)
  - `s3_uri` (String, optional)

### S3 Bucket
- **Bucket Name**: `ourchants-songs`
- **File Organization**: `songs/{song_id}/{filename}`
- **Supported Formats**: MP3, M4A
- **Access Control**: Private with pre-signed URLs
- **URL Expiration**: 1 hour (3600 seconds)

## API Endpoints

### List Songs
- **Endpoint**: `GET /songs`
- **Query Parameters**:
  - `artist_filter` (optional): Filter songs by artist name
  - `limit` (optional, default: 20): Number of items per page (1-100)
  - `offset` (optional, default: 0): Number of items to skip
- **Response**:
  ```json
  {
    "items": [
      {
        "song_id": "string",
        "title": "string",
        "artist": "string",
        "album": "string",
        "bpm": "string",
        "composer": "string",
        "version": "string",
        "date": "string",
        "filename": "string",
        "filepath": "string",
        "description": "string",
        "lineage": ["string"],
        "s3_uri": "string"
      }
    ],
    "total": 0,
    "has_more": false
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Invalid pagination parameters
    ```json
    {
      "error": "Invalid limit parameter",
      "details": "limit must be between 1 and 100",
      "code": "INVALID_LIMIT"
    }
    ```
  - 400 Bad Request: Invalid offset parameter
    ```json
    {
      "error": "Invalid offset parameter",
      "details": "offset must be non-negative",
      "code": "INVALID_OFFSET"
    }
    ```

### Create Song
- **Endpoint**: `POST /songs`
- **Request Body**:
  ```json
  {
    "title": "string",
    "artist": "string",
    "album": "string",
    "bpm": "string",
    "composer": "string",
    "version": "string",
    "date": "string",
    "filename": "string",
    "filepath": "string",
    "description": "string",
    "lineage": ["string"],
    "s3_uri": "string"
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "song_id": "string",
    "title": "string",
    "artist": "string",
    "album": "string",
    "bpm": "string",
    "composer": "string",
    "version": "string",
    "date": "string",
    "filename": "string",
    "filepath": "string",
    "description": "string",
    "lineage": ["string"],
    "s3_uri": "string"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Validation error
    ```json
    {
      "error": {
        "field_name": ["error message"]
      }
    }
    ```

### Get Song
- **Endpoint**: `GET /songs/{song_id}`
- **Response**: 200 OK
  ```json
  {
    "song_id": "string",
    "title": "string",
    "artist": "string",
    "album": "string",
    "bpm": "string",
    "composer": "string",
    "version": "string",
    "date": "string",
    "filename": "string",
    "filepath": "string",
    "description": "string",
    "lineage": ["string"],
    "s3_uri": "string"
  }
  ```
- **Error Responses**:
  - 404 Not Found: Song not found
    ```json
    {
      "error": "Song not found"
    }
    ```

### Update Song
- **Endpoint**: `PUT /songs/{song_id}`
- **Request Body**:
  ```json
  {
    "title": "string",
    "artist": "string",
    "album": "string",
    "bpm": "string",
    "composer": "string",
    "version": "string",
    "date": "string",
    "filename": "string",
    "filepath": "string",
    "description": "string",
    "lineage": ["string"],
    "s3_uri": "string"
  }
  ```
- **Response**: 200 OK
  ```json
  {
    "song_id": "string",
    "title": "string",
    "artist": "string",
    "album": "string",
    "bpm": "string",
    "composer": "string",
    "version": "string",
    "date": "string",
    "filename": "string",
    "filepath": "string",
    "description": "string",
    "lineage": ["string"],
    "s3_uri": "string"
  }
  ```
- **Error Responses**:
  - 404 Not Found: Song not found
    ```json
    {
      "error": "Song not found"
    }
    ```
  - 400 Bad Request: Validation error
    ```json
    {
      "error": {
        "field_name": ["error message"]
      }
    }
    ```

### Delete Song
- **Endpoint**: `DELETE /songs/{song_id}`
- **Response**: 204 No Content
- **Error Responses**: None (idempotent)

### Pre-signed URL Generation
- **Endpoint**: `POST /presigned-url`
- **Request Body**:
  ```json
  {
    "bucket": "string",
    "key": "string"
  }
  ```
- **Response**: 200 OK
  ```json
  {
    "url": "string",
    "expiresIn": 3600
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Invalid request body
    ```json
    {
      "error": "Invalid request body",
      "code": "INVALID_REQUEST"
    }
    ```
  - 400 Bad Request: Invalid object key
    ```json
    {
      "error": "Invalid object key",
      "details": "Object key cannot be empty",
      "code": "INVALID_OBJECT_KEY"
    }
    ```
  - 400 Bad Request: Invalid bucket name
    ```json
    {
      "error": "Invalid bucket name",
      "details": "Bucket name must be between 3 and 63 characters long",
      "code": "INVALID_BUCKET_NAME"
    }
    ```
  - 404 Not Found: Bucket not found
    ```json
    {
      "error": "Bucket {bucket} not found",
      "details": "The specified S3 bucket does not exist",
      "code": "BUCKET_NOT_FOUND"
    }
    ```
  - 404 Not Found: Object not found
    ```json
    {
      "error": "Object {key} not found in bucket {bucket}",
      "details": "The specified S3 object does not exist in the bucket",
      "code": "OBJECT_NOT_FOUND"
    }
    ```

## Error Codes
- `INVALID_REQUEST`: Invalid request format or missing required fields
- `INVALID_PAGINATION`: Invalid pagination parameters
- `INVALID_LIMIT`: Limit parameter out of range (1-100)
- `INVALID_OFFSET`: Offset parameter is negative
- `INVALID_BUCKET_NAME`: Invalid S3 bucket name
- `INVALID_OBJECT_KEY`: Invalid S3 object key
- `BUCKET_NOT_FOUND`: Specified bucket doesn't exist or access denied
- `OBJECT_NOT_FOUND`: Specified object doesn't exist in bucket
- `INTERNAL_ERROR`: Unexpected server error

## CORS Headers
All endpoints include the following CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
Access-Control-Allow-Headers: Content-Type
``` 