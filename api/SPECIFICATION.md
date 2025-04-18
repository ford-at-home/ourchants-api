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
The API is configured to accept requests from:
```
http://ourchants-website.s3-website-us-east-1.amazonaws.com
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
  bpm?: string;          // Optional, stored as string for flexibility
  composer?: string;      // Optional
  version?: string;       // Optional
  date?: string;         // Optional, format: "YYYY-MM-DD HH:MM:SS"
  filename?: string;      // Optional
  filepath?: string;      // Optional
  description?: string;   // Optional
  lineage?: string[];    // Optional, defaults to empty array
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
- **Response Body**: Array of song objects
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

## Error Handling

### Error Response Format
```typescript
interface ErrorResponse {
  error: string;    // Error message
  code: string;     // Error code
  details?: any;    // Additional error details (optional)
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
async function updateSongWithRetry(songId: string, song: Song, maxRetries = 3): Promise<Song> {
  let retries = 0;
  
  while (retries < maxRetries) {
    try {
      const response = await fetch(`${API_BASE_URL}/songs/${songId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(song),
      });
      
      if (response.status === 409) {
        retries++;
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retries)));
        continue;
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    } catch (error) {
      if (retries === maxRetries - 1) throw error;
      retries++;
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retries)));
    }
  }
  
  throw new Error('Max retries exceeded');
}
```

### 2. Error Handling
```typescript
async function handleApiError(response: Response) {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }
  return response.json();
}
```

### 3. Type Safety
```typescript
// Use TypeScript interfaces for type safety
interface ApiResponse<T> {
  data?: T;
  error?: ErrorResponse;
}

async function fetchSongs(): Promise<ApiResponse<Song[]>> {
  try {
    const response = await fetch(`${API_BASE_URL}/songs`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: { message: error.message } };
  }
}
```

### 4. React Integration Example
```typescript
import { useState, useEffect } from 'react';

function SongList() {
  const [songs, setSongs] = useState<Song[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSongs() {
      try {
        const response = await fetch(`${API_BASE_URL}/songs`);
        if (!response.ok) throw new Error('Failed to fetch songs');
        const data = await response.json();
        setSongs(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchSongs();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {songs.map(song => (
        <div key={song.song_id}>
          <h2>{song.title}</h2>
          <p>Artist: {song.artist}</p>
          {/* ... other song details ... */}
        </div>
      ))}
    </div>
  );
}
```

## Rate Limits and Quotas
- Default AWS API Gateway limits apply
- 10,000 requests per second per region
- Implement appropriate error handling for throttling (429 responses)

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
- Updated for HTTP API integration 