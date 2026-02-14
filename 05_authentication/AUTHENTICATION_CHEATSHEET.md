# 🔐 OAuth2 + JWT Authentication Cheatsheet

## 📦 Installation

```bash
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-multipart
```

---

## ⚡ Quick Setup

### 1. **Basic Configuration**

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Configuration
SECRET_KEY = "your-secret-key"  # Use: openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
```

### 2. **Password Hashing**

```python
# Hash password
hashed_password = pwd_context.hash("mypassword")

# Verify password
is_valid = pwd_context.verify("mypassword", hashed_password)
```

### 3. **Create JWT Token**

```python
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 4. **Login Endpoint**

```python
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

### 5. **Get Current User Dependency**

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
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
```

### 6. **Protected Route**

```python
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

---

## 🛡️ Role-Based Access Control (RBAC)

### Define Roles

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
```

### Role Checker Dependency

```python
def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_checker
```

### Use in Routes

```python
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_role(UserRole.ADMIN))
):
    # Only admins can access this
    return {"message": "User deleted"}
```

---

## 🔑 Security Scopes

### Setup OAuth2 with Scopes

```python
from fastapi.security import SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "items:read": "Read items",
        "items:write": "Write items",
        "users:read": "Read users",
    }
)
```

### Validate Scopes

```python
async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
):
    # ... decode token ...
    
    token_scopes = payload.get("scopes", [])
    
    # Check required scopes
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return user
```

### Use in Routes

```python
from fastapi import Security

@app.get("/items/")
async def read_items(
    current_user: User = Security(get_current_user, scopes=["items:read"])
):
    return items

@app.post("/items/")
async def create_item(
    item: Item,
    current_user: User = Security(get_current_user, scopes=["items:write"])
):
    return item
```

### Create Token with Scopes

```python
access_token = create_access_token(
    data={
        "sub": user.username,
        "scopes": ["items:read", "items:write"]
    }
)
```

---

## 📋 Common Patterns

### 1. **Register User**

```python
@app.post("/register")
async def register(username: str, password: str):
    if user_exists(username):
        raise HTTPException(400, "User already exists")
    
    hashed_password = pwd_context.hash(password)
    create_user_in_db(username, hashed_password)
    
    return {"message": "User created"}
```

### 2. **Refresh Token**

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
        raise HTTPException(400, "Invalid token type")
    
    username = payload.get("sub")
    new_access_token = create_access_token({"sub": username})
    
    return {"access_token": new_access_token, "token_type": "bearer"}
```

### 3. **Logout (Token Blacklist)**

```python
blacklisted_tokens = set()

@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklisted_tokens.add(token)
    return {"message": "Logged out"}

# In get_current_user, check:
if token in blacklisted_tokens:
    raise HTTPException(401, "Token has been revoked")
```

### 4. **Multiple Role Check**

```python
def require_any_role(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(403, "Access denied")
        return current_user
    return role_checker

@app.get("/admin-or-mod")
async def admin_or_mod_only(
    user: User = Depends(require_any_role(UserRole.ADMIN, UserRole.MODERATOR))
):
    return {"message": "Welcome!"}
```

### 5. **Check User Disabled**

```python
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.disabled:
        raise HTTPException(400, "Inactive user")
    return current_user
```

---

## 🎯 Quick Reference Table

| Task | Code |
|------|------|
| **Hash password** | `pwd_context.hash(password)` |
| **Verify password** | `pwd_context.verify(plain, hashed)` |
| **Create JWT** | `jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)` |
| **Decode JWT** | `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])` |
| **OAuth2 scheme** | `OAuth2PasswordBearer(tokenUrl="token")` |
| **Login form** | `OAuth2PasswordRequestForm = Depends()` |
| **Protected route** | `current_user: User = Depends(get_current_user)` |
| **Role check** | `admin: User = Depends(require_admin)` |
| **Scope check** | `Security(get_current_user, scopes=["items:read"])` |

---

## 🚨 Common Errors & Solutions

### Error: "Not authenticated"

**Cause**: No token or invalid token  
**Solution**: Login first at `/token` endpoint

### Error: "Could not validate credentials"

**Cause**: Token expired or invalid  
**Solution**: Login again to get new token

### Error: "Not enough permissions"

**Cause**: Token doesn't have required scope  
**Solution**: User needs different role/permissions

### Error: "Operation requires admin role"

**Cause**: User is not admin  
**Solution**: Use admin account or change user role

---

## 🔒 Security Best Practices

```python
# ✅ DO:
SECRET_KEY = os.getenv("SECRET_KEY")  # From environment
ACCESS_TOKEN_EXPIRE_MINUTES = 30       # Short expiration
pwd_context = CryptContext(schemes=["bcrypt"])  # Strong hashing

# ❌ DON'T:
SECRET_KEY = "secret"  # Weak secret
ACCESS_TOKEN_EXPIRE_MINUTES = 999999  # Too long
password = user.password  # Store plain text
```

---

## 📊 Flow Diagram

```
┌─────────┐          ┌─────────┐
│ Client  │          │ Server  │
└────┬────┘          └────┬────┘
     │                    │
     │  POST /token       │
     ├───────────────────►│
     │  {username, pwd}   │
     │                    │
     │  ◄─────────────────┤
     │  {access_token}    │
     │                    │
     │  GET /users/me     │
     ├───────────────────►│
     │  Authorization:    │
     │  Bearer <token>    │
     │                    │
     │  ◄─────────────────┤
     │  {user data}       │
     │                    │
```

---

## 🧪 Testing with cURL

```bash
# 1. Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret"

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Use token
TOKEN="eyJ..."

curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎓 Study Tips

1. **Start Simple**: OAuth2 → Add JWT → Add Roles → Add Scopes
2. **Test Each Layer**: Use `/docs` to test authentication flow
3. **Understand Tokens**: Decode JWT at [jwt.io](https://jwt.io)
4. **Practice Errors**: Try accessing endpoints without/with wrong tokens
5. **Read Payloads**: Check what's in your JWT tokens

---

## 🔗 Related Patterns

- **Dependency Injection**: Authentication uses dependencies heavily
- **Middleware**: Can add global authentication middleware
- **Database Integration**: Store users in real database
- **Environment Variables**: Store secrets securely
