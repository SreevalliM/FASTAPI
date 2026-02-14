# 🎓 FastAPI Advanced Projects

Three production-ready FastAPI projects demonstrating professional development practices.

## 📁 Projects Overview

### 🥇 [Project 1: Auth Service](14_auth_service/)
**JWT Authentication with RBAC**

Complete authentication service with industry-standard security.

**Features:**
- ✅ JWT Access Tokens (30 min expiry)
- ✅ Refresh Tokens (7 day expiry with rotation)
- ✅ Role-Based Access Control (Admin, Manager, User)
- ✅ Bcrypt Password Hashing
- ✅ Token Revocation on Logout
- ✅ Comprehensive Test Suite

**Tech Stack:** FastAPI, python-jose, passlib, bcrypt

**Use Cases:** User management systems, secure APIs, multi-tenant applications

[View Documentation →](14_auth_service/README.md)

---

### 🥈 [Project 2: ML Inference API](15_ml_api/)
**Async Machine Learning API**

Production ML API with async inference and background logging.

**Features:**
- ✅ Async Inference (5-7x faster than sync)
- ✅ Batch Predictions with Parallel Processing
- ✅ Background Logging (non-blocking)
- ✅ Model Hot-Swapping
- ✅ Docker Deployment
- ✅ Health Monitoring & Statistics

**Tech Stack:** FastAPI, NumPy, scikit-learn, Docker

**Use Cases:** Real-time predictions, batch processing, model serving

[View Documentation →](15_ml_api/README.md)

---

### 🥉 [Project 3: Production REST API](16_production_api/)
**Enterprise-Grade Task Management API**

Full-stack production API with database, caching, and monitoring.

**Features:**
- ✅ PostgreSQL with SQLAlchemy ORM
- ✅ Alembic Database Migrations
- ✅ Redis Caching Layer
- ✅ Docker & Docker Compose
- ✅ CI/CD Pipeline (GitHub Actions)
- ✅ Prometheus + Grafana Monitoring
- ✅ Comprehensive Testing

**Tech Stack:** FastAPI, PostgreSQL, Redis, Alembic, Docker, Prometheus, Grafana

**Use Cases:** Production APIs, scalable microservices, containerized deployments

[View Documentation →](16_production_api/README.md)

---

## 🚀 Quick Start Guide

### Prerequisites
```bash
# Required
- Python 3.11+
- Docker & Docker Compose

# Optional (for local development)
- PostgreSQL 16+
- Redis 7+
```

### Run All Projects

#### Project 1: Auth Service
```bash
cd 14_auth_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

#### Project 2: ML API
```bash
cd 15_ml_api
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
# Or with Docker:
docker-compose up --build
# Docs: http://localhost:8001/docs
```

#### Project 3: Production API
```bash
cd 16_production_api
docker-compose up --build
# API: http://localhost:8000/docs
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

---

## 📊 Feature Comparison

| Feature | Auth Service | ML API | Production API |
|---------|-------------|---------|----------------|
| **Authentication** | ✅ Full | ⚠️ Ready to add | ⚠️ Ready to add |
| **Database** | 💾 In-memory | 💾 Model storage | ✅ PostgreSQL |
| **Caching** | ❌ | ❌ | ✅ Redis |
| **Async** | ✅ Partial | ✅ Full | ✅ Partial |
| **Docker** | ⚠️ Ready | ✅ Complete | ✅ Complete |
| **Migrations** | ❌ | ❌ | ✅ Alembic |
| **CI/CD** | ⚠️ Ready | ⚠️ Ready | ✅ GitHub Actions |
| **Monitoring** | ❌ | ✅ Logging | ✅ Prometheus/Grafana |
| **Testing** | ✅ Complete | ✅ Complete | ✅ Complete |

---

## 🎯 Learning Path

### Beginner → Intermediate
1. Start with **Auth Service** to learn security fundamentals
2. Study JWT tokens, password hashing, and RBAC
3. Run tests to understand authentication flows

### Intermediate → Advanced
4. Move to **ML API** for async programming
5. Learn background tasks and parallel processing
6. Understand Docker containerization

