# OurChants API Specification

## Overview
The OurChants API provides a RESTful interface for managing song data in the OurChants application. This document outlines the API endpoints, request/response formats, error handling, and integration guidelines for frontend developers.

## Base URL
```
https://{api_id}.execute-api.{region}.amazonaws.com
```

## Authentication
Currently, the API is publicly accessible. Future versions will implement authentication using AWS Cognito or API keys.

## CORS Configuration
The API is configured to accept requests from any origin:
```
Access-Control-Allow-Origin: *
```

Allowed methods: GET, POST, PUT, DELETE
Allowed headers: Content-Type, Accept
Max age: 3000 seconds

## Data Models

### Song Object
```typescript
interface Song {
  song_id?: string;       // UUID, auto-generated
  title: string;          // Required
  artist: string;         // Required
  album?: string;         // Optional
  genre?: string;         // Optional
  composer?: string;      // Optional
  version?: string;       // Optional
  date?: string;         // Optional, format: "YYYY-MM-DD HH:MM:SS"
  filename?: string;      // Optional
  filepath?: string;      // Optional
  description?: string;   // Optional
  lineage?: string[];    // Optional, defaults to empty array
  s3_uri?: string;       // Optional, S3 URI of the audio file
  duration?: string;     // Optional, duration in seconds
}

### Pre-signed URL Request
```typescript
interface PresignedUrlRequest {
  bucket?: string;  // Optional, defaults to configured bucket
  key: string;      // Required, S3 object key
}
```

### Pre-signed URL Response
```typescript
interface PresignedUrlResponse {
  url: string;      // Pre-signed URL for the S3 object
  expiresIn: number // Expiration time in seconds
}
```

## Endpoints

### 1. Create Song
- **Method**: POST
- **Path**: `/songs`
- **Request Body**: Song object (without song_id)
- **Response**: 201 Created
- **Response Body**: Complete song object with generated song_id
- **Example Request**:
```typescript
const newSong = {
  title: "Amazing Grace",
  artist: "John Newton",
  album: "Hymnal Volume 1",
  bpm: "70",
  composer: "John Newton",
  version: "1.0",
  date: "2024-04-17 08:46:12",
  filename: "amazing_grace.mp3",
  filepath: "Media/amazing_grace.mp3",
  description: "Traditional hymn",
  lineage: ["original"]
};

const response = await fetch(`${API_BASE_URL}/songs`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(newSong),
});
```

### 2. Get Song
- **Method**: GET
- **Path**: `/songs/{song_id}`
- **Response**: 200 OK
- **Response Body**: Complete song object
- **Error**: 404 Not Found if song_id doesn't exist
- **Example**:
```typescript
const response = await fetch(`${API_BASE_URL}/songs/${songId}`);
const song = await response.json();
```

### 3. List Songs
- **Method**: GET
- **Path**: `/songs`
- **Response**: 200 OK
- **Response Body**: Array of song objects that have an s3_uri attribute
- **Note**: Only songs with an s3_uri attribute will be returned in the list
- **Example**:
```typescript
const response = await fetch(`${API_BASE_URL}/songs`);
const songs = await response.json();
```

### 4. Update Song
- **Method**: PUT
- **Path**: `/songs/{song_id}`
- **Request Body**: Song object (without song_id)
- **Response**: 200 OK
- **Response Body**: Updated song object
- **Error**: 404 Not Found if song_id doesn't exist
- **Example**:
```typescript
const updatedSong = {
  title: "Updated Amazing Grace",
  artist: "John Newton",
  // ... other fields
};

