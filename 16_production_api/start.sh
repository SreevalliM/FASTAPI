#!/bin/bash

# Production API Quick Start Script

echo "🚀 Starting Production REST API..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "Starting services with Docker Compose..."
echo ""
echo "Services:"
echo "  - PostgreSQL (port 5432)"
echo "  - Redis (port 6379)"
echo "  - FastAPI (port 8000)"
echo "  - Prometheus (port 9090)"
echo "  - Grafana (port 3000)"
echo ""

# Start Docker Compose
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ All services started successfully!"
    echo ""
    echo "Access points:"
    echo "  📚 API Documentation: http://localhost:8000/docs"
    echo "  🏥 Health Check: http://localhost:8000/health"
    echo "  📊 Prometheus: http://localhost:9090"
    echo "  📈 Grafana: http://localhost:3000 (admin/admin)"
    echo ""
    echo "Example requests:"
    echo "  curl http://localhost:8000/health"
    echo "  curl -X POST http://localhost:8000/tasks -H 'Content-Type: application/json' -d '{\"title\":\"Test Task\",\"priority\":\"high\"}'"
    echo ""
    echo "To stop all services: docker-compose down"
    echo "To view logs: docker-compose logs -f api"
else
    echo ""
    echo "⚠️  Some services may not have started correctly."
    echo "Run 'docker-compose ps' to check status"
    echo "Run 'docker-compose logs' to view logs"
fi
