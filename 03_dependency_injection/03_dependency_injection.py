"""
FastAPI Dependency Injection - User Management API
Demonstrates: Depends(), reusable logic, shared DB sessions, security, logging, rate-limiting

Dependency Injection Benefits:
1. Code reusability - Write once, use everywhere
2. Shared resources - DB connections, configurations, loggers
3. Security - Authentication, authorization checks
4. Testing - Easy to mock dependencies
"""

from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Annotated, Dict
from datetime import datetime, timedelta
import logging
import re
from collections import defaultdict

# ==================== FastAPI App ====================

app = FastAPI(
    title="User Management API with Dependency Injection",
    description="Learn Depends(), shared resources, security, logging, and rate-limiting",
    version="1.0.0"
)

# ==================== Logging Setup ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== In-Memory Databases ====================

# User database
users_db: Dict[int, dict] = {}
user_counter = 0

# Rate limiting storage (stores IP -> list of request timestamps)
rate_limit_storage: Dict[str, List[datetime]] = defaultdict(list)

# API key storage (for security)
API_KEYS = {
    "admin_key_123": {"username": "admin", "role": "admin"},
    "user_key_456": {"username": "john_doe", "role": "user"},
}

# ==================== Pydantic Models ====================

class UserCreate(BaseModel):
    """Model for creating a user"""
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: EmailStr = Field(..., description="Valid email address")
    age: int = Field(..., ge=18, le=120, description="Age must be between 18 and 120")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 chars)")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Custom validator: name should not contain numbers"""
        if any(char.isdigit() for char in v):
            raise ValueError("Name should not contain numbers")
        return v.strip()

class UserResponse(BaseModel):
    """Response model (excludes password)"""
    id: int
    name: str
    email: str
    age: int
    created_at: datetime
    last_login: Optional[datetime] = None

class UserUpdate(BaseModel):
    """Model for updating user info"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    age: Optional[int] = Field(None, ge=18, le=120)

# ==================== DEPENDENCY 1: Logging Dependency ====================

class LoggingDependency:
    """
    Shared logging dependency - logs every request
    This is a CLASS-BASED dependency (will be instantiated)
    """
    
    def __call__(self, request: Request):
        """Called for every request that uses this dependency"""
        logger.info(f"📥 Request: {request.method} {request.url.path}")
        logger.info(f"🌐 Client IP: {request.client.host}")
        return {
            "timestamp": datetime.now(),
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host
        }

# Create a single instance (shared across all requests)
log_request = LoggingDependency()

# ==================== DEPENDENCY 2: Database Session ====================

class DatabaseSession:
    """
    Simulates a database session
    In real apps, this would be SQLAlchemy session or database connection
    """
    
    def __init__(self):
        self.connected = True
        logger.info("🔌 Database session created")
    
    def close(self):
        self.connected = False
        logger.info("🔌 Database session closed")

def get_db():
    """
    Database dependency - yields a session and ensures cleanup
    This is a GENERATOR-BASED dependency (runs cleanup code after request)
    """
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()

# ==================== DEPENDENCY 3: Rate Limiting ====================

class RateLimiter:
    """
    Rate limiting dependency - limits requests per IP address
    Prevents abuse by limiting to N requests per time window
    """
    
    def __init__(self, requests: int = 10, window_seconds: int = 60):
        """
        Args:
            requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = requests
        self.window = timedelta(seconds=window_seconds)
    
    def __call__(self, request: Request):
        """Check if client has exceeded rate limit"""
        client_ip = request.client.host
        now = datetime.now()
        
        # Get request history for this IP
        request_history = rate_limit_storage[client_ip]
        
        # Remove old requests outside the time window
        request_history[:] = [
            timestamp for timestamp in request_history 
            if now - timestamp < self.window
        ]
        
        # Check if limit exceeded
        if len(request_history) >= self.max_requests:
            logger.warning(f"⚠️  Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window.seconds} seconds."
            )
        
        # Add current request to history
        request_history.append(now)
        logger.info(f"✅ Rate limit check passed: {len(request_history)}/{self.max_requests} requests")
        
        return {
            "requests_remaining": self.max_requests - len(request_history),
            "window_seconds": self.window.seconds
        }

# Create rate limiter instances with different limits
rate_limiter_strict = RateLimiter(requests=5, window_seconds=60)  # 5 requests per minute
rate_limiter_normal = RateLimiter(requests=10, window_seconds=60)  # 10 requests per minute

# ==================== DEPENDENCY 4: Security (API Key) ====================