const response = await fetch(`${API_BASE_URL}/songs/${songId}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(updatedSong),
});
```

### 5. Delete Song
- **Method**: DELETE
- **Path**: `/songs/{song_id}`
- **Response**: 204 No Content
- **Error**: 404 Not Found if song_id doesn't exist
- **Example**:
```typescript
const response = await fetch(`${API_BASE_URL}/songs/${songId}`, {
  method: 'DELETE',
});
```

### 6. Generate Pre-signed URL
- **Method**: POST
- **Path**: `/presigned-url`
- **Request Body**: Pre-signed URL Request object
- **Response**: 200 OK
- **Response Body**: Pre-signed URL Response object
- **Error Responses**:
  - 400 Bad Request:
    ```json
    {
      "error": "Invalid bucket name",
      "details": "Bucket name must be between 3 and 63 characters long",
      "code": "INVALID_BUCKET_NAME"
    }
    ```
    ```json
    {
      "error": "Invalid object key",
      "details": "Object key cannot exceed 1024 characters",
      "code": "INVALID_OBJECT_KEY"
    }
    ```
  - 404 Not Found:
    ```json
    {
      "error": "Bucket ourchants-songs not found",
      "details": "The specified S3 bucket does not exist",
      "code": "BUCKET_NOT_FOUND"
    }
    ```
    ```json
    {
      "error": "Object song.mp3 not found in bucket ourchants-songs",
      "details": "The specified S3 object does not exist in the bucket",
      "code": "OBJECT_NOT_FOUND"
    }
    ```
  - 500 Internal Server Error:
    ```json
    {
      "error": "Failed to generate pre-signed URL",
      "details": "An error occurred while generating the pre-signed URL",
      "code": "INTERNAL_ERROR"
    }
    ```
- **CORS Headers**:
  ```
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: OPTIONS,POST
  Access-Control-Allow-Headers: Content-Type
  ```
- **Rate Limits**:
  - Maximum 3 retry attempts for S3 operations
  - 5-second timeout for S3 connections
  - 5-second timeout for S3 read operations
- **Example**:
```typescript
const response = await fetch(`${API_BASE_URL}/presigned-url`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    bucket: "ourchants-songs",
    key: "songs/amazing_grace.mp3"
  }),
});
const { url, expiresIn } = await response.json();
```

## Error Handling

### Error Response Format
```typescript
interface ErrorResponse {
  error: string;    // Error message
  code: string;     // Error code
}
```

### Common Error Codes
- **400 Bad Request**: Invalid request body or parameters
- **404 Not Found**: Resource not found
- **409 Conflict**: Concurrent update conflict
- **500 Internal Server Error**: Server-side error

## Best Practices

### 1. Concurrent Operations
```typescript
// Example of handling concurrent updates
const response = await fetch(`${API_BASE_URL}/songs/${songId}`);
const song = await response.json();

// Make changes
song.title = "Updated Title";

// Update with optimistic locking
const updateResponse = await fetch(`${API_BASE_URL}/songs/${songId}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(song),
});

if (updateResponse.status === 409) {
  // Handle conflict
  console.log("Song was modified by another user");
}
```

### 2. Audio Playback
```typescript
// Example of using pre-signed URLs for audio playback
async function getAudioUrl(song: Song) {
  // Extract bucket and key from S3 URI
  const s3Uri = song.s3_uri;
  if (!s3Uri) return null;
  
  const [bucket, ...keyParts] = s3Uri.replace('s3://', '').split('/');
  const key = keyParts.join('/');
  
  // Get pre-signed URL
  const response = await fetch(`${API_BASE_URL}/presigned-url`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ bucket, key }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to get pre-signed URL');
  }
  
  const { url, expiresIn } = await response.json();
  return url;
}

// Usage in audio player component
const audioUrl = await getAudioUrl(song);
if (audioUrl) {
  audioPlayer.src = audioUrl;
}
```

## Rate Limits and Quotas
The API uses AWS API Gateway's default limits:
- 10,000 requests per second per region
- Implement appropriate error handling for throttling (429 responses)

Note: These are AWS-imposed limits and may vary based on your AWS account type and region.

## Future Enhancements
1. Authentication and authorization
2. Pagination for list endpoint
3. Search and filter capabilities
4. File upload integration
5. Versioning support

## Support
For API support or to report issues, please contact the API team or create an issue in the repository.

## Changelog
- **2024-04-17**: Initial API specification
- Added full schema support for all song fields
- Implemented concurrent operation handling
- Added detailed error responses
- Added pre-signed URL endpoint for audio playback 