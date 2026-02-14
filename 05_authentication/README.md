# 🔐 Module 05: OAuth2 + JWT Authentication

Learn how to implement secure authentication with OAuth2, JWT tokens, and role-based access control in FastAPI.

---

## 📚 What You'll Learn

✅ **OAuth2PasswordBearer** - Token-based authentication  
✅ **JWT Token Creation** - Generate and validate tokens  
✅ **Password Hashing** - Secure password storage with bcrypt  
✅ **Token Expiration** - Time-limited access tokens  
✅ **Role-Based Access Control (RBAC)** - Admin vs User permissions  
✅ **Security Scopes** - Fine-grained permission control  
✅ **Protected Routes** - Authentication & authorization  

---

## 📦 Prerequisites

### Install Required Packages

```bash
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-multipart
```

**What each package does:**
- `python-jose`: JWT token encoding/decoding
- `passlib[bcrypt]`: Password hashing
- `python-multipart`: Form data parsing for OAuth2

---

## 🚀 Quick Start

### 1. Run the Example API

```bash
cd 05_authentication
uvicorn 05_user_auth_api:app --reload
```

### 2. Test in Browser

Open: http://localhost:8000/docs

### 3. Try Authentication

1. Click **"Authorize"** button (top right)
2. Enter credentials:
   - Username: `alice`
   - Password: `secret`
3. Click "Authorize"
4. Now try the protected endpoints!

### Test Users

| Username | Password | Role | Scopes |
|----------|----------|------|--------|
| alice | secret | Admin | All permissions |
| bob | secret | User | Read items only |
| charlie | secret | User | Read & write items |

---

## 📖 Learning Path

### Step 1: Understanding the Basics

Read: [`05_AUTHENTICATION_TUTORIAL.md`](05_AUTHENTICATION_TUTORIAL.md)

Topics covered:
- OAuth2 fundamentals
- JWT token structure
- Password hashing with bcrypt
- Security best practices

### Step 2: Study the Implementation

Examine: [`05_user_auth_api.py`](05_user_auth_api.py)

Key sections:
- Configuration & setup
- Password hashing functions
- Token creation
- Authentication dependencies
- Protected routes
- Role-based access control

### Step 3: Quick Reference

Keep handy: [`AUTHENTICATION_CHEATSHEET.md`](AUTHENTICATION_CHEATSHEET.md)

Quick lookup for:
- Common patterns
- Code snippets
- Error solutions
- Security tips

---

## 🎯 Practice Exercises

### Exercise 1: Test Basic Authentication

**Goal**: Understand the authentication flow

**Tasks**:
1. Run the API: `uvicorn 05_user_auth_api:app --reload`
2. Go to http://localhost:8000/docs
3. Try accessing `/users/me` without authentication
   - You should get a 401 error
4. Click "Authorize" and login as `alice` / `secret`
5. Try `/users/me` again
   - You should see your profile

**Expected Results**:
- Unauthorized access → 401 error
- After login → Access granted

---

### Exercise 2: Test Role-Based Access

**Goal**: See how roles control access

**Tasks**:
1. Login as **bob** (regular user)
2. Try to access `/users` (list all users)
   - Should fail with 403 Forbidden
3. Logout (click Authorize → Logout)
4. Login as **alice** (admin)
5. Try `/users` again
   - Should succeed

**Expected Results**:
- Bob: Cannot list users (not admin)
- Alice: Can list users (is admin)

---

### Exercise 3: Test Security Scopes

**Goal**: Understand fine-grained permissions

**Tasks**:
1. Login as **bob** (has `items:read` scope only)
2. Try `GET /users/me/items` → Should work
3. Try `POST /items` with title "Test Item" → Should fail (needs `items:write`)
4. Logout and login as **charlie** (has `items:read` and `items:write`)
5. Try `POST /items` again → Should work

**Expected Results**:
- Scopes control what each user can do
- Different from roles (more granular)

---

### Exercise 4: Register New User

**Goal**: Create a new user account

**Tasks**:
1. Use `POST /register` endpoint
2. Register a new user:
   ```json
   {
     "username": "david",
     "email": "david@example.com",
     "full_name": "David Developer",
     "password": "SecurePass123",
     "role": "user"
   }
   ```
3. Try to register with weak password
   - Should fail validation
