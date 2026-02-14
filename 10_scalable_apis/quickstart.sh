#!/bin/bash

# Quickstart script for Module 10: Scalable APIs
# This script sets up the environment and provides quick access to examples

set -e  # Exit on error

echo ""
echo "======================================================================"
echo "  Module 10: Writing Scalable APIs - Quick Start"
echo "======================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "../fastapi-env" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv ../fastapi-env
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source ../fastapi-env/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install --upgrade pip -q
pip install fastapi uvicorn[standard] httpx aiosqlite psutil gunicorn pytest pytest-asyncio -q
echo "✓ Dependencies installed"
echo ""

echo -e "${GREEN}======================================================================"
echo "  Setup Complete! Here's what you can do:"
echo "======================================================================${NC}"
echo ""
echo "📚 Read the tutorial:"
echo "   cat 10_SCALABLE_APIS_TUTORIAL.md"
echo ""
echo "🚀 Run the examples:"
echo "   1. Async Basics:           python 10_async_basics.py"
echo "   2. Async DB Operations:    python 10_async_db_operations.py"
echo "   3. Concurrency Patterns:   python 10_concurrency_patterns.py"
echo "   4. Production Deployment:  python 10_production_deployment.py"
echo ""
echo "🌐 View interactive docs:"
echo "   • Async Basics:     http://localhost:8000/docs"
echo "   • DB Operations:    http://localhost:8001/docs"
echo "   • Concurrency:      http://localhost:8002/docs"
echo "   • Production:       http://localhost:8003/docs"
echo ""
echo "🧪 Run tests:"
echo "   pytest test_scalable_apis.py -v"
echo ""
echo "📝 Manual testing:"
echo "   python manual_test.py"
echo ""
echo "📖 Quick reference:"
echo "   cat SCALABLE_APIS_CHEATSHEET.md"
echo ""
echo "🏭 Production deployment:"
echo "   gunicorn 10_production_deployment:app -c gunicorn.conf.py"
echo ""
echo "======================================================================"
echo ""

# Ask if user wants to run an example
read -p "Would you like to run Async Basics example now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo -e "${GREEN}Starting Async Basics API...${NC}"
    echo "Access it at: http://localhost:8000/docs"
    echo "Press Ctrl+C to stop"
    echo ""
    python 10_async_basics.py
fi

echo ""
echo "Happy coding! 🚀"
echo ""
