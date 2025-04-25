# DynamoDB Schema and Data Representation

## Important Notes About DynamoDB Data Representation

### SDK vs AWS Console Representation
DynamoDB data can appear differently depending on how you view it:

1. **AWS Console View**:
   - Shows data in a simplified, human-readable format
   - Doesn't show the underlying type information
   - Example: `"title": "Song Name"`

2. **SDK Response Format**:
   - Every value is wrapped in a type descriptor
   - Uses a specific format to represent DynamoDB types
   - Example: `"title": { "S": "Song Name" }`

### Common Confusion Points
1. **M->S->S Pattern**:
   - When viewing SDK responses, you might see nested structures like:
     ```json
     {
       "M": {
         "S": {
           "S": "value"
         }
       }
     }
     ```
   - This is NOT how the data is actually stored in DynamoDB
   - It's just the SDK's way of representing a simple string value
   - Don't try to "fix" this pattern - it's normal SDK behavior

2. **Type Descriptors**:
   - `S`: String
   - `N`: Number
   - `L`: List
   - `M`: Map
   - `BOOL`: Boolean
   - `NULL`: Null value

## Songs Table Schema

### Primary Key
- `song_id` (String): Unique identifier for each song

### Required Fields
- `title` (String): Song title
- `artist` (String): Artist name
- `s3_uri` (String): S3 location of the song file
- `filename` (String): Original filename
- `filepath` (String): Local file path
- `duration` (String): Song duration in seconds

### Optional Fields
- `lineage` (List): List of lineage information
- `composer` (String): Song composer
- `album` (String): Album name
- `year` (String): Release year
- `genre` (String): Music genre
- `bpm` (String): Beats per minute
- `track_number` (String): Track number
- `s3_key` (String): S3 object key
- `date_added` (String): Date when the song was added
- `encoded_by` (String): Software used for encoding
- `version` (String): Version information
- `date` (String): Additional date field
- `description` (String): Song description
- `disc_number` (String): Disc number

## Working with DynamoDB Data

### Best Practices
1. **Always use the SDK's type system**:
   - Don't try to manipulate the SDK's representation format
   - Use the provided type descriptors (S, N, L, M, etc.)

2. **When reading data**:
   - Expect the SDK's wrapped format
   - Use proper extraction methods to get the actual values

3. **When writing data**:
   - Always wrap values in the appropriate type descriptor
   - Don't try to "simplify" the structure

### Common Pitfalls
1. **Don't be confused by the SDK's representation**:
   - The nested M->S->S pattern is normal
   - It doesn't indicate a problem with your data

2. **Don't try to "fix" the SDK format**:
   - The format is intentional and necessary
   - Attempting to simplify it can cause issues

3. **Be careful with type conversion**:
   - Always use the proper DynamoDB types
   - Don't assume string values can be numbers or vice versa

## Example Data Representations

### AWS Console View
```json
{
  "song_id": "123",
  "title": "Song Name",
  "artist": "Artist Name",
  "duration": "180"
}
```

### SDK Response Format
```json
{
  "song_id": { "S": "123" },
  "title": { "S": "Song Name" },
  "artist": { "S": "Artist Name" },
  "duration": { "S": "180" }
}
```

### List Example (lineage field)
```json
{
  "lineage": {
    "L": [
      { "S": "value1" },
      { "S": "value2" }
    ]
  }
}
```

## Tools and Scripts

### Schema Fix Script
The `scripts/fix_dynamodb_schema.py` script helps maintain data consistency by:
1. Properly handling the SDK's representation format
2. Ensuring all fields use the correct DynamoDB types
3. Maintaining the lineage field as a proper list type

### Verification Script
The `scripts/verify_schema_fix.py` script helps verify data consistency by:
1. Analyzing the type structure of all fields
2. Checking for proper DynamoDB type usage
3. Identifying any problematic patterns

## Additional Resources
- [DynamoDB Data Types](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.NamingRulesDataTypes.html)
- [AWS SDK for Python (Boto3) DynamoDB Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html) 