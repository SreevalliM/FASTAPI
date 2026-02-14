# Module 12: Production Deployment

Learn how to deploy FastAPI applications to production with Docker, NGINX, CI/CD, and multiple cloud platforms.

## 📚 What You'll Learn

- **Environment Variables**: Secure configuration management with Pydantic Settings
- **Dockerization**: Multi-stage builds, Docker Compose, container optimization
- **NGINX**: Reverse proxy, load balancing, SSL/TLS, rate limiting
- **Logging & Monitoring**: Structured logging, health checks, metrics, error tracking
- **CI/CD**: GitHub Actions and GitLab CI pipelines
- **Cloud Deployment**: Deploy to AWS, Azure, GCP, Render, and Railway

## 📁 Module Structure

```
12_production_deployment/
├── 12_production_api.py              # Production-ready FastAPI app
├── Dockerfile                         # Multi-stage production Dockerfile
├── Dockerfile.dev                     # Development Dockerfile
├── docker-compose.yml                 # Production Docker Compose
├── docker-compose.dev.yml            # Development Docker Compose
├── nginx.conf                         # NGINX reverse proxy configuration
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .dockerignore                      # Docker ignore file
├── .github-workflows-ci-cd.yml       # GitHub Actions CI/CD pipeline
├── .gitlab-ci.yml                    # GitLab CI/CD pipeline
├── 12_PRODUCTION_DEPLOYMENT_TUTORIAL.md  # Comprehensive tutorial
├── DEPLOYMENT_CHEATSHEET.md          # Quick reference guide
├── README.md                          # This file
├── quickstart.sh                      # Quick start script
├── test_production_api.py            # Test suite
├── manual_test.py                     # Manual testing script
└── deploy/                            # Deployment configurations
    ├── aws/                           # AWS deployment files
    ├── azure/                         # Azure deployment files
    ├── gcp/                           # GCP deployment files
    ├── render/                        # Render configuration
    └── railway/                       # Railway configuration
```

## 🚀 Quick Start

### Option 1: Local Development

```bash
# Create environment file
cp .env.example .env

# Run with Docker Compose
docker-compose -f docker-compose.dev.yml up

# Access the API
open http://localhost:8000
open http://localhost:8000/api/docs
```

### Option 2: Production Mode

```bash
# Build and run production containers
docker-compose up -d

# View logs
docker-compose logs -f api

# Test the API
curl http://localhost:8000/health
```

### Option 3: Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ENV=development
export DEBUG=true

# Run the server
python 12_production_api.py
```

## 🎯 Learning Path

Follow this sequence for the best learning experience:

1. **Start with the Tutorial** (`12_PRODUCTION_DEPLOYMENT_TUTORIAL.md`)
   - Read through all sections
   - Understand the concepts
   
2. **Explore the Production API** (`12_production_api.py`)
   - Study the code structure
   - Understand middleware, logging, health checks
   
3. **Practice with Docker**
   - Build the Docker image
   - Run with Docker Compose
   - Experiment with different configurations
   
4. **Configure NGINX**
   - Study `nginx.conf`
   - Test reverse proxy functionality
   - Implement rate limiting
   
5. **Set Up CI/CD**
   - Choose GitHub Actions or GitLab CI
   - Configure secrets
   - Run the pipeline
   
6. **Deploy to Cloud**
   - Choose a platform (Render is easiest to start)
   - Follow platform-specific guide
   - Monitor the deployment

## 📖 Module Contents

### 1. Production API (`12_production_api.py`)

A complete production-ready FastAPI application with:
- Environment variable configuration
- Structured logging
- Request ID tracking
- Health check endpoints
- Error handling
- CORS middleware
- Metrics endpoint

**Key Features:**
```python
# Environment configuration
settings = Settings()

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application")
    yield
    # Shutdown
    logger.info("Shutting down")

# Health checks
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 2. Docker Configuration

**Multi-stage Dockerfile:**
- Stage 1: Build dependencies
- Stage 2: Lightweight runtime
- Non-root user for security
- Health checks built-in

**Docker Compose:**
- FastAPI application
- PostgreSQL database
- Redis cache
- NGINX reverse proxy

### 3. NGINX Configuration

- Reverse proxy setup
- Load balancing
- SSL/TLS termination
- Rate limiting
- Caching strategies
- Security headers

### 4. CI/CD Pipelines

