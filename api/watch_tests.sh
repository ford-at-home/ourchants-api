#!/bin/bash

# Development test watcher for the Songs API
# This script watches for changes in Python files and automatically runs tests
# It uses entr to monitor file changes and run_tests.sh to execute the tests
# Usage: ./watch_tests.sh

# Watch Python files and run tests when they change
find . -name "*.py" | entr -c ./run_tests.sh 