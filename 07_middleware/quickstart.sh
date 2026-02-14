#!/bin/bash

# FastAPI Middleware Module - Quick Start Script
# This script sets up and runs the middleware examples

set -e  # Exit on error

echo "🚀 FastAPI Middleware - Quick Start"
echo "===================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "../fastapi-env" ]; then
    echo "⚠️  Virtual environment not found at ../fastapi-env"
    echo "Creating virtual environment..."
    python3 -m venv ../fastapi-env
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source ../fastapi-env/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install fastapi uvicorn pytest httpx requests > /dev/null 2>&1

echo "✅ Dependencies installed"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Display menu
echo ""
echo "===================================="
echo "Choose an option:"
echo "===================================="
echo "1. Run Basic Middleware (port 8000)"
echo "2. Run Logging Middleware (port 8001)"
echo "3. Run Timing Middleware (port 8002)"
echo "4. Run CORS Middleware (port 8003)"
echo "5. Run Tests"
echo "6. Run Manual Test Script"
echo "7. Start All Servers (in background)"
echo "8. Stop All Background Servers"
echo "0. Exit"
echo "===================================="

read -p "Enter your choice (0-8): " choice

case $choice in
    1)
        echo "🚀 Starting Basic Middleware Server..."
        python 07_middleware_basic.py
        ;;
    2)
        echo "🚀 Starting Logging Middleware Server..."
        python 07_logging_middleware.py
        ;;
    3)
        echo "🚀 Starting Timing Middleware Server..."
        python 07_timing_middleware.py
        ;;
    4)
        echo "🚀 Starting CORS Middleware Server..."
        python 07_cors_middleware.py
        ;;
    5)
        echo "🧪 Running tests..."
        pytest test_middleware.py -v
        ;;
    6)
        echo "🧪 Running manual test script..."
        python manual_test.py
        ;;
    7)
        echo "🚀 Starting all servers in background..."
        
        if check_port 8000; then
            echo "⚠️  Port 8000 is already in use"
        else
            python 07_middleware_basic.py > /tmp/fastapi_basic.log 2>&1 &
            echo "✅ Basic Middleware started (port 8000)"
        fi
        
        if check_port 8001; then
            echo "⚠️  Port 8001 is already in use"
        else
            python 07_logging_middleware.py > /tmp/fastapi_logging.log 2>&1 &
            echo "✅ Logging Middleware started (port 8001)"
        fi
        
        if check_port 8002; then
            echo "⚠️  Port 8002 is already in use"
        else
            python 07_timing_middleware.py > /tmp/fastapi_timing.log 2>&1 &
            echo "✅ Timing Middleware started (port 8002)"
        fi
        
        if check_port 8003; then
            echo "⚠️  Port 8003 is already in use"
        else
            python 07_cors_middleware.py > /tmp/fastapi_cors.log 2>&1 &
            echo "✅ CORS Middleware started (port 8003)"
        fi
        
        echo ""
        echo "🌐 Servers are running:"
        echo "  http://localhost:8000/docs - Basic Middleware"
        echo "  http://localhost:8001/docs - Logging Middleware"
        echo "  http://localhost:8002/docs - Timing Middleware"
        echo "  http://localhost:8003/docs - CORS Middleware"
        echo ""
        echo "📝 Logs are in /tmp/fastapi_*.log"
        echo "🛑 To stop servers: ./quickstart.sh and choose option 8"
        ;;
    8)
        echo "🛑 Stopping all background servers..."
        pkill -f "07_middleware_basic.py" 2>/dev/null && echo "  ✅ Stopped Basic Middleware" || echo "  ℹ️  Basic Middleware not running"
        pkill -f "07_logging_middleware.py" 2>/dev/null && echo "  ✅ Stopped Logging Middleware" || echo "  ℹ️  Logging Middleware not running"
        pkill -f "07_timing_middleware.py" 2>/dev/null && echo "  ✅ Stopped Timing Middleware" || echo "  ℹ️  Timing Middleware not running"
        pkill -f "07_cors_middleware.py" 2>/dev/null && echo "  ✅ Stopped CORS Middleware" || echo "  ℹ️  CORS Middleware not running"
        echo "✅ All servers stopped"
        ;;
    0)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
