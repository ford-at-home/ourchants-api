#!/bin/bash

# Exit on error and print commands as they are executed
set -ex

echo "=== Starting deployment process ==="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "=== Creating virtual environment ==="
    python3 -m venv venv
fi

echo "=== Activating virtual environment ==="
source venv/bin/activate

# Print Python version and environment info
echo "=== Python Environment Info ==="
which python3
python3 --version
pip --version

# Install dependencies with verbose output
echo "=== Installing dependencies ==="
pip install -v -r requirements.txt

# Get AWS account info
echo "=== Getting AWS account info ==="
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"  # or get from AWS_DEFAULT_REGION env var
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "AWS Region: ${AWS_REGION}"

# Set up Python path to find infrastructure module
echo "=== Setting up Python path ==="
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
echo "PYTHONPATH: $PYTHONPATH"

# Bootstrap CDK with verbose output
echo "=== Bootstrapping CDK ==="
cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION} --verbose

# Deploy Database Stack first with verbose output
echo "=== Deploying Database Stack ==="
echo "Synthesizing Database Stack..."
cdk synth DatabaseStack --verbose
echo "Deploying Database Stack..."
cdk deploy DatabaseStack --require-approval never --verbose
echo "=== Database Stack deployed! ==="

# Print Database Stack outputs
echo "=== Database Stack outputs ==="
aws cloudformation describe-stacks --stack-name DatabaseStack --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table

# Deploy API Stack with verbose output
echo "=== Deploying API Stack ==="
echo "Synthesizing API Stack..."
cdk synth ApiStack --verbose
echo "Deploying API Stack..."
cdk deploy ApiStack --require-approval never --verbose
echo "=== API Stack deployed! ==="

# Print API Stack outputs
echo "=== API Stack outputs ==="
aws cloudformation describe-stacks --stack-name ApiStack --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table

echo "=== All stacks deployed successfully! ==="
echo "Deployment completed at: $(date)" 