4. Login with new credentials
5. Test what the new user can access

**Expected Results**:
- Strong password required
- New user created successfully
- Can login and access user endpoints

---

### Exercise 5: Token Expiration

**Goal**: Understand token expiration

**Tasks**:
1. In `05_user_auth_api.py`, change `ACCESS_TOKEN_EXPIRE_MINUTES` to `1`
2. Restart the server
3. Login as alice
4. Use a protected endpoint immediately → Works
5. Wait 2 minutes
6. Try the same endpoint → Should fail (token expired)

**Expected Results**:
- Fresh token works
- Expired token returns 401 error
- Need to login again for new token

---

### Exercise 6: Inspect JWT Tokens

**Goal**: Understand JWT structure

**Tasks**:
1. Login and copy the access token from the response
2. Go to https://jwt.io/
3. Paste your token in the "Encoded" box
4. Look at the decoded payload:
   - What's in `sub`?
   - What's in `scopes`?
   - When does it expire (`exp`)?
5. Try modifying the token and using it
   - Should fail verification

**Expected Results**:
- JWT contains user data
- Token cannot be tampered with
- Signature validation catches modifications

---

## 🏗️ Build Your Own

### Challenge 1: Add Email Verification

**Requirements**:
- Generate verification token on registration
- Send email with verification link (simulate with print)
- Add `/verify-email/{token}` endpoint
- User cannot login until email verified

**Hints**:
```python
# Add to User model
email_verified: bool = False

# Generate verification token
verification_token = secrets.token_urlsafe(32)

# In login, check:
if not user.email_verified:
    raise HTTPException(400, "Email not verified")
```

---

### Challenge 2: Implement Password Reset

**Requirements**:
- `POST /forgot-password` - Request reset
- Generate reset token with 1-hour expiration
- `POST /reset-password` - Reset with token

**Hints**:
```python
def create_reset_token(email: str):
    data = {
        "sub": email,
        "type": "reset",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
```

---

### Challenge 3: Add Refresh Tokens

**Requirements**:
- Login returns both access and refresh tokens
- Access token expires in 15 minutes
- Refresh token expires in 7 days
- `POST /refresh` - Get new access token with refresh token

**Hints**:
```python
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # ... authenticate ...
    
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

---

### Challenge 4: Implement User Scopes Management

**Requirements**:
- Admin can view user's scopes: `GET /users/{username}/scopes`
- Admin can add a scope: `POST /users/{username}/scopes`
- Admin can remove a scope: `DELETE /users/{username}/scopes/{scope}`
- Changes affect next login

**Hints**:
```python
@app.post("/users/{username}/scopes")
async def add_scope(
    username: str,
    scope: str,
    admin: User = Depends(require_admin)
):
    user = get_user(username)
    if scope not in user.scopes:
        user.scopes.append(scope)
    return user
```

---

### Challenge 5: Add "Remember Me" Feature

**Requirements**:
- Add `remember_me: bool` to login form
- If true, token expires in 30 days
- If false, token expires in 30 minutes

**Hints**:
```python
@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = False
):
    # ...authenticate...
    
    expires = timedelta(days=30 if remember_me else minutes=30)
    access_token = create_access_token(data, expires_delta=expires)
    
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## 🧪 Testing Guide

### Manual Testing with Swagger UI

1. **Test Authentication Flow**
   - Try protected endpoint → 401
   - Login → Get token
   - Try again → 200 OK

2. **Test Different Users**
   - Compare alice (admin) vs bob (user)
   - Note which endpoints each can access

3. **Test Invalid Credentials**
   - Wrong password
   - Non-existent user
   - Expired token

### Testing with cURL

```bash
# 1. Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret"

# 2. Copy token from response
TOKEN="<paste_token_here>"

# 3. Access protected endpoint
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer $TOKEN"

# 4. Test admin endpoint
curl -X GET "http://localhost:8000/users" \
  -H "Authorization: Bearer $TOKEN"
```

