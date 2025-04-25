# Testing Guide for OurChants API

## Common Issues and Solutions

### 1. DynamoDB Type Formatting Issues

#### Problem
When testing with `moto` (AWS mocking library), we encountered type mismatch errors:
```
Type mismatch for key song_id expected: S actual: M
```

This happened because:
- The test data was being formatted incorrectly for DynamoDB
- The `song_id` field was being wrapped in multiple layers of type descriptors
- The mock DynamoDB table expected a simple string type for `song_id`

#### Solution
We simplified the data handling by:
1. Removing the manual `_format_for_dynamodb` function
2. Using Marshmallow schemas to handle data validation and formatting
3. Letting the DynamoDB SDK handle type conversion automatically

The key changes were:
```python
# Before (problematic):
def _format_for_dynamodb(self, data):
    formatted = {}
    for key, value in data.items():
        if key == 'song_id':
            formatted[key] = {"S": str(value)}
        # ... more complex type handling

# After (simplified):
def create_song(self, song_data):
    validated_data = song_schema.load(song_data)
    validated_data['song_id'] = str(uuid4())
    self.table.put_item(Item=validated_data)
    return song_schema.dump(validated_data)
```

### 2. Mock AWS Environment Setup

#### Problem
Tests were failing because:
- The mock DynamoDB table wasn't being created properly
- Multiple mocking approaches were conflicting (`@mock_aws` decorator and fixture)

#### Solution
We standardized on using a single mocking approach:
1. Created a `mock_dynamodb` fixture in `conftest.py`
2. Removed all `@mock_aws` decorators from test functions
3. Ensured the fixture creates the table with the correct schema

Example fixture:
```python
@pytest.fixture
def mock_dynamodb():
    with mock_aws():
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName='test-songs-table',
            KeySchema=[{'AttributeName': 'song_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'song_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        yield table
```

### 3. Test Data Management

#### Problem
Test data was inconsistent and hard to maintain:
- Different formats in different tests
- Manual DynamoDB type formatting
- Inconsistent field values

#### Solution
We created a standardized test data fixture:
```python
@pytest.fixture
def test_song():
    return {
        'song_id': 'test-song-id',
        'title': 'Test Song',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'bpm': '120',
        'composer': 'Test Composer',
        'version': 'Test Version',
        'date': '2024-03-20 12:00:00',
        'filename': 'test_song.mp3',
        'filepath': 'Media/test_song.mp3',
        'description': 'Test description',
        'lineage': [],
        's3_uri': 's3://ourchants-songs/test_song.mp3'
    }
```

### 4. Best Practices for Future Testing

1. **Use Schemas for Data Validation**
   - Let Marshmallow handle data validation and formatting
   - Avoid manual type conversion for DynamoDB

2. **Standardize Mock Setup**
   - Use a single mocking approach (fixtures over decorators)
   - Create mock resources in `conftest.py`
   - Ensure mock resources match production schema

3. **Test Data Management**
   - Use fixtures for test data
   - Keep test data consistent across tests
   - Document test data structure

4. **Error Handling**
   - Test both success and failure cases
   - Verify error messages and types
   - Handle edge cases (empty lists, missing fields, etc.)

5. **Clean Up**
   - Remove unused code
   - Keep tests focused and simple
   - Document test purpose and assumptions

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/api/test_core.py

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s
```

## Common Test Patterns

### Testing CRUD Operations
```python
def test_create_song(mock_dynamodb, test_song):
    api = SongsApi(mock_dynamodb)
    song = api.create_song(test_song)
    assert song['title'] == test_song['title']
    assert song['artist'] == test_song['artist']

def test_get_song(mock_dynamodb, test_song):
    api = SongsApi(mock_dynamodb)
    created = api.create_song(test_song)
    song = api.get_song(created['song_id'])
    assert song['title'] == test_song['title']
```

### Testing Error Cases
```python
def test_create_song_missing_required(mock_dynamodb):
    api = SongsApi(mock_dynamodb)
    with pytest.raises(ValidationError):
        api.create_song({})
```

### Testing Pagination
```python
def test_list_songs_pagination(mock_dynamodb, test_song):
    api = SongsApi(mock_dynamodb)
    api.create_song(test_song)
    result = api.list_songs(limit=1, offset=0)
    assert len(result['items']) == 1
    assert result['has_more'] == False
``` 