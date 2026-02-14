# Production Deployment Tutorial: Complete Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Environment Variables](#environment-variables)
3. [Dockerizing FastAPI](#dockerizing-fastapi)
4. [NGINX Reverse Proxy](#nginx-reverse-proxy)
5. [Logging & Monitoring](#logging--monitoring)
6. [CI/CD Pipelines](#cicd-pipelines)
7. [Cloud Deployment](#cloud-deployment)
   - [AWS](#deploying-to-aws)
   - [Azure](#deploying-to-azure)
   - [Google Cloud Platform](#deploying-to-gcp)
   - [Render](#deploying-to-render)
   - [Railway](#deploying-to-railway)
8. [Best Practices](#best-practices)

---

## Introduction

This tutorial covers everything you need to deploy a FastAPI application to production, including containerization, reverse proxies, CI/CD, and deployment to multiple cloud platforms.

**What You'll Learn:**
- Configure environment variables securely
- Containerize FastAPI with Docker
- Set up NGINX as a reverse proxy
- Implement structured logging and monitoring
- Create CI/CD pipelines
- Deploy to AWS, Azure, GCP, Render, and Railway

---

## Environment Variables

### Why Environment Variables?

Environment variables allow you to:
- Separate configuration from code
- Use different settings per environment (dev, staging, prod)
- Keep secrets secure
- Change configuration without code changes

### Using Pydantic Settings

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    environment: str = Field(default="development", alias="ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    
    # Security
    api_key: str = Field(..., alias="API_KEY")
    secret_key: str = Field(..., alias="SECRET_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Creating .env Files

**.env (local development)**
```bash
ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./test.db
API_KEY=dev-key
SECRET_KEY=dev-secret
```

**.env.production**
```bash
ENV=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:5432/db
API_KEY=prod-key-from-secrets-manager
SECRET_KEY=prod-secret-from-secrets-manager
```

### Security Best Practices

1. **Never commit .env files to Git**
   ```bash
   echo ".env" >> .gitignore
   echo ".env.*" >> .gitignore
   ```

2. **Use secret management services:**
   - AWS: Secrets Manager, Parameter Store
   - Azure: Key Vault
   - GCP: Secret Manager
   - Render/Railway: Built-in secret management

3. **Validate required variables:**
   ```python
   required_vars = ["DATABASE_URL", "API_KEY", "SECRET_KEY"]
   for var in required_vars:
       if not getattr(settings, var.lower(), None):
           raise ValueError(f"Missing required environment variable: {var}")
   ```

---

## Dockerizing FastAPI

### Why Docker?

- **Consistency**: Same environment everywhere
- **Isolation**: No dependency conflicts
- **Scalability**: Easy to scale horizontally
- **Portability**: Run anywhere Docker runs

### Multi-Stage Dockerfile

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "12_production_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose for Local Development

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app  # Hot reload
    ports:
      - "8000:8000"
    environment:
      - ENV=development
      - DEBUG=true
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: fastapi_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Docker Commands

```bash
# Build image
docker build -t fastapi-app .

# Run container
docker run -d -p 8000:8000 --env-file .env fastapi-app

# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

### Docker Best Practices

1. **Use .dockerignore**
   ```
   __pycache__
   *.pyc
   .env
   .git
   .vscode
   venv/
   ```

2. **Multi-stage builds** - Reduce image size
3. **Non-root user** - Security
4. **Health checks** - Container orchestration
5. **Layer caching** - Faster builds

---

## NGINX Reverse Proxy

### Why Use NGINX?

- **Load balancing**: Distribute traffic across servers
- **SSL termination**: Handle HTTPS
- **Caching**: Improve performance
- **Rate limiting**: Prevent abuse
- **Static file serving**: Offload from application

### Basic NGINX Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream fastapi_backend {
        least_conn;
        server api:8000 max_fails=3 fail_timeout=30s;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;

        location / {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            access_log off;
            proxy_pass http://fastapi_backend/health;
        }
    }
}
```

### Load Balancing

```nginx
upstream fastapi_backend {
    least_conn;  # Use least connections algorithm
    server api1:8000 weight=3;
    server api2:8000 weight=2;
    server api3:8000 weight=1;
    
    # Health checks
    keepalive 32;
}
```

### Rate Limiting

```nginx
# Define rate limit zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://fastapi_backend;
    }
}
```

### Caching

```nginx
# Proxy cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

server {
    location /api/items {
        proxy_cache api_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        add_header X-Cache-Status $upstream_cache_status;
        
        proxy_pass http://fastapi_backend;
    }
}
```

### SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (runs automatically)
sudo certbot renew --dry-run
```

---

## Logging & Monitoring

### Structured Logging

```python
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    
    if settings.environment == "production":
        # JSON logging for production
        logHandler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)
    else:
        # Human-readable logging for development
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
setup_logging()
logger = logging.getLogger(__name__)
```

### Request ID Tracking

```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path
        }
    )
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """Health check for load balancers"""
    # Check database connection
    try:
        await database.execute("SELECT 1")
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    return {"status": "ready"}

@app.get("/metrics")
async def metrics():
    """Metrics for Prometheus"""
    return {
        "requests_total": request_counter,
        "response_time_ms": avg_response_time
    }
```

### Error Tracking with Sentry

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    environment=settings.environment,
    traces_sample_rate=1.0 if settings.environment == "development" else 0.1,
    integrations=[
        FastApiIntegration(),
    ]
)
```

### Application Performance Monitoring

**Using Prometheus:**

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

---

## CI/CD Pipelines

### GitHub Actions

See `.github/workflows/ci-cd.yml` for a complete example that includes:

1. **Testing**: Run tests on multiple Python versions
2. **Linting**: Code quality checks
3. **Building**: Build and push Docker images
4. **Deployment**: Deploy to production

Key features:
- Parallel testing across Python versions
- Docker layer caching
- Secrets management
- Environment-specific deployments

### GitLab CI

See `.gitlab-ci.yml` for a complete pipeline with:

1. **Test stage**: Automated testing
2. **Build stage**: Docker image creation
3. **Deploy stages**: Deploy to dev, staging, and production

Key features:
- Service containers for testing
- Manual approval for production
- Environment URLs
- Artifact caching

### CI/CD Best Practices

1. **Run tests on every commit**
2. **Use branch protection rules**
3. **Implement code review requirements**
4. **Use semantic versioning**
5. **Tag releases**
6. **Deploy to staging before production**
7. **Implement rollback procedures**
8. **Monitor deployments**

---

## Cloud Deployment

### Deploying to AWS

#### Option 1: Elastic Beanstalk (Easiest)

```bash
# Install EB CLI
pip install awsebcli

# Initialize application
eb init -p python-3.11 fastapi-app --region us-east-1

# Create environment
eb create fastapi-prod --database.engine postgres

# Deploy
eb deploy

# View logs
eb logs

# SSH into instance
eb ssh
```

#### Option 2: ECS (Recommended for Production)

1. **Create ECR repository:**
   ```bash
   aws ecr create-repository --repository-name fastapi-app
   ```

2. **Build and push image:**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   docker build -t fastapi-app .
   docker tag fastapi-app:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/fastapi-app:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/fastapi-app:latest
   ```

3. **Create ECS cluster and service** using the task definition in `deploy/aws/ecs-task-definition.json`

4. **Set up Application Load Balancer** for traffic distribution

#### Option 3: Lambda (Serverless)

```bash
# Install dependencies
pip install mangum

# Build deployment package
sam build

# Deploy
sam deploy --guided
```

**When to use each:**
- **Elastic Beanstalk**: Quick setup, managed platform
- **ECS**: Full control, best for microservices
- **Lambda**: Serverless, pay-per-use, best for APIs with variable traffic

---

### Deploying to Azure

#### Option 1: App Service

```bash
# Login
az login

# Create resource group
az group create --name fastapi-rg --location eastus

# Create App Service plan
az appservice plan create --name fastapi-plan --resource-group fastapi-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group fastapi-rg --plan fastapi-plan --name fastapi-app-unique --runtime "PYTHON:3.11"

# Deploy
az webapp up --resource-group fastapi-rg --name fastapi-app-unique
```

#### Option 2: Container Instances

```bash
# Create container group
az container create \
  --resource-group fastapi-rg \
  --name fastapi-container \
  --image yourregistry.azurecr.io/fastapi:latest \
  --cpu 2 \
  --memory 4 \
  --dns-name-label fastapi-app \
  --ports 8000
```

#### Option 3: Azure Kubernetes Service (AKS)

For large-scale applications requiring orchestration.

---

### Deploying to GCP

#### Option 1: Cloud Run (Recommended)

```bash
# Build with Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/fastapi-app

# Deploy to Cloud Run
gcloud run deploy fastapi-app \
  --image gcr.io/PROJECT_ID/fastapi-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

**Benefits:**
- Automatic scaling to zero
- Pay only for requests
- Fully managed
- Simple deployment

#### Option 2: App Engine

```bash
# Create app.yaml
echo "runtime: python311" > app.yaml
echo "entrypoint: gunicorn -w 4 -k uvicorn.workers.UvicornWorker 12_production_api:app" >> app.yaml

# Deploy
gcloud app deploy
```

#### Option 3: Google Kubernetes Engine (GKE)

For enterprise applications requiring full Kubernetes features.

---

### Deploying to Render

Render offers zero-configuration deployments with built-in:
- SSL certificates
- Automatic deploys from Git
- Preview environments for PRs
- Managed databases

#### Steps:

1. **Connect your Git repository**
2. **Create a new Web Service**
3. **Configure:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn 12_production_api:app --host 0.0.0.0 --port $PORT`

Or use the `render.yaml` blueprint for infrastructure-as-code.

**Advantages:**
- Zero DevOps - fully managed
- Free SSL
- Automatic deploys
- Built-in metrics

---

### Deploying to Railway

Railway offers simple deployment with excellent developer experience.

#### Deployment Steps:

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   railway init
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

Or connect your GitHub repository for automatic deployments.

**Use railway.toml** for configuration:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn 12_production_api:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
```

**Advantages:**
- Instant deploys
- Free tier includes databases
- Built-in metrics
- Preview environments

---

## Best Practices

### Security

1. **Use HTTPS everywhere**
2. **Implement rate limiting**
3. **Validate all inputs**
4. **Use parameterized queries (prevent SQL injection)**
5. **Implement CORS properly**
6. **Keep dependencies updated**
7. **Use secrets management**
8. **Implement authentication and authorization**
9. **Log security events**
10. **Regular security audits**

### Performance

1. **Use async/await properly**
2. **Implement caching (Redis)**
3. **Database connection pooling**
4. **Use CDN for static files**
5. **Compress responses (gzip)**
6. **Implement pagination**
7. **Use database indexes**
8. **Monitor slow queries**
9. **Horizontal scaling**
10. **Load balancing**

### Reliability

1. **Health checks**
2. **Graceful shutdown**
3. **Circuit breakers**
4. **Retry logic with exponential backoff**
5. **Database migrations**
6. **Backup strategy**
7. **Disaster recovery plan**
8. **Zero-downtime deployments**
9. **Rollback procedures**
10. **Monitoring and alerting**

### Monitoring

1. **Application metrics** (Prometheus, DataDog, New Relic)
2. **Log aggregation** (ELK Stack, Splunk, CloudWatch)
3. **Error tracking** (Sentry, Rollbar)
4. **Uptime monitoring** (Pingdom, UptimeRobot)
5. **Performance monitoring** (APM tools)
6. **User analytics**
7. **Set up alerts**
8. **Dashboard for key metrics**

### Cost Optimization

1. **Right-size your resources**
2. **Use auto-scaling**
3. **Implement caching**
4. **Use spot instances (AWS)**
5. **Schedule non-critical workloads**
6. **Monitor and optimize database queries**
7. **Use serverless for variable workloads**
8. **Review and remove unused resources**

---

## Summary

You've learned how to:

✅ Configure environment variables securely  
✅ Dockerize FastAPI applications  
✅ Set up NGINX as a reverse proxy  
✅ Implement structured logging and monitoring  
✅ Create CI/CD pipelines with GitHub Actions and GitLab CI  
✅ Deploy to AWS (EB, ECS, Lambda)  
✅ Deploy to Azure (App Service, ACI)  
✅ Deploy to GCP (Cloud Run, App Engine)  
✅ Deploy to Render  
✅ Deploy to Railway  

### Next Steps

1. Choose your deployment platform
2. Set up CI/CD pipeline
3. Configure monitoring and alerts
4. Implement security best practices
5. Optimize for performance
6. Plan for scaling

### Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [NGINX Documentation](https://nginx.org/en/docs/)
- [The Twelve-Factor App](https://12factor.net/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

**Happy Deploying! 🚀**
