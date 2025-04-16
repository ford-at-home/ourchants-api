#!/bin/bash

# Test watcher for the Songs API
# This script watches for changes in Python files and runs tests automatically
# Usage: ./watch_tests.sh

# Install test dependencies
pip install -r requirements-test.txt

# Watch for changes and run tests
ptw --runner "coverage run -m pytest tests/api -v && coverage report --include='src/api/*'" 