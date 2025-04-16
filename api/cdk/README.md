# API Integration Tests

This directory contains the CDK infrastructure for the Songs API. After deploying the CDK stack, you can run integration tests to verify the API is working correctly.

## Running Integration Tests

From the `api/cdk` directory, run:
```bash
./test_api.sh
```

The script will automatically:
1. Get the current API URL from the CDK outputs
2. Run the integration tests against the deployed API

## Understanding the Test Output

The integration test performs a complete CRUD (Create, Read, Update, Delete) cycle on the API. Here's what to expect in the output:

1. **API Endpoint**: Shows the deployed API Gateway URL
   ```
   Testing API at: https://<your-api-url>.execute-api.us-east-1.amazonaws.com/prod/
   ```

2. **Create (POST)**: Creates a new song and shows the response
   ```
   Testing POST /songs...
   POST Response: {"title": "Test Song", "artist": "Test Artist", ...}
   Created song with ID: 22ee6e13-db49-44d6-b71f-f402d597739b
   ```

3. **Read All (GET)**: Lists all songs in the database
   ```
   Testing GET /songs...
   GET All Response: [{"artist": "Test Artist", ...}]
   ```

4. **Read One (GET)**: Retrieves the specific song we created
   ```
   Testing GET /songs/22ee6e13-db49-44d6-b71f-f402d597739b...
   GET One Response: {"artist": "Test Artist", ...}
   ```

5. **Update (PUT)**: Modifies the song and shows the updated data
   ```
   Testing PUT /songs/22ee6e13-db49-44d6-b71f-f402d597739b...
   PUT Response: {"artist": "Updated Artist", ...}
   ```

6. **Delete (DELETE)**: Removes the song and verifies it's gone
   ```
   Testing DELETE /songs/22ee6e13-db49-44d6-b71f-f402d597739b...
   DELETE Response: 
   Verifying deletion...
   GET After Delete Response: {"error": "Song not found"}
   ```

7. **Lambda Logs**: Shows the execution logs from the Lambda function
   ```
   Fetching Lambda logs...
   Lambda function: SongsApiStack-SongsLambda1C3C9254-nhDHDgl3DLAh
   Log group: /aws/lambda/SongsApiStack-SongsLambda1C3C9254-nhDHDgl3DLAh
   ```

## Troubleshooting

If the tests fail:
1. Check that the Lambda function has proper permissions
2. Look at the Lambda logs for any errors
3. Ensure the DynamoDB table exists and is accessible

## Notes

- The tests use a unique song ID for each run to avoid conflicts
- All test data is cleaned up after the tests complete
- The Lambda logs show execution times and memory usage, which can help identify performance issues 