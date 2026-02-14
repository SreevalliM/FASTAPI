"""
Auth Service with JWT, Refresh Tokens, RBAC, and Password Hashing
==================================================================
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, use environment variable
REFRESH_SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Initialize FastAPI
app = FastAPI(title="Auth Service", version="1.0.0")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory database (replace with real DB in production)
users_db = {}
refresh_tokens_db = {}

# Models
class UserRole(str):
    """User roles for RBAC"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = UserRole.USER

class UserResponse(BaseModel):
    username: str
    email: str
    role: str
    disabled: bool = False

class User(BaseModel):
    username: str
    email: str
    hashed_password: str
    role: str
    disabled: bool = False

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[User]:
    """Get user from database"""
    if username in users_db:
        return User(**users_db[username])
    return None

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
        
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

# RBAC Dependencies
class RoleChecker:
    """Dependency for role-based access control"""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        return user

# Role-specific dependencies
require_admin = RoleChecker([UserRole.ADMIN])
require_manager = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])
require_user = RoleChecker([UserRole.ADMIN, UserRole.MANAGER, UserRole.USER])

# Routes
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user"""
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Validate role
    if user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "role": user.role,
        "disabled": False
    }
    users_db[user.username] = user_dict
    
    return UserResponse(**user_dict)

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access + refresh tokens"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})
    
    # Store refresh token
    refresh_tokens_db[refresh_token] = {
        "username": user.username,
        "created_at": datetime.utcnow()
    }
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@app.post("/refresh", response_model=Token)
async def refresh_access_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(request.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise credentials_exception
        
        # Check if refresh token exists in database
        if request.refresh_token not in refresh_tokens_db:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "role": role},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": username, "role": role})
    
    # Invalidate old refresh token and store new one
    del refresh_tokens_db[request.refresh_token]
    refresh_tokens_db[new_refresh_token] = {
        "username": username,
        "created_at": datetime.utcnow()
    }
    
    return Token(access_token=access_token, refresh_token=new_refresh_token)

@app.post("/logout")
async def logout(request: RefreshTokenRequest, current_user: User = Depends(get_current_user)):
    """Logout and invalidate refresh token"""
    if request.refresh_token in refresh_tokens_db:
        del refresh_tokens_db[request.refresh_token]
    return {"message": "Successfully logged out"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user.dict())

@app.get("/admin/users", response_model=List[UserResponse])
async def admin_get_all_users(current_user: User = Depends(require_admin)):
    """Admin only: Get all users"""
    return [UserResponse(**user) for user in users_db.values()]

@app.delete("/admin/users/{username}")
async def admin_delete_user(username: str, current_user: User = Depends(require_admin)):
    """Admin only: Delete a user"""
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    del users_db[username]
    return {"message": f"User {username} deleted successfully"}

@app.get("/manager/dashboard")
async def manager_dashboard(current_user: User = Depends(require_manager)):
    """Manager and Admin access: Dashboard"""
    return {
        "message": "Welcome to the manager dashboard",
        "user": current_user.username,
        "role": current_user.role,
        "total_users": len(users_db)
    }

@app.get("/protected")
async def protected_route(current_user: User = Depends(require_user)):
    """Protected route for all authenticated users"""
    return {
        "message": "This is a protected route",
        "user": current_user.username,
        "role": current_user.role
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Auth Service API",
        "version": "1.0.0",
        "endpoints": {
            "register": "/register",
            "login": "/token",
            "refresh": "/refresh",
            "logout": "/logout",
            "profile": "/users/me",
            "admin": "/admin/*",
            "manager": "/manager/*",
            "protected": "/protected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
