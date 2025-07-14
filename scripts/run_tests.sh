#!/bin/bash

# Script to run tests with proper database setup

set -e  # Exit on error

echo "Building test image..."
docker-compose -f docker-compose.test.yml build test-runner

echo "Starting test environment..."
docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test-runner

# Store exit code
TEST_EXIT_CODE=$?

# Cleanup
echo "Cleaning up test environment..."
docker-compose -f docker-compose.test.yml down -v

exit $TEST_EXIT_CODE