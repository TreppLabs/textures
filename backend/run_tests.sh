#!/bin/bash
# Simple test runner script for backend tests

cd "$(dirname "$0")"

echo "Running backend tests..."
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed"
    echo "Please install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Run tests with coverage
pytest tests/ -v --tb=short

echo ""
echo "Tests completed!"