def verify_api_key(api_key: Annotated[str, Header(description="API Key for authentication")]):
    """
    Security dependency - validates API key from header
    This is a FUNCTION-BASED dependency
    
    Usage: Add 'api_key' header to your requests
    """
    if api_key not in API_KEYS:
        logger.warning(f"🚫 Invalid API key attempted: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    user_info = API_KEYS[api_key]
    logger.info(f"🔐 Authenticated user: {user_info['username']} (role: {user_info['role']})")
    return user_info

# ==================== DEPENDENCY 5: Authorization (Admin Only) ====================

def verify_admin(user_info: dict = Depends(verify_api_key)):
    """
    Authorization dependency - checks if user is admin
    This depends on verify_api_key (DEPENDENCY CHAINING)
    """
    if user_info.get("role") != "admin":
        logger.warning(f"🚫 Unauthorized admin access attempt by: {user_info['username']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    logger.info(f"✅ Admin access granted: {user_info['username']}")
    return user_info

# ==================== DEPENDENCY 6: Email Validation ====================

def validate_email_domain(email: str) -> bool:
    """
    Dependency function to validate email domain
    Can be used as a reusable validation logic
    """
    # List of allowed domains (for demonstration)
    allowed_domains = ["gmail.com", "outlook.com", "company.com", "example.com"]
    
    domain = email.split("@")[-1].lower()
    
    if domain not in allowed_domains:
        logger.warning(f"⚠️  Rejected email domain: {domain}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email domain '{domain}' not allowed. Allowed domains: {', '.join(allowed_domains)}"
        )
    
    logger.info(f"✅ Email domain validated: {domain}")
    return True

# ==================== UTILITY FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Simulate password hashing (in real apps, use bcrypt/passlib)"""
    return f"hashed_{password}_salted"

# ==================== API ENDPOINTS ====================

@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint with API information"""
    return {
        "message": "🎓 User Management API - Dependency Injection Tutorial",
        "features": [
            "✅ Shared logging dependency",
            "✅ Rate limiting",
            "✅ API key authentication",
            "✅ Admin authorization",
            "✅ Email domain validation",
            "✅ Database session management"
        ],
        "docs": "/docs",
        "test_api_keys": {
            "admin": "admin_key_123",
            "user": "user_key_456"
        }
    }

# ==================== USER ENDPOINTS ====================

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Create a new user"
)
def create_user(
    user: UserCreate,
    log_info: dict = Depends(log_request),  # Logs the request
    rate_limit: dict = Depends(rate_limiter_normal),  # Rate limiting
    db: DatabaseSession = Depends(get_db),  # Database session
):
    """
    Create a new user with all validations
    
    **Dependencies Used:**
    - `log_request`: Logs request details
    - `rate_limiter_normal`: 10 requests per minute
    - `get_db`: Database session management
    
    **Validations:**
    - Name: 2-50 chars, no numbers
    - Email: Valid email format
    - Age: 18-120
    - Password: Min 8 chars
    """
    global user_counter
    
    # Validate email domain
    validate_email_domain(user.email)
    
    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user.email}' already registered"
            )
    
    # Create user
    user_counter += 1
    new_user = {
        "id": user_counter,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "password": hash_password(user.password),
        "created_at": datetime.now(),
        "last_login": None
    }
    
    users_db[user_counter] = new_user
    
    logger.info(f"✅ User created: {user.email} (ID: {user_counter})")
    
    # Return user without password
    return UserResponse(**{k: v for k, v in new_user.items() if k != "password"})

@app.get(
    "/users",
    response_model=List[UserResponse],
    tags=["Users"],
    summary="Get all users"
)
def list_users(
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    log_info: dict = Depends(log_request),
    rate_limit: dict = Depends(rate_limiter_normal),
    api_key: dict = Depends(verify_api_key),  # Requires authentication
    db: DatabaseSession = Depends(get_db),
):
    """
    Get list of all users (requires authentication)
    
    **Dependencies Used:**
    - `log_request`: Logs request
    - `rate_limiter_normal`: Rate limiting
    - `verify_api_key`: API key authentication required
    - `get_db`: Database session
    
    **Headers Required:**
    - `api_key`: Your API key (admin_key_123 or user_key_456)
    """
    users = list(users_db.values())[:limit]
    
    # Remove passwords from response
    users_response = [
        UserResponse(**{k: v for k, v in user.items() if k != "password"})
        for user in users
    ]
    
    logger.info(f"📋 Returned {len(users_response)} users to {api_key['username']}")
    return users_response

@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get user by ID"
)
def get_user(
    user_id: int,
    log_info: dict = Depends(log_request),
    rate_limit: dict = Depends(rate_limiter_normal),
    api_key: dict = Depends(verify_api_key),
    db: DatabaseSession = Depends(get_db),
):
    """
    Get a specific user by ID (requires authentication)
    
    **Dependencies Used:**
    - Authentication required
    - Rate limiting applied
    - Request logging
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    user = users_db[user_id]
    logger.info(f"👤 User {user_id} retrieved by {api_key['username']}")
    
    return UserResponse(**{k: v for k, v in user.items() if k != "password"})

@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Update user (Admin only)"
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    log_info: dict = Depends(log_request),
    rate_limit: dict = Depends(rate_limiter_strict),  # Stricter rate limit for updates
    admin: dict = Depends(verify_admin),  # Admin only (dependency chaining)
    db: DatabaseSession = Depends(get_db),
):
    """
    Update user information (ADMIN ONLY)
    
    **Dependencies Used:**
    - `verify_admin`: Requires admin role (chains verify_api_key)
    - `rate_limiter_strict`: 5 requests per minute (stricter)
    
    **Authorization:**
    - Only users with role='admin' can update users
    - Use API key: admin_key_123
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    user = users_db[user_id]
    
    # Update only provided fields
    if user_update.name is not None:
        user["name"] = user_update.name
    if user_update.age is not None:
        user["age"] = user_update.age
    
    logger.info(f"✏️  User {user_id} updated by admin: {admin['username']}")
    
    return UserResponse(**{k: v for k, v in user.items() if k != "password"})

@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Users"],
    summary="Delete user (Admin only)"
)
def delete_user(
    user_id: int,
    log_info: dict = Depends(log_request),
    rate_limit: dict = Depends(rate_limiter_strict),
    admin: dict = Depends(verify_admin),  # Admin only
    db: DatabaseSession = Depends(get_db),
):
    """
    Delete a user (ADMIN ONLY)
    
    **Dependencies Used:**
    - Admin authorization required
    - Strict rate limiting
    
    **Authorization:**
    - Only admins can delete users
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    deleted_user = users_db.pop(user_id)
    logger.info(f"🗑️  User {user_id} ({deleted_user['email']}) deleted by admin: {admin['username']}")
    
    return None

# ==================== UTILITY ENDPOINTS ====================

@app.get("/rate-limit-status", tags=["Utility"])
def get_rate_limit_status(
    request: Request,
    log_info: dict = Depends(log_request)
):
    """
    Check your current rate limit status (no rate limit on this endpoint)
    Shows how many requests you've made recently
    """
    client_ip = request.client.host
    now = datetime.now()
    
    # Clean up old requests
    request_history = rate_limit_storage.get(client_ip, [])
    recent_requests = [
        timestamp for timestamp in request_history
        if now - timestamp < timedelta(seconds=60)
    ]
    
    return {
        "your_ip": client_ip,
        "requests_last_minute": len(recent_requests),
        "normal_limit": "10 requests/minute",
        "strict_limit": "5 requests/minute (admin operations)",
        "request_timestamps": [ts.isoformat() for ts in recent_requests[-5:]]
    }

@app.get("/stats", tags=["Utility"])
def get_stats(
    log_info: dict = Depends(log_request),
    api_key: dict = Depends(verify_api_key)
):
    """
    Get API statistics (requires authentication)
    """
    return {
        "total_users": len(users_db),
        "authenticated_as": api_key["username"],
        "role": api_key["role"],
        "database_connected": True,
        "timestamp": datetime.now().isoformat()
    }

# ==================== LEARNING EXAMPLES ====================

@app.get("/learn/simple-dependency", tags=["Learning"])
def simple_dependency_example(common_param: str = Depends(lambda: "I'm a simple dependency!")):
    """
    Example 1: Simple function dependency
    The lambda function runs before this endpoint
    """
    return {"dependency_result": common_param}

@app.get("/learn/multiple-dependencies", tags=["Learning"])
def multiple_dependencies_example(
    log: dict = Depends(log_request),
    rate: dict = Depends(rate_limiter_normal),
):
    """
    Example 2: Multiple dependencies
    Both dependencies run before the endpoint
    """
    return {
        "log_info": log,
        "rate_limit_info": rate,
        "message": "Multiple dependencies executed!"
    }

@app.get("/learn/chained-dependencies", tags=["Learning"])
def chained_dependency_example(
    admin: dict = Depends(verify_admin)  # verify_admin depends on verify_api_key
):
    """
    Example 3: Dependency chaining
    verify_admin calls verify_api_key automatically
    """
    return {
        "message": "Dependency chaining works!",
        "admin_info": admin
    }

# ==================== RUN INSTRUCTIONS ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 Starting User Management API with Dependency Injection")
    print("="*70)
    print("\n📚 KEY CONCEPTS:")
    print("   1. Depends() - Injects reusable logic")
    print("   2. Logging - Shared logging dependency")
    print("   3. Rate Limiting - Prevents abuse")
    print("   4. Authentication - API key validation")
    print("   5. Authorization - Role-based access")
    print("   6. Database Sessions - Simulated DB connections")
    print("\n🔑 TEST API KEYS:")
    print("   Admin: admin_key_123")
    print("   User:  user_key_456")
    print("\n📖 Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
