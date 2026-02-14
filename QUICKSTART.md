# 🚀 Quick Start - Dependency Injection Module

## ⚡ 5-Minute Quick Start

### 1. Install Dependencies (if not already done)

```bash
cd "/Users/L107127/Library/CloudStorage/OneDrive-EliLillyandCompany/Desktop/FASTAPI"
pip install -r requirements.txt
```

### 2. Run the API

```bash
python 03_dependency_injection.py
```

You should see:
```
🚀 Starting User Management API with Dependency Injection
📚 KEY CONCEPTS:
   1. Depends() - Injects reusable logic
   2. Logging - Shared logging dependency
   ...
📖 Documentation: http://localhost:8000/docs
```

### 3. Open Documentation

Go to: **http://localhost:8000/docs**

Interactive Swagger UI will open where you can test all endpoints!

---

## 🎯 Test the API (3 Ways)

### Option 1: Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Click on any endpoint (e.g., "POST /users")
3. Click "Try it out"
4. Fill in the example data
5. Click "Execute"
6. See the response!

**For protected endpoints:**
- Click the 🔒 "Authorize" button at the top
- Enter API key: `admin_key_123` or `user_key_456`
- Click "Authorize"
- Now try protected endpoints!

### Option 2: Test Script (Automated)

Open a **new terminal** (keep the server running in the first one):

```bash
cd "/Users/L107127/Library/CloudStorage/OneDrive-EliLillyandCompany/Desktop/FASTAPI"
python test_dependency_injection.py
```

This will run 14 automated tests and show you all features!

### Option 3: cURL Commands (Manual)

#### Create a user:
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@gmail.com",
    "age": 25,
    "password": "password123"
  }'
```

#### List users (requires auth):
```bash
curl -X GET "http://localhost:8000/users" \
  -H "api_key: user_key_456"
```

#### Update user (admin only):
```bash
curl -X PUT "http://localhost:8000/users/1" \
  -H "api_key: admin_key_123" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated"}'
```

---

## 🎓 Learning Path (30 minutes)

### Step 1: Understand the Basics (5 min)
Read: **[DEPENDENCY_CHEATSHEET.md](DEPENDENCY_CHEATSHEET.md)**
- Quick overview of all patterns
- Understanding syntax

### Step 2: Run and Test (10 min)
1. Start the API: `python 03_dependency_injection.py`
2. Run tests: `python test_dependency_injection.py`
3. Watch the server logs to see dependencies in action!

### Step 3: Deep Dive (15 min)
Read: **[03_DI_TUTORIAL.md](03_DI_TUTORIAL.md)**
- Detailed explanations
- Real-world examples
- Best practices

### Step 4: Experiment (10 min)
Open `03_dependency_injection.py` and:
- Change rate limits
- Add your own dependency
- Modify logging
- Create a new endpoint

---

## 📝 Key Files Created

| File | Purpose |
|------|---------|
| `03_dependency_injection.py` | Main API with all features |
| `03_DI_TUTORIAL.md` | Complete tutorial (30 min read) |
| `DEPENDENCY_CHEATSHEET.md` | Quick reference (5 min read) |
| `test_dependency_injection.py` | Automated test suite |
| `README.md` | Updated with Module 3 info |

---

## 🔑 Important Info

### API Keys for Testing:

- **Admin Key:** `admin_key_123`
  - Can list, create, update, delete users
  - Has strict rate limit (5 req/min)
  
- **User Key:** `user_key_456`
  - Can list and view users
  - Has normal rate limit (10 req/min)

### Allowed Email Domains:

- gmail.com
- outlook.com
- company.com
- example.com

### Rate Limits:

- **Normal endpoints:** 10 requests per minute
- **Admin endpoints:** 5 requests per minute

---

## 🎯 What You'll Learn

### ✅ Six Types of Dependencies Demonstrated:

1. **Logging Dependency** (`log_request`)
   - Logs every request automatically
   - Class-based dependency

2. **Database Session** (`get_db`)
   - Generator-based with cleanup
   - Simulates real DB connection

3. **Rate Limiting** (`rate_limiter_normal`, `rate_limiter_strict`)
   - IP-based rate limiting
   - Configurable limits

4. **Authentication** (`verify_api_key`)
   - Function-based security
   - API key validation

5. **Authorization** (`verify_admin`)
   - Role-based access control
   - Dependency chaining example

6. **Email Validation** (`validate_email_domain`)
   - Function-based validation
   - Reusable business logic

---

## 🔍 Watch Dependencies in Action

### Start the server and watch the logs:

```bash
python 03_dependency_injection.py
```

### In another terminal, create a user:

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@gmail.com",
    "age": 25,
    "password": "password123"
  }'
```

### Server logs will show:

```
INFO - 📥 Request: POST /users
INFO - 🌐 Client IP: 127.0.0.1
INFO - ✅ Rate limit check passed: 1/10 requests
INFO - 🔌 Database session created
INFO - ✅ Email domain validated: gmail.com
INFO - ✅ User created: test@gmail.com (ID: 1)
INFO - 🔌 Database session closed
```

**See how dependencies execute in order!**

---

## ⚡ Common Issues

### Issue 1: Port already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
uvicorn 03_dependency_injection:app --port 8001
```

### Issue 2: Module not found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure virtual environment is activated
source fastapi-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Issue 3: Cannot connect to server

**Error:** Connection refused

**Solution:**
- Make sure server is running: `python 03_dependency_injection.py`
- Check the URL: Should be `http://localhost:8000`
- Check firewall settings

---

## 🎉 Next Steps

After mastering this module, you can:

1. **Add more features:**
   - Password hashing (bcrypt)
   - JWT authentication
   - Refresh tokens
   - Email verification

2. **Connect to real database:**
   - SQLite with SQLAlchemy
   - PostgreSQL
   - MongoDB

3. **Add more dependencies:**
   - Caching (Redis)
   - File upload handling
   - Background tasks
   - WebSocket support

4. **Deploy to production:**
   - Docker
   - Heroku
   - AWS Lambda
   - Railway

---

## 📚 Resources

- **Official Docs:** https://fastapi.tiangolo.com/tutorial/dependencies/
- **Full Tutorial:** [03_DI_TUTORIAL.md](03_DI_TUTORIAL.md)
- **Quick Reference:** [DEPENDENCY_CHEATSHEET.md](DEPENDENCY_CHEATSHEET.md)
- **Main README:** [README.md](README.md)

---

## 💬 Quick Tips

1. **Always check server logs** - Dependencies log their execution
2. **Use Swagger UI** - Easiest way to test
3. **Read error messages** - FastAPI gives clear error details
4. **Experiment** - Modify the code and see what happens!
5. **Ask questions** - Use the interactive docs to explore

---

**🚀 You're ready to go! Start the server and begin learning.**

```bash
python 03_dependency_injection.py
```

**Happy Learning! 🎓**