### Testing with Python Requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/token",
    data={"username": "alice", "password": "secret"}
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/users/me", headers=headers)
print(response.json())
```

---

## 🔒 Security Checklist

When implementing authentication, ensure:

- [ ] Strong secret key (use `openssl rand -hex 32`)
- [ ] Secret key stored in environment variables
- [ ] Passwords hashed with bcrypt
- [ ] Password validation (length, complexity)
- [ ] Token expiration implemented
- [ ] HTTPS in production
- [ ] Rate limiting on login endpoint
- [ ] Account lockout after failed attempts
- [ ] Secure password reset flow
- [ ] Token validation on every request

---

## 🐛 Common Issues & Solutions

### Issue 1: "Not authenticated"

**Cause**: Token not included or expired  
**Solution**: Login again to get new token

### Issue 2: "Could not validate credentials"

**Cause**: Invalid token format or signature  
**Solution**: Check token is correctly copied/generated

### Issue 3: "Not enough permissions"

**Cause**: User lacks required scope  
**Solution**: Modify user scopes or use different user

### Issue 4: "bcrypt not installed"

**Cause**: Missing bcrypt package  
**Solution**: `pip install passlib[bcrypt]`

---

## 📊 Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         CLIENT                                  │
│  (Browser / Mobile App / API Client)                           │
└───────────────────┬────────────────────────────────────────────┘
                    │
                    │ 1. POST /token
                    │    {username, password}
                    │
                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    LOGIN ENDPOINT                               │
│  • Validate credentials                                         │
│  • Generate JWT token                                           │
│  • Return token                                                 │
└───────────────────┬────────────────────────────────────────────┘
                    │
                    │ 2. {access_token: "eyJ..."}
                    │
                    ▼
┌────────────────────────────────────────────────────────────────┐
│                     CLIENT STORAGE                              │
│  Store token (memory / localStorage / secure storage)          │
└───────────────────┬────────────────────────────────────────────┘
                    │
                    │ 3. GET /protected-resource
                    │    Authorization: Bearer eyJ...
                    │
                    ▼
┌────────────────────────────────────────────────────────────────┐
│              AUTHENTICATION DEPENDENCY                          │
│  • Extract token from header                                    │
│  • Decode & validate JWT                                        │
│  • Check expiration                                             │
│  • Check scopes/roles                                           │
│  • Return user or raise 401/403                                 │
└───────────────────┬────────────────────────────────────────────┘
                    │
                    │ 4. User object or HTTPException
                    │
                    ▼
┌────────────────────────────────────────────────────────────────┐
│                  PROTECTED ENDPOINT                             │
│  • Process request with authenticated user                      │
│  • Return response                                              │
└────────────────────────────────────────────────────────────────┘
```

---

## 📚 Additional Resources

- [FastAPI Security Tutorial](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 Specification](https://oauth.net/2/)
- [JWT Introduction](https://jwt.io/introduction)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Bcrypt Explained](https://en.wikipedia.org/wiki/Bcrypt)

---

## 🎯 Learning Outcomes

After completing this module, you should be able to:

✅ Implement OAuth2 password flow in FastAPI  
✅ Create and validate JWT tokens  
✅ Hash and verify passwords securely  
✅ Implement role-based access control  
✅ Use security scopes for fine-grained permissions  
✅ Protect API endpoints with authentication  
✅ Handle token expiration  
✅ Follow security best practices  

---

## ⏭️ Next Steps

After mastering authentication, explore:

1. **Database Integration** - Store users in PostgreSQL/MongoDB
2. **Frontend Integration** - Connect with React/Vue.js
3. **API Rate Limiting** - Prevent abuse
4. **OAuth2 Social Login** - Google, GitHub, etc.
5. **Two-Factor Authentication (2FA)** - Extra security layer
6. **WebSocket Authentication** - Secure real-time connections

---

## 💡 Pro Tips

1. **Always use HTTPS** in production
2. **Never log tokens** - They're like passwords
3. **Rotate secret keys** periodically
4. **Use environment variables** for configuration
5. **Implement token refresh** for better UX
6. **Add rate limiting** on login endpoints
7. **Monitor failed login attempts**
8. **Use short token expiration** times

---

## 🤔 Discussion Questions

1. Why is JWT better than session-based authentication for APIs?
2. What's the difference between authentication and authorization?
3. When would you use scopes vs roles?
4. Why is bcrypt preferred over SHA-256 for passwords?
5. What are the security implications of long token expiration times?

---

**Happy Learning! 🚀**

Need help? Check the tutorial files or refer to the cheatsheet!
