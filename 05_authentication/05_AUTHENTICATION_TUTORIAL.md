# 🔐 OAuth2 + JWT Authentication Tutorial

## 📚 Table of Contents
1. [OAuth2 Basics](#oauth2-basics)
2. [JWT Tokens](#jwt-tokens)
3. [Password Hashing](#password-hashing)
4. [Token Creation & Validation](#token-creation--validation)
5. [Role-Based Access Control](#role-based-access-control)
6. [Security Scopes](#security-scopes)
7. [Best Practices](#best-practices)

---

## 🎯 OAuth2 Basics

### What is OAuth2?

OAuth2 is an authorization framework that enables applications to obtain limited access to user accounts. In FastAPI, we use **OAuth2PasswordBearer** for password-based authentication.

### OAuth2PasswordBearer

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

**Key Points:**
- `tokenUrl="token"` tells the client where to get the token
- Returns the token as a string that you can pass to dependencies
- Automatically adds a "Bearer" token authorization header
- Creates automatic API documentation with a "Authorize" button

### How It Works

```
1. Client sends credentials → /token endpoint
2. Server validates credentials
3. Server creates JWT token
4. Server returns token to client
5. Client includes token in subsequent requests
6. Server validates token for each protected route
```

---

## 🎫 JWT Tokens

### What is JWT?

**JWT (JSON Web Token)** is a compact, URL-safe token format that contains claims about a user.

### JWT Structure

A JWT has three parts separated by dots:

```
xxxxx.yyyyy.zzzzz
```

1. **Header**: Algorithm & token type
2. **Payload**: Claims (user data)
3. **Signature**: Verification signature

### Example JWT Payload

```python
{
    "sub": "user@example.com",  # Subject (user identifier)
    "exp": 1640000000,           # Expiration time
    "role": "admin",             # Custom claim
    "scopes": ["read", "write"]  # Permissions
}
```

### Creating JWT Tokens

```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
```

### Decoding & Validating JWT

```python
from jose import JWTError, jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
        return payload
        
    except JWTError:
        raise credentials_exception
```

---

## 🔒 Password Hashing

**NEVER** store plain text passwords!

### Using `passlib` with `bcrypt`

```python
from passlib.context import CryptContext

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash a password
hashed_password = pwd_context.hash("mypassword123")

# Verify a password
is_valid = pwd_context.verify("mypassword123", hashed_password)
```

### Why Bcrypt?

- **Slow by design**: Makes brute-force attacks impractical
- **Salted**: Each password has unique hash
- **Adaptive**: Can increase cost factor over time

---

## 🎪 Token Creation & Validation

### Complete Authentication Flow

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Login endpoint
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    # Get user from database and return
    return current_user
```

---

## 👥 Role-Based Access Control (RBAC)

### Defining Roles

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
```

### Role-Based Dependencies

```python
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract and return current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = get_user_from_db(username)
    
    if user is None:
        raise credentials_exception
        
    return user

def require_role(required_role: UserRole):
    """Dependency factory for role-based access"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role} role"
            )
        return current_user
    return role_checker

# Usage in routes
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_role(UserRole.ADMIN))
):
    """Only admins can delete users"""
    delete_user_from_db(user_id)
    return {"message": "User deleted"}

@app.get("/users/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Any authenticated user can access their own profile"""
    return current_user
```

---

## 🛡️ Security Scopes

### What are Security Scopes?

Security scopes provide **fine-grained permissions** beyond simple roles. A user can have multiple scopes.

### Example Scopes

```python
# User has multiple permissions
scopes = ["items:read", "items:write", "users:read"]
```

### Using SecurityScopes in FastAPI

```python
from fastapi.security import SecurityScopes

def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> User:
    """Validate token and check required scopes"""
    
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
        token_scopes = payload.get("scopes", [])
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = get_user_from_db(username)
    
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

# Usage with specific scopes
@app.get("/items/", dependencies=[Security(get_current_user, scopes=["items:read"])])
async def read_items():
    return [{"item_id": 1, "name": "Foo"}]

@app.post("/items/", dependencies=[Security(get_current_user, scopes=["items:write"])])
async def create_item(item: Item):
    return item
```

### Creating Tokens with Scopes

```python
def create_access_token(username: str, scopes: list[str]):
    data = {
        "sub": username,
        "scopes": scopes,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
```

---

## ✅ Best Practices

### 1. **Use Strong Secret Keys**

```python
# Generate a secure secret key
import secrets
secret_key = secrets.token_urlsafe(32)

# Or use command line:
# openssl rand -hex 32
```

### 2. **Environment Variables**

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
```

### 3. **Token Expiration**

- **Access tokens**: Short-lived (15-30 minutes)
- **Refresh tokens**: Long-lived (days/weeks)

### 4. **HTTPS Only**

Always use HTTPS in production to prevent token interception.

### 5. **Password Requirements**

```python
import re

def validate_password(password: str) -> bool:
    """
    Validate password strength:
    - At least 8 characters
    - Contains uppercase
    - Contains lowercase
    - Contains digit
    - Contains special character
    """
    if len(password) < 8:
        return False
    
    if not re.search(r"[A-Z]", password):
        return False
    
    if not re.search(r"[a-z]", password):
        return False
    
    if not re.search(r"\d", password):
        return False
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    
    return True
```

### 6. **Rate Limiting**

Protect login endpoints from brute force:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/token")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # Login logic
    pass
```

### 7. **Logout (Token Blacklist)**

Since JWT is stateless, implement token blacklisting:

```python
# Store invalidated tokens in Redis or database
blacklisted_tokens = set()

def is_token_blacklisted(token: str) -> bool:
    return token in blacklisted_tokens

@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklisted_tokens.add(token)
    return {"message": "Successfully logged out"}
```

### 8. **Refresh Tokens**

```python
def create_refresh_token(username: str):
    data = {
        "sub": username,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/refresh")
async def refresh_token(refresh_token: str):
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")
    
    username = payload.get("sub")
    new_access_token = create_access_token(username)
    
    return {"access_token": new_access_token, "token_type": "bearer"}
```

---

## 🎯 Quick Reference

| Concept | Purpose | Example |
|---------|---------|---------|
| `OAuth2PasswordBearer` | Extract token from request | `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")` |
| `OAuth2PasswordRequestForm` | Get username/password from form | `form_data: OAuth2PasswordRequestForm = Depends()` |
| `jwt.encode()` | Create JWT token | `jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)` |
| `jwt.decode()` | Decode JWT token | `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])` |
| `pwd_context.hash()` | Hash password | `hashed = pwd_context.hash(plain_password)` |
| `pwd_context.verify()` | Verify password | `pwd_context.verify(plain, hashed)` |
| `Security()` | Apply scopes | `Security(get_current_user, scopes=["items:read"])` |

---

## 📦 Required Packages

```bash
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-multipart
```

---

## 🚀 Next Steps

1. ✅ Implement user registration
2. ✅ Create login endpoint
3. ✅ Add protected routes
4. ✅ Implement role-based access
5. ✅ Add security scopes
6. 📝 Add refresh token functionality
7. 🔧 Implement rate limiting
8. 🛡️ Add token blacklisting

---

## 📚 Additional Resources

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT.io](https://jwt.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
