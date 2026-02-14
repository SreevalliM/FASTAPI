#!/bin/bash

# Auth Service Quick Start Script

echo "🔐 Starting Auth Service..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Example requests:"
echo "  1. Register: curl -X POST http://localhost:8000/register -H 'Content-Type: application/json' -d '{\"username\":\"test\",\"email\":\"test@example.com\",\"password\":\"testpass\"}'"
echo "  2. Login: curl -X POST http://localhost:8000/token -d 'username=test&password=testpass'"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server
uvicorn main:app --reload --port 8000
