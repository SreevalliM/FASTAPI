#!/bin/bash

# E-commerce API Quickstart Script

echo "🛒 E-commerce API Quickstart"
echo "=============================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating fastapi-env..."
    source ../fastapi-env/bin/activate
fi

# Check dependencies
echo "📦 Checking dependencies..."
pip install -q fastapi uvicorn sqlalchemy pydantic[email]

echo ""
echo "🚀 Starting E-commerce API..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 Interactive docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the API
python ecommerce_api.py
