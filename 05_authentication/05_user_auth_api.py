"""
🔐 FastAPI OAuth2 + JWT Authentication
==========================================
Complete authentication system with role-based access control.

Features:
- User registration with password hashing
- Login with JWT token generation
- Protected routes
- Role-based access (Admin, User)
- Security scopes for fine-grained permissions

Run: uvicorn 05_user_auth_api:app --reload
"""

from datetime import datetime, timedelta
from typing import Optional, List, Annotated
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, validator

# ==================== Configuration ====================

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In production, use: openssl rand -hex 32
# And store in environment variables

# ==================== Password Context ====================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "users:read": "Read user information",
        "users:write": "Create and update users",
        "users:delete": "Delete users",
        "items:read": "Read items",
        "items:write": "Create and update items",
    }
)

# ==================== Enums ====================

class UserRole(str, Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    USER = "user"

# ==================== Models ====================

class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Data extracted from token"""
    username: Optional[str] = None
    scopes: List[str] = []

class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    """User creation model with password"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class User(UserBase):
    """User model for responses"""
    id: int
    disabled: bool = False
    
    class Config:
        from_attributes = True

class UserInDB(User):
    """User model with hashed password (for database)"""
    hashed_password: str
    scopes: List[str] = []

# ==================== Fake Database ====================

fake_users_db = {
    "alice": {
        "id": 1,
        "username": "alice",
        "email": "alice@example.com",
        "full_name": "Alice Wonderland",
        "role": UserRole.ADMIN,
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "scopes": ["users:read", "users:write", "users:delete", "items:read", "items:write"],
    },
    "bob": {
        "id": 2,
        "username": "bob",
        "email": "bob@example.com",
        "full_name": "Bob Builder",
        "role": UserRole.USER,
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "scopes": ["items:read"],
    },
    "charlie": {
        "id": 3,
        "username": "charlie",
        "email": "charlie@example.com",
        "full_name": "Charlie Chocolate",
        "role": UserRole.USER,
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "scopes": ["items:read", "items:write"],
    },
}

# ==================== Helper Functions ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# ==================== Dependencies ====================

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UserInDB:
    """
    Validate token and return current user.
    Also validates security scopes if specified.
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
        
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    
    if user is None:
        raise credentials_exception
    
    # Check if user has required scopes
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user

async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=[])]
) -> User:
    """Check if user is active (not disabled)"""
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# ==================== FastAPI App ====================

app = FastAPI(
    title="🔐 FastAPI OAuth2 + JWT Authentication",
    description="Complete authentication system with role-based access control",
    version="1.0.0",
)

# ==================== Routes ====================

@app.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    🔑 **Login endpoint** - Get JWT token
    
    Use the "Try it out" button and enter:
    - Username: alice (admin) or bob/charlie (users)
    - Password: secret
    
    The token will be used automatically in other endpoints.
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Include user's scopes in the token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "scopes": user.scopes,
            "role": user.role,
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user_create: UserCreate):
    """
    📝 **Register new user**
    
    Password requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    # Check if user already exists
    if user_create.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Generate new user ID
    new_id = max([u["id"] for u in fake_users_db.values()], default=0) + 1
    
    # Create user with hashed password
    hashed_password = get_password_hash(user_create.password)
    
    # Default scopes for regular users
    default_scopes = ["items:read"]
    if user_create.role == UserRole.ADMIN:
        default_scopes = ["users:read", "users:write", "users:delete", "items:read", "items:write"]
    
    new_user = {
        "id": new_id,
        "username": user_create.username,
        "email": user_create.email,
        "full_name": user_create.full_name,
        "role": user_create.role,
        "hashed_password": hashed_password,
        "disabled": False,
        "scopes": default_scopes,
    }
    
    fake_users_db[user_create.username] = new_user
    
    return User(**new_user)

@app.get("/users/me", response_model=User, tags=["Users"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    👤 **Get current user profile**
    
    Any authenticated user can access their own profile.
    Requires: Valid JWT token
    """
    return current_user

@app.get("/users/me/items", tags=["Users"])
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["items:read"])]
):
    """
    📦 **Get current user's items**
    
    Requires: `items:read` scope
    """
    return [
        {"item_id": 1, "title": "Item 1", "owner": current_user.username},
        {"item_id": 2, "title": "Item 2", "owner": current_user.username},
    ]

@app.get("/users", response_model=List[User], tags=["Users"])
async def list_all_users(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["users:read"])]
):
    """
    📋 **List all users**
    
    Requires: `users:read` scope (Admin only)
    """
    users = []
    for user_data in fake_users_db.values():
        users.append(User(**user_data))
    return users

@app.get("/users/{username}", response_model=User, tags=["Users"])
async def get_user_by_username(
    username: str,
    current_user: Annotated[User, Depends(require_admin)]
):
    """
    🔍 **Get specific user by username**
    
    Requires: Admin role
    """
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.put("/users/{username}/role", response_model=User, tags=["Users - Admin"])
async def update_user_role(
    username: str,
    new_role: UserRole,
    admin: Annotated[User, Depends(require_admin)]
):
    """
    🛡️ **Update user role**
    
    Requires: Admin role
    
    Only admins can change user roles.
    """
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update role in "database"
    fake_users_db[username]["role"] = new_role
    
    # Update scopes based on new role
    if new_role == UserRole.ADMIN:
        fake_users_db[username]["scopes"] = ["users:read", "users:write", "users:delete", "items:read", "items:write"]
    else:
        fake_users_db[username]["scopes"] = ["items:read"]
    
    updated_user = get_user(username)
    return updated_user

@app.delete("/users/{username}", tags=["Users - Admin"])
async def delete_user(
    username: str,
    admin: Annotated[User, Security(get_current_active_user, scopes=["users:delete"])]
):
    """
    🗑️ **Delete user**
    
    Requires: `users:delete` scope (Admin only)
    
    Admins cannot delete themselves.
    """
    if username == admin.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    del fake_users_db[username]
    
    return {"message": f"User {username} deleted successfully"}

@app.post("/items", tags=["Items"])
async def create_item(
    title: str,
    current_user: Annotated[User, Security(get_current_active_user, scopes=["items:write"])]
):
    """
    ✍️ **Create new item**
    
    Requires: `items:write` scope
    """
    return {
        "item_id": 999,
        "title": title,
        "owner": current_user.username,
        "created_at": datetime.utcnow()
    }

@app.get("/status", tags=["Public"])
async def get_status():
    """
    ✅ **Public endpoint** - Check API status
    
    No authentication required.
    """
    return {
        "status": "online",
        "timestamp": datetime.utcnow(),
        "total_users": len(fake_users_db)
    }

# ==================== Info ====================

@app.get("/", tags=["Public"])
async def root():
    """
    🏠 **Welcome & Instructions**
    """
    return {
        "message": "Welcome to FastAPI OAuth2 + JWT Authentication API",
        "docs": "/docs",
        "test_users": {
            "admin": {
                "username": "alice",
                "password": "secret",
                "role": "admin",
                "scopes": ["users:read", "users:write", "users:delete", "items:read", "items:write"]
            },
            "user1": {
                "username": "bob",
                "password": "secret",
                "role": "user",
                "scopes": ["items:read"]
            },
            "user2": {
                "username": "charlie",
                "password": "secret",
                "role": "user",
                "scopes": ["items:read", "items:write"]
            }
        },
        "instructions": [
            "1. Go to /docs",
            "2. Click 'Authorize' button",
            "3. Login with username: alice, password: secret",
            "4. Try different endpoints with different users",
            "5. Notice how permissions vary by role and scopes"
        ]
    }

# ==================== Run ====================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI OAuth2 + JWT Authentication API")
    print("📚 Test users:")
    print("   - Admin: alice / secret")
    print("   - User: bob / secret")
    print("   - User: charlie / secret")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
