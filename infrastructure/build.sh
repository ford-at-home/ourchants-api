#!/bin/bash
export JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1

# Get absolute paths
INFRA_DIR="$(pwd)"
ROOT_DIR="$(dirname "$INFRA_DIR")"
LAYER_DIR="$INFRA_DIR/layers/python"

echo "=== Starting Build Process ==="

# Create virtual environment for layer
echo "=== Setting up Layer Environment ==="
cd "$LAYER_DIR"
python3.9 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -v

# Create python directory for layer
echo "=== Packaging Layer ==="
mkdir -p python
pip install -r requirements.txt -t python/

# Clean up unnecessary files
find python -type d -name "__pycache__" -exec rm -rf {} +
find python -type d -name "*.dist-info" -exec rm -rf {} +
find python -type d -name "*.egg-info" -exec rm -rf {} +

# Create zip file for layer
echo "=== Creating Layer Package ==="
zip -r layer.zip python/
rm -rf python/

# Return to infrastructure directory
cd "$INFRA_DIR"

# Set up Python environment for CDK
echo "=== Setting up CDK Environment ==="
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -v

# Deploy infrastructure in correct order
echo "=== Deploying Database Stack ==="
cdk deploy DatabaseStack --verbose

echo "=== Deploying API Stack ==="
cdk deploy ApiStack --verbose

echo "=== Build Complete ===" 