### Advanced → Production
7. Dive into **Production API** for full-stack deployment
8. Master databases, migrations, and caching
9. Set up monitoring and CI/CD pipelines

---

## 🧪 Testing All Projects

```bash
# Test Auth Service
cd 14_auth_service
pytest test_auth.py -v --cov=main

# Test ML API
cd 15_ml_api
pytest test_ml_api.py -v --cov=main

# Test Production API
cd 16_production_api
pytest test_production_api.py -v --cov=main
```

---

## 📚 Key Concepts Covered

### Security & Authentication
- JWT token generation and validation
- Refresh token rotation
- Password hashing (bcrypt)
- Role-based access control (RBAC)
- Token revocation

### Async Programming
- Async/await patterns
- Concurrent request handling
- Background tasks
- Parallel batch processing

### Database Management
- SQLAlchemy ORM
- Database migrations (Alembic)
- Connection pooling
- Query optimization
- Indexes

### Caching
- Redis integration
- Cache invalidation strategies
- TTL management
- Cache key patterns

### DevOps
- Docker containerization
- Docker Compose orchestration
- Multi-stage builds
- Health checks
- CI/CD pipelines

### Monitoring & Logging
- Request/response logging
- Prometheus metrics
- Grafana dashboards
- Health check endpoints
- Performance monitoring

---

## 🔗 Integration Examples

### Combine Auth + ML API
```python
# Add authentication to ML API
from auth_service import get_current_user, require_user

@app.post("/predict")
async def predict(
    input_data: PredictionInput,
    user: User = Depends(require_user)  # Add auth
):
    # Only authenticated users can make predictions
    prediction = await model.predict(input_data.features)
    return {"prediction": prediction, "user": user.username}
```

### Add ML Predictions to Production API
```python
# Add ML endpoint to production API
@app.post("/tasks/{task_id}/predict-completion")
async def predict_task_completion(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    # Extract features from task
    features = extract_task_features(task)
    # Call ML model
    prediction = await ml_model.predict(features)
    return {"task_id": task_id, "completion_probability": prediction}
```

---

## 🏆 Production Checklist

Before deploying to production, ensure:

- [ ] Environment variables configured
- [ ] Database backups enabled
- [ ] HTTPS/TLS configured
- [ ] CORS properly set up
- [ ] Rate limiting implemented
- [ ] Logging configured (ELK, CloudWatch, etc.)
- [ ] Monitoring alerts set up
- [ ] CI/CD pipeline tested
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation updated
- [ ] Error tracking (Sentry, etc.)

---

## 📖 Additional Resources

### Official Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Documentation](https://docs.docker.com/)

### Best Practices
- [12-Factor App](https://12factor.net/)
- [REST API Design](https://restfulapi.net/)
- [OWASP Security](https://owasp.org/www-project-api-security/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Community
- [FastAPI GitHub](https://github.com/tiangolo/fastapi)
- [FastAPI Discord](https://discord.gg/fastapi)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/fastapi)

---

## 🎯 Next Steps

### Extend These Projects
1. **Auth Service**
   - Add OAuth2 providers (Google, GitHub)
   - Implement 2FA
   - Add email verification
   - Password reset flow

2. **ML API**
   - Add TensorFlow/PyTorch models
   - Implement streaming predictions
   - Add model A/B testing
   - SHAP explainability

3. **Production API**
   - Add WebSocket support
   - Implement GraphQL endpoint
   - Add file upload/download
   - Implement soft deletes

### Build New Projects
- **E-commerce API**: Combine all three projects
- **Social Media API**: Real-time feeds with caching
- **Analytics Dashboard**: Time-series data with PostgreSQL
- **Microservices**: Split into multiple services

---

## 🤝 Contributing

Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests
- Share your implementations

---

## 📝 License

MIT License - Use these projects for learning or production!

---

## ⭐ Summary

You now have three production-ready FastAPI projects covering:
1. **Security**: JWT authentication and RBAC
2. **Performance**: Async inference and caching
3. **Infrastructure**: Database, Docker, CI/CD, monitoring

Each project is fully functional, tested, and documented. Use them as:
- Learning resources
- Project templates
- Production starters
- Portfolio pieces

**Happy coding! 🚀**
