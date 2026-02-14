# 🚀 Production-Grade REST API

A comprehensive production-ready Task Management API built with FastAPI, PostgreSQL, Redis caching, Alembic migrations, Docker deployment, CI/CD, and monitoring.

## ✨ Features

- **PostgreSQL Database**: Production-grade relational database
- **Redis Caching**: Fast in-memory caching for improved performance
- **Alembic Migrations**: Version-controlled database schema management
- **Docker & Docker Compose**: Complete containerization
- **CI/CD Pipeline**: GitHub Actions workflow
- **Monitoring**: Prometheus + Grafana integration
- **Health Checks**: Comprehensive health monitoring
- **Request Logging**: Detailed request/response logging
- **CORS & Compression**: Production middleware
- **Comprehensive Testing**: Full test suite with coverage

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       v
┌─────────────┐     ┌─────────────┐
│   FastAPI   │────>│   Redis     │
│     API     │     │   Cache     │
└──────┬──────┘     └─────────────┘
       │
       v
┌─────────────┐
│ PostgreSQL  │
│  Database   │
└─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)

### Local Development

```bash
# Clone repository
# cd into project directory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start PostgreSQL and Redis (with Docker)
docker run -d -p 5432:5432 \
  -e POSTGRES_DB=taskdb \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  postgres:16-alpine

docker run -d -p 6379:6379 redis:7-alpine

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

### Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

Services:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📚 API Documentation

### Endpoints

#### Health & Info

**GET /**
- Root endpoint with API information

**GET /health**
- Health check for API, database, and Redis
```json
{
  "status": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "timestamp": "2026-02-14T10:30:00"
}
```

#### Tasks

**POST /tasks** - Create task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the FastAPI project",
    "priority": "high"
  }'
```

**GET /tasks** - List tasks (with pagination & filters)
```bash
# All tasks
curl http://localhost:8000/tasks

# With filters
curl "http://localhost:8000/tasks?completed=false&priority=high&skip=0&limit=10"
```

**GET /tasks/{id}** - Get specific task
```bash
curl http://localhost:8000/tasks/1
```

**PUT /tasks/{id}** - Update task
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "completed": true,
    "priority": "low"
  }'
```

**DELETE /tasks/{id}** - Delete task
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

#### Statistics

**GET /stats** - Get task statistics
```json
{
  "total_tasks": 50,
  "completed": 30,
  "pending": 20,
  "by_priority": {
    "low": 15,
    "medium": 20,
    "high": 15
  },
  "completion_rate": 60.0
}
```

#### Admin

**POST /cache/clear** - Clear Redis cache

## 🗄️ Database Migrations

### Create Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

### Apply Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio httpx

# Run all tests
pytest test_production_api.py -v

# Run with coverage
pytest test_production_api.py --cov=main --cov-report=html

# Run specific test
pytest test_production_api.py::test_create_task -v

# Run tests in Docker
docker-compose exec api pytest test_production_api.py -v
```

## 📊 Monitoring

### Prometheus Metrics
Access Prometheus at http://localhost:9090

Example queries:
- `up{app="production-api"}` - API availability
- `rate(http_requests_total[5m])` - Request rate

### Grafana Dashboards
Access Grafana at http://localhost:3000

1. Login with admin/admin
2. Add Prometheus data source (http://prometheus:9090)
3. Import dashboards for FastAPI, PostgreSQL, Redis

### Application Logs
```bash
# View real-time logs
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100 api

# Export logs
docker-compose logs api > api_logs.txt
```

## 🔄 CI/CD Pipeline

GitHub Actions workflow includes:

1. **Testing**
   - Run pytest with coverage
   - Linting with flake8
   - Code formatting with black

2. **Building**
   - Build Docker image
   - Push to container registry
   - Tag with version/commit SHA

3. **Deployment**
   - Deploy to production (configure for your environment)

### Setup GitHub Actions

1. Enable GitHub Actions in repository
2. Add secrets in repository settings:
   - `DOCKER_USERNAME` (if using Docker Hub)
   - `DOCKER_PASSWORD`
   - Add deployment credentials

## 🐳 Docker

### Production Dockerfile
Multi-stage build for smaller image size (~150MB)

### Docker Compose Services
- `postgres`: PostgreSQL database
- `redis`: Redis cache
- `api`: FastAPI application
- `prometheus`: Metrics collection
- `grafana`: Metrics visualization

### Volume Management
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres taskdb > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres taskdb < backup.sql

# View volumes
docker volume ls

# Remove volumes (WARNING: deletes data)
docker-compose down -v
```

## ⚡ Performance

### Caching Strategy
- **List queries**: Cached for 5 minutes
- **Single task**: Cached until modified
- **Statistics**: Cached for 1 minute
- **Background invalidation**: Cache cleared asynchronously

### Benchmarks
```bash
# Install Apache Bench
# apt-get install apache2-utils  (Linux)
# brew install apache-bench       (Mac)

# Test endpoint
ab -n 1000 -c 10 http://localhost:8000/tasks

# With Redis cache (expected: 2-3x faster)
```

### Database Optimization
- Indexes on frequently queried fields
- Connection pooling (10 connections, 20 max overflow)
- Prepared statements via SQLAlchemy

## 🔒 Security Checklist

- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/TLS in production
- [ ] Configure CORS properly
- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Use database connection SSL
- [ ] Scan Docker images for vulnerabilities
- [ ] Regular security updates
- [ ] Input validation (implemented)
- [ ] SQL injection protection (SQLAlchemy ORM)

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
api:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
```

### Load Balancing
Use Nginx or Traefik:
```nginx
upstream api {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}
```

### Database Scaling
- Read replicas for queries
- Connection pooling
- Query optimization
- Partitioning for large tables

## 🎯 Production Deployment

### AWS ECS
```bash
# Build and push
docker build -t your-registry/api:latest .
docker push your-registry/api:latest

# Update ECS service
aws ecs update-service --service api --force-new-deployment
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: your-registry/api:latest
        ports:
        - containerPort: 8000
```

### DigitalOcean/Heroku
Follow platform-specific deployment guides.

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U postgres -d taskdb -c "SELECT 1"

# View PostgreSQL logs
docker-compose logs postgres
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# View Redis logs
docker-compose logs redis
```

### Migration Issues
```bash
# Reset database (WARNING: loses data)
alembic downgrade base
alembic upgrade head

# Check migration status
alembic current
alembic history
```

## 📖 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Redis](https://redis.io/documentation)
- [Docker Compose](https://docs.docker.com/compose/)
- [Prometheus](https://prometheus.io/docs/)

## 📝 License

MIT License - Feel free to use for learning and production!
