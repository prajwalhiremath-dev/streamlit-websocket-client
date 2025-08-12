#!/bin/bash

# Build script for streamlit-websocket-client
# This script builds both the frontend and creates the Python package

echo "Building streamlit-websocket-client..."

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install Node.js and npm."
    exit 1
fi

# Build frontend
echo "Building frontend..."
cd streamlit_websocket_client/frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# Build production bundle
echo "Creating production build..."
npm run build

# Go back to root
cd ../..

# Build Python package
echo "Building Python package..."
python setup.py sdist bdist_wheel

echo "Build complete!"
echo ""
echo "To install locally for development:"
echo "  pip install -e ."
echo ""
echo "To upload to PyPI:"
echo "  pip install twine"
echo "  twine upload dist/*"