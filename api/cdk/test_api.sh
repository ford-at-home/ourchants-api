#!/bin/bash

# Get the API endpoint from CloudFormation stack
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name SongsApiStack \
  --query 'Stacks[0].Outputs[?contains(OutputKey, `SongsApiEndpoint`)].OutputValue' \
  --output text)

if [ -z "$API_ENDPOINT" ]; then
  echo "Error: Could not find API endpoint in CloudFormation stack"
  exit 1
fi

echo "Testing API at: $API_ENDPOINT"

# Test POST /songs
echo -e "\nTesting POST /songs..."
POST_RESPONSE=$(curl -s -X POST "$API_ENDPOINT/songs" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Song", "artist": "Test Artist", "lyrics": "Test lyrics"}')

echo "POST Response: $POST_RESPONSE"
SONG_ID=$(echo $POST_RESPONSE | jq -r '.song_id')
echo "Created song with ID: $SONG_ID"

# Test GET /songs
echo -e "\nTesting GET /songs..."
GET_ALL_RESPONSE=$(curl -s "$API_ENDPOINT/songs")
echo "GET All Response: $GET_ALL_RESPONSE"

# Test GET /songs/{song_id}
echo -e "\nTesting GET /songs/$SONG_ID..."
GET_ONE_RESPONSE=$(curl -s "$API_ENDPOINT/songs/$SONG_ID")
echo "GET One Response: $GET_ONE_RESPONSE"

# Test PUT /songs/{song_id}
echo -e "\nTesting PUT /songs/$SONG_ID..."
PUT_RESPONSE=$(curl -s -X PUT "$API_ENDPOINT/songs/$SONG_ID" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Song", "artist": "Updated Artist", "lyrics": "Updated lyrics"}')
echo "PUT Response: $PUT_RESPONSE"

# Test DELETE /songs/{song_id}
echo -e "\nTesting DELETE /songs/$SONG_ID..."
DELETE_RESPONSE=$(curl -s -X DELETE "$API_ENDPOINT/songs/$SONG_ID")
echo "DELETE Response: $DELETE_RESPONSE"

# Verify the song was deleted
echo -e "\nVerifying deletion..."
GET_AFTER_DELETE=$(curl -s "$API_ENDPOINT/songs/$SONG_ID")
echo "GET After Delete Response: $GET_AFTER_DELETE"

# Get Lambda function name and logs
echo -e "\nFetching Lambda logs..."

# Get the Lambda function name from CloudFormation
LAMBDA_FUNCTION=$(aws cloudformation describe-stack-resources \
  --stack-name SongsApiStack \
  --query "StackResources[?ResourceType=='AWS::Lambda::Function'].PhysicalResourceId" \
  --output text)

if [ -z "$LAMBDA_FUNCTION" ]; then
  echo "Error: Could not find Lambda function in stack"
  exit 1
fi

echo "Lambda function: $LAMBDA_FUNCTION"

# Get the log group name
LOG_GROUP="/aws/lambda/$LAMBDA_FUNCTION"
echo "Log group: $LOG_GROUP"

# Get the most recent log streams
echo -e "\nMost recent logs:"
aws logs get-log-events \
  --log-group-name "$LOG_GROUP" \
  --log-stream-name $(aws logs describe-log-streams \
    --log-group-name "$LOG_GROUP" \
    --order-by LastEventTime \
    --descending \
    --limit 1 \
    --query 'logStreams[0].logStreamName' \
    --output text) \
  --limit 20 \
  --query 'events[*].message' \
  --output text

echo -e "\nTests completed!" 