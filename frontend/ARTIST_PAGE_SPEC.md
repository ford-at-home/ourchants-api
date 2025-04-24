# Artist Page Specification

## Overview
The artist page displays all songs by a specific artist, along with their albums and metadata. This page is accessible via the URL pattern `/artist/:slug` where `:slug` is a URL-friendly version of the artist name.

## API Integration

### Endpoint
```typescript
GET /songs?artist={artistName}&limit={limit}&offset={offset}
```

### Query Parameters
- `artist`: Artist name to filter by (required)
- `limit`: Number of items per page (optional, default: 20, max: 100)
- `offset`: Number of items to skip (optional, default: 0)

### Response Format
```typescript
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  has_more: boolean;
}

interface Song {
  song_id: string;
  title: string;
  artist: string;
  album?: string;
  bpm?: string;
  composer?: string;
  version?: string;
  date?: string;
  filename?: string;
  filepath?: string;
  description?: string;
  lineage?: string[];
  s3_uri?: string;
}
```

## Page Components

### 1. ArtistHeader
- Displays the artist name
- Optional: Artist image/avatar if available
- Optional: Brief artist description if available
- Displays total number of songs by the artist

### 2. AlbumList
- Groups songs by album
- Displays album names in a collapsible list
- Shows song count per album
- Optional: Album artwork if available

### 3. SongList
- Lists all songs by the artist
- Reuses existing SongPlayer component
- Displays:
  - Song title
  - Album name
  - Duration
  - Play/pause controls
  - Optional: Additional metadata (BPM, composer, etc.)

### 4. PaginationControls
- Displays current page number
- Shows total number of pages
- Provides navigation buttons:
  - Previous page
  - Next page
  - First page
  - Last page
- Optional: Page size selector

## URL Structure

### Route Pattern
```
/artist/:slug?page={pageNumber}&limit={pageSize}
```

### URL Generation
- Convert artist name to URL-friendly slug:
  - Convert to lowercase
  - Replace spaces with hyphens
  - Remove special characters
  - Example: "Shipibo Healer" → "shipibo-healer"

### URL Parsing
- Convert slug back to artist name:
  - Replace hyphens with spaces
  - Capitalize words
  - Example: "shipibo-healer" → "Shipibo Healer"

## State Management

### Required State
```typescript
interface ArtistPageState {
  artistName: string;
  songs: Song[];
  albums: {
    [albumName: string]: Song[];
  };
  pagination: {
    currentPage: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
    hasMore: boolean;
  };
  isLoading: boolean;
  error: string | null;
}
```

### Data Flow
1. Extract artist name from URL slug
2. Extract pagination parameters from URL
3. Fetch songs using `GET /songs?artist={artistName}&limit={limit}&offset={offset}`
4. Group songs by album
5. Update state with fetched data
6. Render components

## Error Handling

### Error States
1. Artist not found
2. Network error
3. Invalid URL slug
4. Invalid pagination parameters

### Error UI
- Display user-friendly error messages
- Provide "Back to Home" navigation
- Optional: Suggest similar artist names

## Loading States

### Loading UI
- Show loading spinner while fetching data
- Optional: Skeleton loading for song list
- Optional: Progressive loading for large lists
- Show loading state for pagination controls

## Styling Guidelines

### Colors
- Use existing color scheme
- Maintain consistency with app theme
- Ensure sufficient contrast for accessibility

### Typography
- Artist name: Large, bold
- Album names: Medium, semi-bold
- Song titles: Regular
- Metadata: Small, muted
- Pagination: Small, regular

### Layout
- Responsive design
- Mobile-first approach
- Collapsible sections for better mobile experience
- Pagination controls at bottom of list

## Accessibility

### Requirements
- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance
- Pagination controls accessible via keyboard

## Performance Considerations

### Optimization
- Implement pagination to limit initial load
- Lazy load images
- Cache API responses
- Optimize bundle size
- Prefetch next page data

### Metrics to Track
- Page load time
- Time to interactive
- API response time
- User engagement metrics
- Pagination usage statistics

## Testing Requirements

### Unit Tests
- URL slug generation/parsing
- State management
- Component rendering
- Error handling
- Pagination logic

### Integration Tests
- API integration
- Routing
- State updates
- User interactions
- Pagination navigation

### E2E Tests
- Complete user flows
- Error scenarios
- Loading states
- Mobile responsiveness
- Pagination scenarios

## Implementation Checklist

- [ ] Set up route with React Router
- [ ] Create ArtistHeader component
- [ ] Create AlbumList component
- [ ] Integrate SongPlayer component
- [ ] Create PaginationControls component
- [ ] Implement state management
- [ ] Add error handling
- [ ] Add loading states
- [ ] Style components
- [ ] Add accessibility features
- [ ] Implement performance optimizations
- [ ] Write tests
- [ ] Add analytics tracking

## Example Usage

```typescript
// ArtistPage.tsx
import { useParams, useSearchParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { ArtistHeader, AlbumList, SongList, PaginationControls } from '../components';

const ArtistPage = () => {
  const { slug } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [state, setState] = useState<ArtistPageState>({
    artistName: '',
    songs: [],
    albums: {},
    pagination: {
      currentPage: 1,
      pageSize: 20,
      totalItems: 0,
      totalPages: 0,
      hasMore: false
    },
    isLoading: true,
    error: null
  });

  useEffect(() => {
    const fetchArtistSongs = async () => {
      try {
        const artistName = slugToArtistName(slug);
        const page = parseInt(searchParams.get('page') || '1');
        const limit = parseInt(searchParams.get('limit') || '20');
        const offset = (page - 1) * limit;

        const response = await fetch(
          `/api/songs?artist=${encodeURIComponent(artistName)}&limit=${limit}&offset=${offset}`
        );
        const data = await response.json();
        
        const albums = groupSongsByAlbum(data.items);
        
        setState({
          artistName,
          songs: data.items,
          albums,
          pagination: {
            currentPage: page,
            pageSize: limit,
            totalItems: data.total,
            totalPages: Math.ceil(data.total / limit),
            hasMore: data.has_more
          },
          isLoading: false,
          error: null
        });
      } catch (error) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: 'Failed to load artist data'
        }));
      }
    };

    fetchArtistSongs();
  }, [slug, searchParams]);

  const handlePageChange = (newPage: number) => {
    setSearchParams({ page: newPage.toString() });
  };

  if (state.isLoading) return <LoadingSpinner />;
  if (state.error) return <ErrorMessage message={state.error} />;

  return (
    <div className="artist-page">
      <ArtistHeader 
        name={state.artistName} 
        totalSongs={state.pagination.totalItems} 
      />
      <AlbumList albums={state.albums} />
      <SongList songs={state.songs} />
      <PaginationControls
        currentPage={state.pagination.currentPage}
        totalPages={state.pagination.totalPages}
        onPageChange={handlePageChange}
      />
    </div>
  );
};

export default ArtistPage;
```

## Next Steps

1. Review and approve specification
2. Set up project structure
3. Implement core components
4. Add styling and animations
5. Implement error handling
6. Add tests
7. Deploy and monitor

## Questions?

For any questions or clarifications, please contact the backend team or refer to the API documentation. 