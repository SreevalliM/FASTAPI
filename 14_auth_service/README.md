# 🔐 Auth Service

A production-ready authentication service built with FastAPI featuring JWT tokens, refresh tokens, RBAC (Role-Based Access Control), and secure password hashing.

## ✨ Features

- **JWT Authentication**: Secure access tokens with expiration
- **Refresh Tokens**: Long-lived tokens for refreshing access tokens
- **RBAC**: Role-based access control with three roles (Admin, Manager, User)
- **Password Hashing**: Bcrypt-based secure password storage
- **Token Revocation**: Logout functionality to invalidate refresh tokens
- **Email Validation**: Pydantic email validation
- **Comprehensive Testing**: Full test suite with pytest

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at: http://localhost:8000

Interactive API docs: http://localhost:8000/docs

## 📚 API Endpoints

### Public Endpoints

#### Register User
```bash
POST /register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "role": "user"  # Optional: admin, manager, user (default)
}
```

#### Login
```bash
POST /token
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=securepassword123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Protected Endpoints

#### Get Current User
```bash
GET /users/me
Authorization: Bearer <access_token>
```

#### Refresh Token
```bash
POST /refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token_here"
}
```

#### Logout
```bash
POST /logout
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh_token": "your_refresh_token_here"
}
```

#### Protected Route
```bash
GET /protected
Authorization: Bearer <access_token>
```

### Manager Endpoints (Manager + Admin)

```bash
GET /manager/dashboard
Authorization: Bearer <access_token>
```

### Admin Only Endpoints

#### Get All Users
```bash
GET /admin/users
Authorization: Bearer <access_token>
```

#### Delete User
```bash
DELETE /admin/users/{username}
Authorization: Bearer <access_token>
```

## 👥 Roles & Permissions

| Role    | Access Level                                   |
|---------|------------------------------------------------|
| Admin   | Full access to all endpoints                   |
| Manager | Access to manager and user endpoints           |
| User    | Access to basic protected endpoints            |

## 🔑 Token System

### Access Token
- **Lifetime**: 30 minutes
- **Purpose**: Access protected resources
- **Storage**: Memory/Local storage (never in cookies without httpOnly)

### Refresh Token
- **Lifetime**: 7 days
- **Purpose**: Obtain new access tokens
- **Storage**: Secure, httpOnly cookie (recommended)
- **Rotation**: New refresh token issued on each refresh

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest test_auth.py -v

# Run with coverage
pytest test_auth.py --cov=main --cov-report=html
```

## 🔒 Security Best Practices

### Implemented
✅ Password hashing with bcrypt  
✅ JWT token expiration  
✅ Refresh token rotation  
✅ Token type validation (access vs refresh)  
✅ Role-based access control  
✅ Email validation  

### Production Recommendations
1. **Environment Variables**: Store secrets in environment variables
   ```python
   SECRET_KEY = os.getenv("SECRET_KEY")
   REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
   ```

2. **HTTPS Only**: Deploy behind HTTPS in production

3. **Database**: Replace in-memory storage with PostgreSQL/MongoDB
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   ```

4. **Rate Limiting**: Add rate limiting to prevent brute force
   ```python
   from slowapi import Limiter
   @limiter.limit("5/minute")
   async def login(...):
   ```

5. **CORS**: Configure CORS properly
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
   )
   ```

6. **Logging**: Add comprehensive logging
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

## 📊 Example Usage

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register
response = requests.post(f"{BASE_URL}/register", json={
    "username": "alice",
    "email": "alice@example.com",
    "password": "alicepass123",
    "role": "manager"
})
print(response.json())

# 2. Login
response = requests.post(f"{BASE_URL}/token", data={
    "username": "alice",
    "password": "alicepass123"
})
tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

# 3. Access protected route
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/users/me", headers=headers)
print(response.json())

# 4. Refresh access token
response = requests.post(f"{BASE_URL}/refresh", json={
    "refresh_token": refresh_token
})
new_tokens = response.json()

# 5. Logout
response = requests.post(
    f"{BASE_URL}/logout",
    headers={"Authorization": f"Bearer {access_token}"},
    json={"refresh_token": refresh_token}
)
print(response.json())
```

## 🎯 Next Steps

- [ ] Add PostgreSQL database integration
- [ ] Implement email verification
- [ ] Add password reset functionality
- [ ] Implement rate limiting
- [ ] Add OAuth2 providers (Google, GitHub)
- [ ] Add two-factor authentication (2FA)
- [ ] Implement session management
- [ ] Add audit logging

## 📖 References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 with Password Flow](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