**GitHub Actions:**
- Test on multiple Python versions
- Code linting
- Docker build and push
- Automatic deployment

**GitLab CI:**
- Parallel testing
- Docker registry integration
- Multi-environment deployment
- Manual approval gates

### 5. Cloud Deployment Guides

Each platform includes:
- Configuration files
- Deployment scripts
- Environment setup
- Monitoring configuration

**Platforms covered:**
- **AWS**: Elastic Beanstalk, ECS, Lambda
- **Azure**: App Service, Container Instances
- **GCP**: Cloud Run, App Engine
- **Render**: Zero-config deployment
- **Railway**: Instant deployment

## 🛠️ Common Commands

### Docker Commands
```bash
# Build image
docker build -t fastapi-app .

# Run container
docker run -d -p 8000:8000 --env-file .env fastapi-app

# Docker Compose
docker-compose up -d              # Start
docker-compose down               # Stop
docker-compose logs -f api        # Logs
docker-compose exec api sh        # Shell
```

### Testing
```bash
# Run tests
pytest test_production_api.py -v

# With coverage
pytest test_production_api.py -v --cov=.

# Manual testing
python manual_test.py
```

### Deployment
```bash
# AWS
eb init && eb create && eb deploy

# Azure
az webapp up --runtime PYTHON:3.11

# GCP
gcloud run deploy --source .

# Render/Railway
git push origin main  # Auto-deploy from Git
```

## 📊 Health Checks & Monitoring

The application includes three monitoring endpoints:

- **`/health`**: Health check for load balancers
- **`/ready`**: Readiness check for Kubernetes
- **`/metrics`**: Metrics for Prometheus

Example:
```bash
curl http://localhost:8000/health
# {"status":"healthy","environment":"production","version":"1.0.0"}
```

## 🔒 Security Features

- Environment-based configuration
- CORS properly configured
- Security headers via NGINX
- Non-root Docker user
- Rate limiting
- Request ID tracking
- Structured logging for auditing

## 📈 Performance Features

- Multiple worker processes
- Async/await throughout
- Connection pooling ready
- Response compression (via NGINX)
- Caching strategies
- Load balancing via NGINX

## 🐛 Troubleshooting

### Container won't start
```bash
docker logs container-id
# Check environment variables
# Verify port availability
```

### Database connection fails
```bash
# Check DATABASE_URL format
# Verify database is running
docker-compose ps
```

### NGINX issues
```bash
# Test configuration
nginx -t

# View error logs
docker-compose logs nginx
```

## 📚 Additional Resources

- **Tutorial**: Complete deployment guide with examples
- **Cheatsheet**: Quick reference for all commands
- **CI/CD Examples**: Production-ready pipeline configurations
- **Platform Guides**: Specific instructions for each cloud provider

## 🎓 Learning Outcomes

After completing this module, you will be able to:

✅ Configure production-ready FastAPI applications  
✅ Containerize applications with Docker  
✅ Set up NGINX as a reverse proxy  
✅ Implement structured logging and monitoring  
✅ Create CI/CD pipelines  
✅ Deploy to multiple cloud platforms  
✅ Implement security best practices  
✅ Monitor and troubleshoot production applications  
✅ Scale applications horizontally  
✅ Implement zero-downtime deployments  

## 🔗 Related Modules

- **Module 10**: Scalable APIs (async patterns, production deployment basics)
- **Module 11**: Testing with Pytest (test strategies used in CI/CD)

## 💡 Tips

1. **Start simple**: Begin with Render or Railway for easiest deployment
2. **Test locally**: Use docker-compose.dev.yml for development
3. **Monitor everything**: Set up logging and monitoring from day one
4. **Security first**: Never commit secrets, always use environment variables
5. **Automate deployment**: Set up CI/CD early in your project

## 🆘 Need Help?

- Check the **Tutorial** for detailed explanations
- Reference the **Cheatsheet** for quick commands
- Review `12_production_api.py` for implementation examples
- Test with `manual_test.py` to verify functionality

## 📝 Next Steps

1. Complete the tutorial
2. Deploy to at least one platform
3. Set up CI/CD pipeline
4. Configure monitoring and alerts
5. Implement your own production application using these patterns

---

**Ready to deploy?** Start with `./quickstart.sh` or dive into the tutorial!

**Questions?** Review the comprehensive tutorial and cheatsheet for answers.

**Happy Deploying! 🚀**
