#!/bin/bash

# ML API Quick Start Script

echo "🤖 Starting ML Inference API..."
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

# Create models directory
mkdir -p models

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting server on http://localhost:8001"
echo "API Documentation: http://localhost:8001/docs"
echo ""
echo "Example requests:"
echo "  1. Health: curl http://localhost:8001/health"
echo "  2. Predict: curl -X POST http://localhost:8001/predict -H 'Content-Type: application/json' -d '{\"features\":[1,2,3,4,5,6,7,8,9,10]}'"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server
uvicorn main:app --reload --port 8001
