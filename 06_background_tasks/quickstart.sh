#!/bin/bash

# Quick Start Script for Background Tasks Module
# ==============================================

echo "🚀 FastAPI Background Tasks Module - Quick Start"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "../fastapi-env" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv ../fastapi-env
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source ../fastapi-env/bin/activate

# Install dependencies
echo -e "${BLUE}📥 Installing dependencies...${NC}"
pip install -q fastapi uvicorn pydantic[email] pytest httpx

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Function to run examples
run_example() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo ""
}

# Show menu
show_menu() {
    echo ""
    echo "What would you like to do?"
    echo ""
    echo "1) Run Basic Background Tasks Example (Port 8000)"
    echo "2) Run Email Sending Example (Port 8001)"
    echo "3) Test Basic Example with cURL"
    echo "4) Test Email Example with cURL"
    echo "5) Run Tests"
    echo "6) Open API Documentation"
    echo "7) Show Module Structure"
    echo "8) Exit"
    echo ""
    echo -n "Enter your choice [1-8]: "
}

# Test basic example
test_basic() {
    echo ""
    echo -e "${GREEN}Testing Basic Background Tasks...${NC}"
    echo ""
    
    echo -e "${YELLOW}Test 1: Simple notification${NC}"
    curl -X POST "http://localhost:8000/simple/notification" \
      -H "Content-Type: application/json" \
      -d '{"email": "test@example.com", "message": "Hello from curl!"}'
    echo ""
    echo ""
    
    sleep 2
    
    echo -e "${YELLOW}Test 2: Async notification${NC}"
    curl -X POST "http://localhost:8000/simple/notification-async" \
      -H "Content-Type: application/json" \
      -d '{"email": "async@example.com", "message": "Async test"}'
    echo ""
    echo ""
    
    sleep 2
    
    echo -e "${YELLOW}Test 3: Create order (multiple tasks)${NC}"
    curl -X POST "http://localhost:8000/order" \
      -H "Content-Type: application/json" \
      -d '{"item": "Laptop", "quantity": 2, "email": "customer@example.com"}'
    echo ""
    echo ""
    
    sleep 5
    
    echo -e "${YELLOW}Test 4: Get logs${NC}"
    curl "http://localhost:8000/logs"
    echo ""
    echo ""
}

# Test email example
test_email() {
    echo ""
    echo -e "${GREEN}Testing Email Sending Example...${NC}"
    echo ""
    
    echo -e "${YELLOW}Test 1: Register user${NC}"
    curl -X POST "http://localhost:8001/register" \
      -H "Content-Type: application/json" \
      -d '{"username": "john_doe", "email": "john@example.com", "full_name": "John Doe"}'
    echo ""
    echo ""
    
    sleep 2
    
    echo -e "${YELLOW}Test 2: Password reset${NC}"
    curl -X POST "http://localhost:8001/password-reset" \
      -H "Content-Type: application/json" \
      -d '{"email": "john@example.com"}'
    echo ""
    echo ""
    
    sleep 2
    
    echo -e "${YELLOW}Test 3: Order confirmation${NC}"
    curl -X POST "http://localhost:8001/order-confirmation" \
      -H "Content-Type: application/json" \
      -d '{"order_id": "ORD-12345", "email": "john@example.com", "items": ["Book", "Pen"], "total": 25.99}'
    echo ""
    echo ""
    
    sleep 3
    
    echo -e "${YELLOW}Test 4: Get email logs${NC}"
    curl "http://localhost:8001/email-logs"
    echo ""
    echo ""
}

# Show module structure
show_structure() {
    echo ""
    echo -e "${GREEN}📁 Module Structure:${NC}"
    echo ""
    tree -L 1 . 2>/dev/null || ls -la
    echo ""
    echo -e "${BLUE}Key Files:${NC}"
    echo "  • 06_background_tasks_basic.py - Basic examples"
    echo "  • 06_email_sending.py - Email sending scenarios"
    echo "  • 06_BACKGROUND_TASKS_TUTORIAL.md - Complete tutorial"
    echo "  • BACKGROUND_TASKS_CHEATSHEET.md - Quick reference"
    echo "  • test_background_tasks.py - Test suite"
    echo ""
}

# Main loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            run_example "Running Basic Background Tasks Example"
            echo "Starting server on http://localhost:8000"
            echo "Press Ctrl+C to stop"
            echo ""
            python 06_background_tasks_basic.py
            ;;
        2)
            run_example "Running Email Sending Example"
            echo "Starting server on http://localhost:8001"
            echo "Press Ctrl+C to stop"
            echo ""
            python 06_email_sending.py
            ;;
        3)
            test_basic
            echo -e "${GREEN}✅ Tests completed! Check the logs above.${NC}"
            ;;
        4)
            test_email
            echo -e "${GREEN}✅ Tests completed! Check the logs above.${NC}"
            ;;
        5)
            run_example "Running Tests"
            pytest test_background_tasks.py -v
            ;;
        6)
            echo ""
            echo -e "${GREEN}Opening API documentation...${NC}"
            echo ""
            echo "Make sure a server is running, then open:"
            echo "  • Basic Example: http://localhost:8000/docs"
            echo "  • Email Example: http://localhost:8001/docs"
            echo ""
            if [[ "$OSTYPE" == "darwin"* ]]; then
                open "http://localhost:8000/docs" 2>/dev/null || echo "Start the server first!"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                xdg-open "http://localhost:8000/docs" 2>/dev/null || echo "Start the server first!"
            fi
            ;;
        7)
            show_structure
            ;;
        8)
            echo ""
            echo -e "${GREEN}👋 Goodbye!${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo -e "${YELLOW}⚠️  Invalid choice. Please enter 1-8.${NC}"
            ;;
    esac
done
