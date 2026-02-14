"""
Production-Grade REST API
==========================
Task Management API with PostgreSQL, Redis caching, and monitoring
"""
import os
import time
import logging
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
import redis
import json

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/taskdb")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = None

# Database Models
class Task(Base):
    """Task database model"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, index=True)
    priority = Column(String(20), default="medium", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")

class TaskResponse(TaskBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    timestamp: datetime

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global redis_client
    
    # Startup
    logger.info("Starting Production REST API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Connect to Redis
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        redis_client = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if redis_client:
        redis_client.close()

# Initialize FastAPI
app = FastAPI(
    title="Production REST API",
    description="Task Management API with PostgreSQL, Redis, and monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s "
        f"with status {response.status_code}"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Dependencies
def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Redis dependency"""
    if redis_client is None:
        return None
    return redis_client

# Cache utilities
def get_cache_key(prefix: str, identifier: str) -> str:
    """Generate cache key"""
    return f"{prefix}:{identifier}"

def cache_get(key: str):
    """Get from cache"""
    if redis_client is None:
        return None
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.error(f"Cache get error: {e}")
    return None

def cache_set(key: str, value: dict, ttl: int = CACHE_TTL):
    """Set cache"""
    if redis_client is None:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        logger.error(f"Cache set error: {e}")

def cache_delete(key_pattern: str):
    """Delete cache keys matching pattern"""
    if redis_client is None:
        return
    try:
        keys = redis_client.keys(key_pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        logger.error(f"Cache delete error: {e}")

# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Production REST API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check Redis
    redis_status = "healthy" if redis_client else "unavailable"
    if redis_client:
        try:
            redis_client.ping()
        except Exception:
            redis_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
        timestamp=datetime.utcnow()
    )

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new task"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Invalidate list cache in background
    background_tasks.add_task(cache_delete, "tasks:list:*")
    
    logger.info(f"Created task: {db_task.id}")
    return db_task

@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List tasks with pagination and filtering"""
    # Generate cache key
    cache_key = get_cache_key(
        "tasks:list",
        f"{skip}:{limit}:{completed}:{priority}"
    )
    
    # Try cache first
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Cache hit: {cache_key}")
        return cached
    
    # Query database
    query = db.query(Task)
    
    if completed is not None:
        query = query.filter(Task.completed == completed)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    tasks = query.offset(skip).limit(limit).all()
    
    # Convert to dict for caching
    tasks_dict = [TaskResponse.from_orm(task).dict() for task in tasks]
    
    # Cache result
    cache_set(cache_key, tasks_dict)
    
    logger.info(f"Database query: {len(tasks)} tasks")
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task"""
    # Try cache first
    cache_key = get_cache_key("task", str(task_id))
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Cache hit: {cache_key}")
        return cached
    
    # Query database
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Cache result
    task_dict = TaskResponse.from_orm(task).dict()
    cache_set(cache_key, task_dict)
    
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    
    # Invalidate caches in background
    background_tasks.add_task(cache_delete, f"task:{task_id}")
    background_tasks.add_task(cache_delete, "tasks:list:*")
    
    logger.info(f"Updated task: {task_id}")
    return db_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Delete a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    db.delete(db_task)
    db.commit()
    
    # Invalidate caches in background
    background_tasks.add_task(cache_delete, f"task:{task_id}")
    background_tasks.add_task(cache_delete, "tasks:list:*")
    
    logger.info(f"Deleted task: {task_id}")
    return None

@app.get("/stats", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Get task statistics"""
    cache_key = "stats:tasks"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    total = db.query(Task).count()
    completed = db.query(Task).filter(Task.completed == True).count()
    pending = total - completed
    
    by_priority = {
        "low": db.query(Task).filter(Task.priority == "low").count(),
        "medium": db.query(Task).filter(Task.priority == "medium").count(),
        "high": db.query(Task).filter(Task.priority == "high").count(),
    }
    
    stats = {
        "total_tasks": total,
        "completed": completed,
        "pending": pending,
        "by_priority": by_priority,
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 2)
    }
    
    # Cache for shorter time
    cache_set(cache_key, stats, ttl=60)
    
    return stats

@app.post("/cache/clear", tags=["Admin"])
async def clear_cache():
    """Clear all cache (admin endpoint)"""
    if redis_client is None:
        return {"message": "Redis not available"}
    
    try:
        redis_client.flushdb()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {e}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
