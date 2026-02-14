
"""
Production-Ready FastAPI Application
Demonstrates best practices for production deployment including:
- Environment variables
- Structured logging
- Health checks
- CORS configuration
- Error handling
- Request ID tracking
"""

import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# ========== Configuration ==========
class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    app_name: str = "FastAPI Production App"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", alias="ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # CORS settings
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    
    # Database settings (example)
    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Security
    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


# ========== Logging Configuration ==========
def setup_logging():
    """Configure structured logging for production"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # JSON logging for production
    if settings.environment == "production":
        log_format = '{"time":"%(asctime)s", "name":"%(name)s", "level":"%(levelname)s", "message":"%(message)s"}'
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure uvicorn logger
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []


setup_logging()
logger = logging.getLogger(__name__)


# ========== Lifespan Events ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize resources (database connections, cache, etc.)
    # await database.connect()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    # Clean up resources
    # await database.disconnect()


# ========== FastAPI Application ==========
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready FastAPI application with best practices",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    lifespan=lifespan
)


# ========== Middleware ==========
# CORS Middleware
origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID and Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Add request ID and log all requests"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    logger.info(
        f"Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None
        }
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(
        f"Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s"
        }
    )
    
    return response


# ========== Models ==========
class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    timestamp: str


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)


class Item(ItemCreate):
    id: str
    created_at: str


class MessageResponse(BaseModel):
    message: str
    request_id: str


# ========== In-memory storage (replace with database in production) ==========
items_db = {}


# ========== Endpoints ==========
@app.get("/", response_model=MessageResponse)
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "request_id": request.state.request_id
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring tools
    Should check database connections, external services, etc.
    """
    # In production, check database connection, cache, etc.
    # try:
    #     await database.execute("SELECT 1")
    # except Exception:
    #     raise HTTPException(status_code=503, detail="Database unavailable")
    
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/ready", tags=["Monitoring"])
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes and orchestrators
    Returns 200 when app is ready to accept traffic
    """
    return {"status": "ready"}


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Metrics endpoint for Prometheus or other monitoring systems
    In production, use prometheus_client or similar
    """
    return {
        "items_count": len(items_db),
        "uptime": "N/A"  # Calculate actual uptime
    }


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item: ItemCreate, request: Request):
    """Create a new item"""
    item_id = str(uuid.uuid4())
    
    new_item = Item(
        id=item_id,
        name=item.name,
        description=item.description,
        price=item.price,
        created_at=datetime.utcnow().isoformat()
    )
    
    items_db[item_id] = new_item
    
    logger.info(
        f"Item created",
        extra={
            "request_id": request.state.request_id,
            "item_id": item_id,
            "item_name": item.name
        }
    )
    
    return new_item


@app.get("/items", response_model=list[Item], tags=["Items"])
async def list_items():
    """List all items"""
    return list(items_db.values())


@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: str):
    """Get a specific item"""
    if item_id not in items_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Item {item_id} not found"}
        )
    
    return items_db[item_id]


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
async def delete_item(item_id: str, request: Request):
    """Delete an item"""
    if item_id not in items_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Item {item_id} not found"}
        )
    
    del items_db[item_id]
    
    logger.info(
        f"Item deleted",
        extra={
            "request_id": request.state.request_id,
            "item_id": item_id
        }
    )
    
    return None


# ========== Error Handlers ==========
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Unhandled exception",
        extra={
            "request_id": request_id,
            "error": str(exc),
            "path": request.url.path
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request_id
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "12_production_api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
