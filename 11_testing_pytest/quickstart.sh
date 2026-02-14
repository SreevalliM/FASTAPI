#!/bin/bash

# 🧪 Testing with Pytest - Quick Start Script
# ===========================================
# This script helps you quickly set up and run the testing examples

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🧪 Testing with Pytest - Quick Start         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not detected${NC}"
    echo -e "${YELLOW}Attempting to activate fastapi-env...${NC}"
    
    if [ -f "../fastapi-env/bin/activate" ]; then
        source ../fastapi-env/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${RED}✗ Could not find virtual environment${NC}"
        echo -e "${YELLOW}Please activate it manually:${NC}"
        echo -e "  source ../fastapi-env/bin/activate"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Virtual environment active: ${VIRTUAL_ENV}${NC}"
fi

echo ""

# Check for required packages
echo -e "${BLUE}📦 Checking dependencies...${NC}"

REQUIRED_PACKAGES=("pytest" "fastapi" "uvicorn")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    echo -e "${BLUE}Installing missing packages...${NC}"
    pip install pytest pytest-cov pytest-asyncio httpx
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ All dependencies present${NC}"
fi

echo ""

# Main menu
while true; do
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}What would you like to do?${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo "  1) Run all tests"
    echo "  2) Run tests with verbose output"
    echo "  3) Run tests with coverage"
    echo "  4) Run specific test category"
    echo "  5) Run the API server (for manual testing)"
    echo "  6) Run manual test script"
    echo "  7) View tutorial"
    echo "  8) View cheatsheet"
    echo "  9) Show me the commands"
    echo "  0) Exit"
    echo ""
    read -p "Enter your choice [0-9]: " choice

    case $choice in
        1)
            echo ""
            echo -e "${BLUE}🧪 Running all tests...${NC}"
            pytest test_testing_basics.py
            ;;
        2)
            echo ""
            echo -e "${BLUE}🧪 Running tests with verbose output...${NC}"
            pytest test_testing_basics.py -v
            ;;
        3)
            echo ""
            echo -e "${BLUE}📊 Running tests with coverage...${NC}"
            pytest test_testing_basics.py --cov=11_api_for_testing --cov-report=term-missing
            echo ""
            echo -e "${YELLOW}💡 Tip: Generate HTML coverage report with:${NC}"
            echo -e "   pytest --cov=11_api_for_testing --cov-report=html"
            echo -e "   Then open: htmlcov/index.html"
            ;;
        4)
            echo ""
            echo -e "${BLUE}Select test category:${NC}"
            echo "  1) Tests with 'mock' in name"
            echo "  2) Tests with 'override' in name"
            echo "  3) Tests with 'auth' in name"
            echo "  4) Tests with 'database' in name"
            echo "  5) Tests with 'order' in name"
            echo ""
            read -p "Enter choice [1-5]: " cat_choice
            
            case $cat_choice in
                1) pytest test_testing_basics.py -k "mock" -v ;;
                2) pytest test_testing_basics.py -k "override" -v ;;
                3) pytest test_testing_basics.py -k "auth" -v ;;
                4) pytest test_testing_basics.py -k "database" -v ;;
                5) pytest test_testing_basics.py -k "order" -v ;;
                *) echo -e "${RED}Invalid choice${NC}" ;;
            esac
            ;;
        5)
            echo ""
            echo -e "${BLUE}🚀 Starting API server...${NC}"
            echo -e "${YELLOW}The API will be available at: http://localhost:8000${NC}"
            echo -e "${YELLOW}Docs available at: http://localhost:8000/docs${NC}"
            echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
            echo ""
            python 11_api_for_testing.py
            ;;
        6)
            echo ""
            echo -e "${BLUE}🔧 Running manual test script...${NC}"
            python manual_test.py
            ;;
        7)
            echo ""
            echo -e "${BLUE}📖 Opening tutorial...${NC}"
            if command -v less &> /dev/null; then
                less 11_TESTING_TUTORIAL.md
            else
                cat 11_TESTING_TUTORIAL.md
            fi
            ;;
        8)
            echo ""
            echo -e "${BLUE}📋 Opening cheatsheet...${NC}"
            if command -v less &> /dev/null; then
                less TESTING_CHEATSHEET.md
            else
                cat TESTING_CHEATSHEET.md
            fi
            ;;
        9)
            echo ""
            echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
            echo -e "${BLUE}🔧 Useful Commands${NC}"
            echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
            echo ""
            echo -e "${YELLOW}Basic Testing:${NC}"
            echo "  pytest test_testing_basics.py              # Run all tests"
            echo "  pytest test_testing_basics.py -v           # Verbose output"
            echo "  pytest test_testing_basics.py -s           # Show print statements"
            echo "  pytest test_testing_basics.py -x           # Stop on first failure"
            echo ""
            echo -e "${YELLOW}Specific Tests:${NC}"
            echo "  pytest test_testing_basics.py::test_root   # Run one test"
            echo "  pytest -k \"mock\" -v                       # Tests with 'mock' in name"
            echo "  pytest -k \"auth\" -v                       # Tests with 'auth' in name"
            echo ""
            echo -e "${YELLOW}Coverage:${NC}"
            echo "  pytest --cov=11_api_for_testing            # Basic coverage"
            echo "  pytest --cov=11_api_for_testing --cov-report=html   # HTML report"
            echo "  pytest --cov=11_api_for_testing --cov-report=term-missing  # Show missing lines"
            echo ""
            echo -e "${YELLOW}Debugging:${NC}"
            echo "  pytest --pdb                               # Drop to debugger on failure"
            echo "  pytest --lf                                # Run last failed"
            echo "  pytest --collect-only                      # List all tests"
            echo ""
            echo -e "${YELLOW}Running API:${NC}"
            echo "  python 11_api_for_testing.py               # Start server"
            echo "  uvicorn 11_api_for_testing:app --reload   # Start with auto-reload"
            echo ""
            read -p "Press Enter to continue..."
            ;;
        0)
            echo ""
            echo -e "${GREEN}✨ Happy Testing! 🧪${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    echo ""
done
