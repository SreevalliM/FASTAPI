#!/bin/bash

# 🚀 Quick Start Script for OAuth2 + JWT Authentication
# =====================================================

echo "🔐 FastAPI OAuth2 + JWT Authentication - Quick Start"
echo "===================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "05_user_auth_api.py" ]; then
    echo "❌ Error: Please run this script from the 05_authentication directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider activating your virtual environment first:"
    echo "   source ../fastapi-env/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install required packages
echo "📦 Installing required packages..."
pip install -q python-jose[cryptography] passlib[bcrypt] python-multipart

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Test Users:"
echo "   Admin:  alice / secret"
echo "   User 1: bob / secret"
echo "   User 2: charlie / secret"
echo ""
echo "🌐 Starting server..."
echo "   API Docs: http://localhost:8000/docs"
echo "   ReDoc: http://localhost:8000/redoc"
echo ""
echo "🎯 Try this:"
echo "   1. Open http://localhost:8000/docs"
echo "   2. Click the 'Authorize' button"
echo "   3. Login with: alice / secret"
echo "   4. Try different endpoints!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn 05_user_auth_api:app --reload
