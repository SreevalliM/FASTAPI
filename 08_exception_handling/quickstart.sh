#!/bin/bash

# FastAPI Exception Handling - Quick Start Script
# ==============================================

echo "🚀 FastAPI Exception Handling Quick Start"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📁 Project Root: $PROJECT_ROOT${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/fastapi-env" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    cd "$PROJECT_ROOT"
    python3 -m venv fastapi-env
    echo -e "${GREEN}✅ Virtual environment created${NC}"
    echo ""
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source "$PROJECT_ROOT/fastapi-env/bin/activate"
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Install/upgrade dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q fastapi uvicorn pydantic pytest requests
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Create a helper module to import both apps
cat > "$SCRIPT_DIR/exception_handling.py" << 'EOF'
"""Helper module to make imports easier for tests"""

# Import both apps
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the apps
from importlib.machinery import SourceFileLoader

app_basic = SourceFileLoader(
    "app_basic", 
    str(Path(__file__).parent / "08_exception_handling_basic.py")
).load_module()

app_custom = SourceFileLoader(
    "app_custom",
    str(Path(__file__).parent / "08_custom_exceptions.py")
).load_module()
EOF

echo -e "${GREEN}✅ Helper module created${NC}"
echo ""

# Show menu
echo -e "${BLUE}Choose an option:${NC}"
echo "1) Run Basic Exception Handling API"
echo "2) Run Custom Exception Handling API"
echo "3) Run Tests"
echo "4) Run Manual Tests (requires API running)"
echo "5) Open API Documentation"
echo ""

read -p "Enter your choice (1-5): " choice
echo ""

case $choice in
    1)
        echo -e "${GREEN}🚀 Starting Basic Exception Handling API...${NC}"
        echo ""
        echo -e "${YELLOW}API will be available at: http://127.0.0.1:8000${NC}"
        echo -e "${YELLOW}Documentation: http://127.0.0.1:8000/docs${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        cd "$SCRIPT_DIR"
        python 08_exception_handling_basic.py
        ;;
    2)
        echo -e "${GREEN}🚀 Starting Custom Exception Handling API...${NC}"
        echo ""
        echo -e "${YELLOW}API will be available at: http://127.0.0.1:8000${NC}"
        echo -e "${YELLOW}Documentation: http://127.0.0.1:8000/docs${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        cd "$SCRIPT_DIR"
        python 08_custom_exceptions.py
        ;;
    3)
        echo -e "${GREEN}🧪 Running test suite...${NC}"
        echo ""
        cd "$SCRIPT_DIR"
        pytest test_exception_handling.py -v
        ;;
    4)
        echo -e "${GREEN}🧪 Running manual tests...${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Make sure the API is already running in another terminal!${NC}"
        echo ""
        read -p "Press Enter to continue or Ctrl+C to cancel..."
        cd "$SCRIPT_DIR"
        python manual_test.py
        ;;
    5)
        echo -e "${GREEN}📚 Opening API documentation...${NC}"
        echo ""
        echo -e "${YELLOW}Make sure the API is running first!${NC}"
        echo "Run option 1 or 2, then visit: http://127.0.0.1:8000/docs"
        sleep 2
        open http://127.0.0.1:8000/docs 2>/dev/null || xdg-open http://127.0.0.1:8000/docs 2>/dev/null || echo "Please open http://127.0.0.1:8000/docs in your browser"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done!${NC}"
