# Production Deployment Cheatsheet

## Quick Reference for FastAPI Production Deployment

---

## Environment Variables

```python
# Using pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Security:**
- Never commit `.env` files
- Use secrets management (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
- Validate required variables at startup

---

## Docker Commands

```bash
# Build image
docker build -t app-name .

# Run container
docker run -d -p 8000:8000 --env-file .env app-name

# Docker Compose
docker-compose up -d                  # Start services
docker-compose down                   # Stop services
docker-compose logs -f service-name   # View logs
docker-compose exec service-name sh   # Shell into container
docker-compose up --build             # Rebuild and start

# Clean up
docker system prune -a                # Remove all unused data
```

---

## Production Server Commands

```bash
# Uvicorn (single worker)
uvicorn main:app --host 0.0.0.0 --port 8000

# Uvicorn (multiple workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Gunicorn with Uvicorn workers (recommended for production)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## NGINX Commands

```bash
# Test configuration
nginx -t

# Reload configuration
nginx -s reload

# Start/Stop/Restart
systemctl start nginx
systemctl stop nginx
systemctl restart nginx

# View logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

**Common NGINX Configs:**

```nginx
# Basic proxy
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# SSL redirect
server {
    listen 80;
    return 301 https://$host$request_uri;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
location /api/ {
    limit_req zone=api burst=20;
}
```

---

## AWS Deployment

### Elastic Beanstalk
```bash
eb init -p python-3.11 app-name
eb create production
eb deploy
eb logs
```

### ECS
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/app:latest

# Update service
aws ecs update-service --cluster my-cluster --service my-service --force-new-deployment
```

### Lambda
```bash
sam build
sam deploy --guided
```

---

## Azure Deployment

```bash
# Login
az login

# App Service
az webapp up --runtime PYTHON:3.11 --name app-name

# Container Instances
az container create --resource-group rg --name app --image registry/app:latest --ports 8000

# View logs
az webapp log tail --name app-name --resource-group rg
```

---

## GCP Deployment

```bash
# Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/app
gcloud run deploy app --image gcr.io/PROJECT_ID/app --platform managed --allow-unauthenticated

# App Engine
gcloud app deploy

# View logs
gcloud run services logs read app
```

---

## Render Deployment

1. Connect Git repository
2. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Or use `render.yaml`:
```yaml
services:
  - type: web
    name: app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Railway Deployment

```bash
# Install CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

---

## Health Check Endpoints

```python
@app.get("/health")
async def health():
    """For load balancers"""
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    """For Kubernetes/orchestrators"""
    return {"status": "ready"}

@app.get("/metrics")
async def metrics():
    """For monitoring tools"""
    return {"requests": 1000, "latency": 0.05}
```

---

## Logging Best Practices

```python
import logging

# Structured logging
logger = logging.getLogger(__name__)

# Request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response {request_id}: {response.status_code}")
    return response
```

---

## Security Checklist

- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Implement rate limiting
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Enable CORS properly
- [ ] Implement authentication/authorization
- [ ] Keep dependencies updated
- [ ] Use non-root Docker user
- [ ] Implement security headers
- [ ] Log security events

---

## Performance Optimization

```python
# Connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10
)

# Caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Response compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## Database Migration Commands

```bash
# Alembic
alembic init alembic
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
```

---

## Monitoring & Alerts

**Sentry Integration:**
```python
import sentry_sdk
sentry_sdk.init(dsn="your-dsn", environment="production")
```

**Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram
REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')
```

---

## CI/CD Pipeline Triggers

**GitHub Actions:**
- Push to main: `on: push: branches: [main]`
- Pull requests: `on: pull_request`
- Manual: `on: workflow_dispatch`

**GitLab CI:**
- All branches: `only: - branches`
- Main only: `only: - main`
- Manual: `when: manual`

---

## Common Issues & Solutions

### Issue: Container won't start
- Check logs: `docker logs container-id`
- Verify environment variables
- Check health check configuration

### Issue: Database connection fails
- Verify DATABASE_URL format
- Check network connectivity
- Ensure database is running

### Issue: High memory usage
- Reduce worker count
- Implement connection pooling
- Add memory limits in Docker

### Issue: Slow response times
- Enable caching
- Optimize database queries
- Add indexes
- Implement pagination

---

## Useful Tools

- **Docker**: Container platform
- **Docker Compose**: Multi-container orchestration
- **NGINX**: Reverse proxy and load balancer
- **Gunicorn**: WSGI/ASGI server
- **Uvicorn**: ASGI server
- **Alembic**: Database migrations
- **Sentry**: Error tracking
- **Prometheus**: Metrics and monitoring
- **Grafana**: Metrics visualization
- **Let's Encrypt**: Free SSL certificates

---

## Quick Decision Tree

**Choose deployment platform:**
- **AWS**: Enterprise apps, existing AWS infrastructure
- **Azure**: Microsoft ecosystem, hybrid cloud
- **GCP**: Data-heavy apps, machine learning
- **Render**: Quick deploys, minimal DevOps
- **Railway**: Hobby projects, rapid prototyping

**Choose compute service:**
- **Serverless** (Lambda, Cloud Run): Variable traffic, pay-per-use
- **Containers** (ECS, Cloud Run): Full control, microservices
- **PaaS** (EB, App Service): Quick setup, managed platform

---

## Essential Commands Summary

```bash
# Development
uvicorn main:app --reload

# Production
docker-compose up -d
docker-compose logs -f api

# Deploy
git push origin main  # Triggers CI/CD

# Monitor
docker stats
docker-compose logs -f
curl http://localhost:8000/health

# Debug
docker-compose exec api sh
docker logs container-id --tail 100
```

---

## Remember

1. **Always use environment variables** for configuration
2. **Never commit secrets** to version control
3. **Implement health checks** for all deployments
4. **Monitor everything** in production
5. **Test deployments** in staging first
6. **Have a rollback plan** ready
7. **Keep dependencies updated**
8. **Document your deployment process**

---

**Quick Start:** `docker-compose up -d && docker-compose logs -f api`
