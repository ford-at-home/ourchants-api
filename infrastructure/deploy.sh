#!/bin/bash
set -ex

export JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1

# ===== Path Setup =====
# Get the absolute path of the infrastructure directory
INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$INFRA_DIR")"

echo "=== Directory Structure ==="
echo "Root Directory: $ROOT_DIR"
echo "Infrastructure Directory: $INFRA_DIR"

# ===== Environment Setup =====
# Set up Python path to include both root and infrastructure directories
export PYTHONPATH="$ROOT_DIR:$INFRA_DIR:$PYTHONPATH"
echo "PYTHONPATH: $PYTHONPATH"

# ===== Virtual Environment =====
VENV_DIR="$INFRA_DIR/.venv"
echo "=== Setting up Virtual Environment ==="
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# ===== Dependencies =====
echo "=== Installing Dependencies ==="
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies from root requirements.txt
pip install -r "$ROOT_DIR/requirements.txt" -v

# ===== AWS Configuration =====
echo "=== AWS Configuration ==="
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-east-1")
echo "Account ID: ${AWS_ACCOUNT_ID}"
echo "Region: ${AWS_REGION}"

# ===== CDK Bootstrap =====
echo "=== Bootstrapping CDK ==="
cd "$INFRA_DIR"
cdk bootstrap "aws://${AWS_ACCOUNT_ID}/${AWS_REGION}" --verbose

# ===== Deployment =====
echo "=== Deploying Stacks ==="

# Deploy Database Stack
echo "=== Deploying Database Stack ==="
cdk deploy DatabaseStack --require-approval never -v

# Deploy API Stack
echo "=== Deploying API Stack ==="
cdk deploy ApiStack --require-approval never -v

# ===== Verification =====
echo "=== Verifying Deployment ==="
cdk synth

echo "=== Deployment Complete ==="
echo "Timestamp: $(date)"
echo "Working Directory: $(pwd)"
echo "Python Path: $PYTHONPATH"

# Silence JSII warnings about Node.js version
export JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1 