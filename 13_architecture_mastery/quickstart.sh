#!/bin/bash

# Quickstart script for Architecture Mastery module

echo "======================================"
echo " Architecture Mastery - Quick Start"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python 3 found"

# Check dependencies
echo ""
echo -e "${BLUE}Checking dependencies...${NC}"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing FastAPI..."
    pip install fastapi uvicorn
fi

if ! python3 -c "import redis" 2>/dev/null; then
    echo "Installing Redis client..."
    pip install redis aioredis
fi

if ! python3 -c "import slowapi" 2>/dev/null; then
    echo "Installing SlowAPI (rate limiting)..."
    pip install slowapi
fi

if ! python3 -c "import httpx" 2>/dev/null; then
    echo "Installing HTTPX (HTTP client)..."
    pip install httpx
fi

echo -e "${GREEN}✓ All dependencies installed${NC}"

# Menu
echo ""
echo "What would you like to run?"
echo ""
echo "  1. Clean Architecture (Products & Orders)"
echo "  2. Repository Pattern (Multiple backends)"
echo "  3. Rate Limiting (Various strategies)"
echo "  4. Redis Caching (Requires Redis running)"
echo "  5. API Gateway (Requires backend services)"
echo "  6. Microservices (Start a service)"
echo "  7. Run Manual Tests"
echo ""
read -p "Enter choice (1-7): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}Starting Clean Architecture example...${NC}"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        python3 -m uvicorn 13_clean_architecture:app --reload
        ;;
    
    2)
        echo ""
        echo -e "${YELLOW}Starting Repository Pattern example...${NC}"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        echo "Note: Change REPOSITORY_TYPE in the file to test different backends:"
        echo "  - memory (in-memory)"
        echo "  - sqlite (file-based)"
        echo "  - cached_memory (with caching)"
        echo "  - cached_sqlite (SQLite with caching)"
        echo ""
        python3 -m uvicorn 13_repository_pattern:app --reload
        ;;
    
    3)
        echo ""
        echo -e "${YELLOW}Starting Rate Limiting example...${NC}"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        echo "Test endpoints:"
        echo "  curl http://localhost:8000/slowapi/basic"
        echo "  curl http://localhost:8000/token-bucket/data"
        echo ""
        python3 -m uvicorn 13_rate_limiting:app --reload
        ;;
    
    4)
        echo ""
        echo -e "${YELLOW}Starting Redis Caching example...${NC}"
        echo ""
        # Check if Redis is running
        if command_exists docker; then
            echo "Checking if Redis is running..."
            if ! docker ps | grep -q redis; then
                echo "Starting Redis container..."
                docker run -d -p 6379:6379 --name redis-cache redis:alpine
                echo -e "${GREEN}✓ Redis started${NC}"
            else
                echo -e "${GREEN}✓ Redis already running${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ Docker not found. Please start Redis manually:${NC}"
            echo "  docker run -d -p 6379:6379 redis:alpine"
            echo "Or install Redis locally."
        fi
        
        echo ""
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        python3 -m uvicorn 13_caching_redis:app --reload
        ;;
    
    5)
        echo ""
        echo -e "${YELLOW}Starting API Gateway...${NC}"
        echo ""
        echo "You need to start backend services in separate terminals:"
        echo ""
        echo "  Terminal 2: uvicorn 13_api_gateway:users_service --reload --port 8001"
        echo "  Terminal 3: uvicorn 13_api_gateway:products_service --reload --port 8002"
        echo "  Terminal 4: uvicorn 13_api_gateway:orders_service --reload --port 8003"
        echo ""
        echo "Then test the gateway with API key:"
        echo "  curl -H 'X-API-Key: user_key_123' http://localhost:8000/api/users"
        echo ""
        read -p "Press Enter to start API Gateway..."
        python3 -m uvicorn 13_api_gateway:app --reload --port 8000
        ;;
    
    6)
        echo ""
        echo "Which microservice would you like to start?"
        echo ""
        echo "  1. Users Service (port 8001)"
        echo "  2. Products Service (port 8002)"
        echo "  3. Orders Service (port 8003)"
        echo "  4. Message Bus (port 8004)"
        echo ""
        read -p "Enter choice (1-4): " service_choice
        
        case $service_choice in
            1)
                echo -e "${YELLOW}Starting Users Service...${NC}"
                python3 13_microservices_example.py users
                ;;
            2)
                echo -e "${YELLOW}Starting Products Service...${NC}"
                python3 13_microservices_example.py products
                ;;
            3)
                echo -e "${YELLOW}Starting Orders Service...${NC}"
                python3 13_microservices_example.py orders
                ;;
            4)
                echo -e "${YELLOW}Starting Message Bus...${NC}"
                python3 13_microservices_example.py message_bus
                ;;
            *)
                echo "Invalid choice"
                ;;
        esac
        ;;
    
    7)
        echo ""
        echo -e "${YELLOW}Running manual tests...${NC}"
        echo ""
        echo "Make sure the service you want to test is running on port 8000"
        echo ""
        read -p "Press Enter to continue..."
        python3 manual_test.py
        ;;
    
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
