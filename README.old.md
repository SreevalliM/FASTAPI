# 🚀 FastAPI Learning Project

A comprehensive, hands-on learning project covering FastAPI fundamentals through advanced database integration.

## What is FastAPI?

**FastAPI** is a modern, high-performance web framework for building APIs with Python 3.7+. It's designed to be:

- **Fast**: Built on **Starlette** (web layer) and **Pydantic** (data validation)
- **Easy**: Intuitive to use with automatic interactive documentation
- **Modern**: Uses Python type hints for validation and documentation
- **Async**: Full **ASGI** framework with async/await support
- **Standards-based**: Automatic **OpenAPI** (Swagger) documentation

### Key Technologies

- **Starlette**: High-performance ASGI framework for the web routing
- **Pydantic**: Data validation using Python type annotations
- **ASGI**: Asynchronous Server Gateway Interface (supports async operations)
- **SQLModel**: SQL databases integration (combines SQLAlchemy + Pydantic)
- **Alembic**: Database migration tool

---

## 📁 Project Structure

This project is organized into **4 self-contained modules**, each in its own folder:

```
FASTAPI/
├── 01_todo_crud/              # Module 1: Basic CRUD Operations
├── 02_request_validation/     # Module 2: Advanced Validation
├── 03_dependency_injection/   # Module 3: Dependency Injection
└── 04_database_integration/   # Module 4: Database Integration
```

**📖 See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed organization**

---

## 📚 Learning Modules

### Module 1: Todo CRUD API
**🎯 Learn:** Basic CRUD operations, HTTP methods, Pydantic models

📂 [01_todo_crud/](01_todo_crud/)
```bash
python 01_todo_crud/01_todo_crud_api.py
```

### Module 2: Request Validation
**🎯 Learn:** Advanced validation, Field validators, custom validation

📂 [02_request_validation/](02_request_validation/)
```bash
python 02_request_validation/02_request_validation.py
```

### Module 3: Dependency Injection
**🎯 Learn:** DI patterns, authentication, testing with overrides

📂 [03_dependency_injection/](03_dependency_injection/)
```bash
python 03_dependency_injection/03_dependency_injection.py
```

### Module 4: Database Integration
**🎯 Learn:** SQLModel/SQLAlchemy, migrations, SQLite/PostgreSQL

📂 [04_database_integration/](04_database_integration/)
```bash
python 04_database_integration/05_book_api_sqlite.py
```

---

## 🎓 Key Concepts Covered

### 1. Route Decorators & HTTP Methods
- `@app.get()` - Retrieve data
- `@app.post()` - Create data
- `@app.put()` - Update data
- `@app.delete()` - Delete data

### 2. Path & Query Parameters
```python
@app.get("/items/{item_id}")  # Path parameter
def get_item(item_id: int, skip: int = 0):  # Query parameter
    pass
```

### 3. Request/Response Models
```python
class Item(BaseModel):
    title: str
    description: Optional[str] = None
```

### 4. Validation & Field Constraints
- Required/optional fields
- Type validation
- Custom validators
- Regex patterns

### 5. Dependency Injection
- Reusable dependencies
- Authentication
- Database sessions
- Testing with overrides

### 6. Database Integration
- SQLModel ORM
- CRUD operations
- Alembic migrations
- Multiple database support

### 7. Automatic Documentation
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- (Optional) Docker for PostgreSQL

### Quick Start

1. **Clone and navigate to the project**
```bash
cd FASTAPI
```

2. **Create a virtual environment**
```bash
python -m venv fastapi-env
source fastapi-env/bin/activate  # On macOS/Linux
# or
fastapi-env\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start with Module 1**
```bash
cd 01_todo_crud
python 01_todo_crud_api.py
```

Visit: http://localhost:8000/docs

### Module-Specific Setup

**Module 4 (Database Integration):**
```bash
cd 04_database_integration
./setup_database_module.sh  # Installs additional dependencies
python 05_book_api_sqlite.py
```

---

## 🎯 Quick Examples

### Base URL
```
http://127.0.0.1:8000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/docs` | Interactive Swagger documentation |
| GET | `/health` | Health check |
| POST | `/tasks` | Create a new task |
| GET | `/tasks` | List all tasks (with optional filters) |
| GET | `/tasks/{task_id}` | Get a specific task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a specific task |
| DELETE | `/tasks` | Delete all tasks |

---

## 📝 Usage Examples

### 1. Create a Task (POST)
```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Complete the To-Do API tutorial",
    "completed": false
  }'
```

**Response:**
```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Complete the To-Do API tutorial",
  "completed": false,
  "created_at": "2026-02-14T10:30:00.123456"
}
```

### 2. List All Tasks (GET)
```bash
curl "http://127.0.0.1:8000/tasks"
```

