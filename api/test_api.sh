#!/bin/bash

# Test runner script for the Songs API
# This script runs the test suite with coverage reporting
# Usage:
#   ./test_api.sh              # Run unit tests only
#   ./test_api.sh --integration # Run both unit and integration tests
# The script automatically handles test configuration and coverage reporting

# Default to running unit tests only
TEST_COMMAND="python -m pytest tests/ -v --cov=app --cov-report=term-missing"

# Check if integration tests should be run
if [ "$1" == "--integration" ]; then
    TEST_COMMAND="$TEST_COMMAND -m integration"
    echo "Running integration tests..."
else
    echo "Running unit tests only..."
fi

# Run the tests
eval $TEST_COMMAND 