#!/bin/bash

# Basic test runner for the Songs API
# This script runs the test suite with coverage reporting
# It's used by watch_tests.sh for continuous testing during development
# Usage: ./run_tests.sh

# Run tests with coverage
python3 -m coverage run -m pytest tests/ -v
python3 -m coverage report 