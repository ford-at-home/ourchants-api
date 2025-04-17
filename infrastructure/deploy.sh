#!/bin/bash

# Exit on error
set -e

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

# Get AWS account info
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"

# Set up Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/..

# Bootstrap CDK (if needed)
cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION} 2>/dev/null || true

# Deploy stacks
echo "Deploying Database Stack..."
cdk deploy DatabaseStack --require-approval never --outputs-file database-outputs.json

echo "Deploying API Stack..."
cdk deploy ApiStack --require-approval never --outputs-file api-outputs.json

# Display outputs
echo -e "\nAPI Endpoint:"
cat api-outputs.json | grep -o '"ApiEndpoint": "[^"]*' | cut -d'"' -f4

# Cleanup
rm -f database-outputs.json api-outputs.json 