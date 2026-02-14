#!/bin/bash

# Production Deployment Quick Start Script
# This script helps you get started with the production deployment module

set -e  # Exit on error

echo "=========================================="
echo "FastAPI Production Deployment Quick Start"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running in the correct directory
if [ ! -f "12_production_api.py" ]; then
    echo "Error: Please run this script from the 12_production_deployment directory"
    exit 1
fi

# Menu
echo "Select an option:"
echo "1. Local development (without Docker)"
echo "2. Docker development environment"
echo "3. Docker production environment"
echo "4. Run tests"
echo "5. Manual API testing"
echo "6. View deployment guides"
echo "7. Clean up Docker resources"
echo ""
read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        print_info "Starting local development server..."
        
        # Check if virtual environment exists
        if [ ! -d "../fastapi-env" ]; then
            print_warning "Virtual environment not found. Creating one..."
            cd ..
            python3 -m venv fastapi-env
            source fastapi-env/bin/activate
            cd 12_production_deployment
        else
            source ../fastapi-env/bin/activate
        fi
        
        # Install dependencies
        print_info "Installing dependencies..."
        pip install -q -r requirements.txt
        
        # Create .env file if it doesn't exist
        if [ ! -f ".env" ]; then
            print_info "Creating .env file from template..."
            cp .env.example .env
            print_warning "Please edit .env file with your configuration"
        fi
        
        # Set development environment variables
        export ENV=development
        export DEBUG=true
        export LOG_LEVEL=INFO
        
        print_success "Starting FastAPI server..."
        print_info "API: http://localhost:8000"
        print_info "Docs: http://localhost:8000/api/docs"
        print_info "Press Ctrl+C to stop"
        echo ""
        
        python 12_production_api.py
        ;;
        
    2)
        print_info "Starting Docker development environment..."
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo "Error: Docker is not installed. Please install Docker first."
            exit 1
        fi
        
        # Check if docker-compose is installed
        if ! command -v docker-compose &> /dev/null; then
            echo "Error: docker-compose is not installed. Please install docker-compose first."
            exit 1
        fi
        
        # Create .env file if it doesn't exist
        if [ ! -f ".env" ]; then
            print_info "Creating .env file from template..."
            cp .env.example .env
        fi
        
        print_info "Building and starting containers..."
        docker-compose -f docker-compose.dev.yml up --build -d
        
        print_success "Containers started successfully!"
        echo ""
        print_info "Services:"
        print_info "  API: http://localhost:8000"
        print_info "  API Docs: http://localhost:8000/api/docs"
        print_info "  PostgreSQL: localhost:5432"
        print_info "  Redis: localhost:6379"
        echo ""
        print_info "Useful commands:"
        print_info "  View logs: docker-compose -f docker-compose.dev.yml logs -f"
        print_info "  Stop: docker-compose -f docker-compose.dev.yml down"
        print_info "  Restart: docker-compose -f docker-compose.dev.yml restart"
        echo ""
        
        # Show logs
        read -p "Show logs? (y/n): " show_logs
        if [ "$show_logs" = "y" ]; then
            docker-compose -f docker-compose.dev.yml logs -f
        fi
        ;;
        
    3)
        print_info "Starting Docker production environment..."
        
        if ! command -v docker &> /dev/null; then
            echo "Error: Docker is not installed. Please install Docker first."
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            echo "Error: docker-compose is not installed. Please install docker-compose first."
            exit 1
        fi
        
        # Create .env file if it doesn't exist
        if [ ! -f ".env" ]; then
            print_warning "No .env file found. Creating from template..."
            cp .env.example .env
            print_warning "Please edit .env file with production values before deploying to production!"
        fi
        
        print_info "Building and starting containers..."
        docker-compose up --build -d
        
        print_success "Production containers started successfully!"
        echo ""
        print_info "Services:"
        print_info "  API (via NGINX): http://localhost"
        print_info "  API (direct): http://localhost:8000"
        print_info "  Health: http://localhost:8000/health"
        echo ""
        print_info "Useful commands:"
        print_info "  View logs: docker-compose logs -f"
        print_info "  Stop: docker-compose down"
        print_info "  Restart: docker-compose restart"
        echo ""
        
        # Test health endpoint
        sleep 3
        print_info "Testing health endpoint..."
        if curl -s http://localhost:8000/health > /dev/null; then
            print_success "API is healthy!"
        else
            print_warning "API health check failed. Check logs: docker-compose logs api"
        fi
        ;;
        
    4)
        print_info "Running tests..."
        
        # Activate virtual environment if it exists
        if [ -d "../fastapi-env" ]; then
            source ../fastapi-env/bin/activate
        fi
        
        # Install test dependencies
        print_info "Installing dependencies..."
        pip install -q -r requirements.txt pytest pytest-asyncio pytest-cov httpx
        
        # Run tests
        print_info "Executing test suite..."
        export ENV=test
        export DATABASE_URL=sqlite:///./test.db
        
        if pytest test_production_api.py -v --tb=short; then
            print_success "All tests passed!"
        else
            print_warning "Some tests failed. Review the output above."
        fi
        ;;
        
    5)
        print_info "Running manual API tests..."
        
        # Activate virtual environment if it exists
        if [ -d "../fastapi-env" ]; then
            source ../fastapi-env/bin/activate
        fi
        
        # Install dependencies
        pip install -q httpx
        
        # Run manual tests
        python manual_test.py
        ;;
        
    6)
        print_info "Deployment Guides Available:"
        echo ""
        echo "📚 Main Resources:"
        echo "  1. 12_PRODUCTION_DEPLOYMENT_TUTORIAL.md - Comprehensive tutorial"
        echo "  2. DEPLOYMENT_CHEATSHEET.md - Quick reference"
        echo "  3. README.md - Module overview"
        echo ""
        echo "☁️  Cloud-Specific Guides:"
        echo "  • AWS: deploy/aws/"
        echo "  • Azure: deploy/azure/"
        echo "  • GCP: deploy/gcp/"
        echo "  • Render: deploy/render/"
        echo "  • Railway: deploy/railway/"
        echo ""
        echo "🔧 Configuration Files:"
        echo "  • GitHub Actions: .github-workflows-ci-cd.yml"
        echo "  • GitLab CI: .gitlab-ci.yml"
        echo "  • Docker: Dockerfile, docker-compose.yml"
        echo "  • NGINX: nginx.conf"
        echo ""
        read -p "Open the main tutorial? (y/n): " open_tutorial
        if [ "$open_tutorial" = "y" ]; then
            if command -v open &> /dev/null; then
                open 12_PRODUCTION_DEPLOYMENT_TUTORIAL.md
            elif command -v xdg-open &> /dev/null; then
                xdg-open 12_PRODUCTION_DEPLOYMENT_TUTORIAL.md
            else
                print_info "Please open 12_PRODUCTION_DEPLOYMENT_TUTORIAL.md manually"
            fi
        fi
        ;;
        
    7)
        print_warning "This will remove all stopped containers, unused networks, and dangling images."
        read -p "Continue? (y/n): " confirm
        
        if [ "$confirm" = "y" ]; then
            print_info "Stopping containers..."
            docker-compose down 2>/dev/null || true
            docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
            
            print_info "Cleaning up Docker resources..."
            docker system prune -f
            
            print_success "Cleanup complete!"
        else
            print_info "Cleanup cancelled."
        fi
        ;;
        
    *)
        echo "Invalid choice. Please run the script again and select 1-7."
        exit 1
        ;;
esac

echo ""
print_success "Done!"