**With query parameters:**
```bash
# Get only completed tasks
curl "http://127.0.0.1:8000/tasks?completed=true"

# Limit results
curl "http://127.0.0.1:8000/tasks?limit=5"

# Combine filters
curl "http://127.0.0.1:8000/tasks?completed=false&limit=10"
```

### 3. Get a Specific Task (GET)
```bash
curl "http://127.0.0.1:8000/tasks/1"
```

### 4. Update a Task (PUT)
```bash
curl -X PUT "http://127.0.0.1:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

### 5. Delete a Task (DELETE)
```bash
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
```

---

## 🧪 Testing with Swagger UI

1. Start the server:
   ```bash
   uvicorn 01_todo_crud_api:app --reload
   ```

2. Open your browser and go to:
   ```
   http://127.0.0.1:8000/docs
   ```

3. You'll see an interactive interface where you can:
   - Test all endpoints directly from the browser
   - View request/response schemas
   - See automatic validation errors
   - Try different parameter combinations

---

## 🎓 Learning Checklist

- ✅ **Route decorators**: `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`
- ✅ **Path parameters**: `/tasks/{task_id}`
- ✅ **Query parameters**: `?completed=true&limit=10`
- ✅ **Request body**: Using Pydantic models for validation
- ✅ **Response models**: Automatic serialization and documentation
- ✅ **Automatic documentation**: Swagger UI at `/docs`
- ✅ **Data validation**: Pydantic validates all input automatically
- ✅ **HTTP status codes**: 200, 201, 204, 404, etc.
- ✅ **Error handling**: HTTPException for proper error responses

---

## 🔥 Next Steps

After mastering this basic To-Do API, try:

1. **Add authentication** (JWT tokens)
2. **Connect to a database** (SQLite, PostgreSQL with SQLAlchemy)
3. **Add user management** (multiple users with their own tasks)
4. **Implement filtering & sorting** (by date, priority, etc.)
5. **Add task categories/tags**
6. **Deploy to production** (Heroku, Railway, AWS, etc.)
7. **Add frontend** (React, Vue, or HTML templates)
8. **Write unit tests** (using pytest and TestClient)

---

## 📖 Resources

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Starlette Documentation](https://www.starlette.io/)

---

## � Project Modules

### 📌 Module 1: To-Do CRUD API (`01_todo_crud_api.py`)
**Topics Covered:**
- Route decorators (GET, POST, PUT, DELETE)
- Path and query parameters
- Pydantic models for validation
- CRUD operations
- Automatic documentation

**Run it:**
```bash
python 01_todo_crud_api.py
# or
uvicorn 01_todo_crud_api:app --reload
```

### 📌 Module 2: Request Validation (`02_request_validation.py`)
**Topics Covered:**
- `Query()`, `Path()`, `Body()` parameters
- Advanced validation with Pydantic
- Field constraints (min_length, max_length, ge, le)
- Regex patterns
- Custom validators
- EmailStr validation

**Run it:**
```bash
python 02_request_validation.py
# or
uvicorn 02_request_validation:app --reload
```

### 📌 Module 3: Dependency Injection (`03_dependency_injection.py`) ⭐ NEW!
**Topics Covered:**
- `Depends()` - The core of dependency injection
- Reusable logic and shared resources
- Function-based dependencies
- Class-based dependencies
- Generator-based dependencies (with cleanup)
- Dependency chaining (dependencies depending on other dependencies)
- Security dependencies (authentication & authorization)
- Rate limiting
- Logging
- Database session management

**Practice Project:** User Management API
- ✅ Create user with validation
- ✅ Email format and domain validation
- ✅ Shared logging dependency
- ✅ Rate-limiting dependency (normal & strict)
- ✅ API key authentication
- ✅ Role-based authorization (admin vs user)
- ✅ Database session management

**Run it:**
```bash
python 03_dependency_injection.py
```

**Test API Keys:**
- Admin: `admin_key_123`
- User: `user_key_456`

**Tutorial:** See [03_DI_TUTORIAL.md](03_DI_TUTORIAL.md) for detailed explanations and examples.

---

## 📚 Key Concepts by Module

| Concept | Module 1 | Module 2 | Module 3 |
|---------|----------|----------|----------|
| Route Decorators | ✅ | ✅ | ✅ |
| Path Parameters | ✅ | ✅ | ✅ |
| Query Parameters | ✅ | ✅ | ✅ |
| Pydantic Models | ✅ | ✅ | ✅ |
| Request Validation | Basic | Advanced | Advanced |
| Custom Validators | ❌ | ✅ | ✅ |
| Dependency Injection | ❌ | ❌ | ✅ |
| Authentication | ❌ | ❌ | ✅ |
| Authorization | ❌ | ❌ | ✅ |
| Rate Limiting | ❌ | ❌ | ✅ |
| Logging | ❌ | ❌ | ✅ |
| DB Session Management | ❌ | ❌ | ✅ |

---

## �🎉 Happy Coding!

FastAPI makes building APIs fast and fun. Explore the interactive docs, modify the code, and experiment with different features!