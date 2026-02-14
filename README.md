# 🚀 FastAPI Learning Project

A comprehensive, hands-on learning project covering FastAPI fundamentals through advanced database integration.

## What is FastAPI?

**FastAPI** is a modern, high-performance web framework for building APIs with Python 3.7+. It's designed to be:

- **Fast** ⚡ - High performance, on par with NodeJS and Go
- **Easy** 🎯 - Intuitive to use with automatic interactive documentation
- **Modern** 🔥 - Uses Python type hints for validation and documentation
- **Async** 🔄 - Full ASGI framework with async/await support
- **Production-ready** 🏭 - Used by Microsoft, Uber, Netflix, and more

### Key Technologies

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework |
| **Starlette** | ASGI framework (web routing) |
| **Pydantic** | Data validation using type hints |
| **SQLModel** | SQL database ORM |
| **Alembic** | Database migrations |
| **Uvicorn** | ASGI server |

---

## 📁 Project Structure

This project is organized into **4 self-contained learning modules**:

```
FASTAPI/
├── 01_todo_crud/              # Module 1: Basic CRUD Operations
│   ├── README.md
│   └── 01_todo_crud_api.py
│
├── 02_request_validation/     # Module 2: Advanced Validation
│   ├── README.md
│   └── 02_request_validation.py
│
├── 03_dependency_injection/   # Module 3: Dependency Injection
│   ├── README.md
│   ├── 03_dependency_injection.py
│   ├── 03_DI_TUTORIAL.md
│   ├── DEPENDENCY_CHEATSHEET.md
│   └── test_dependency_injection.py
│
└── 04_database_integration/   # Module 4: Database Integration
    ├── README.md
    ├── 04_book_api_memory.py
    ├── 05_book_api_sqlite.py
    ├── 06_book_api_postgres.py
    ├── book_models.py
    ├── 04_DATABASE_INTEGRATION_TUTORIAL.md
    ├── DATABASE_QUICK_REFERENCE.md
    ├── database_exercises.py
    ├── alembic.ini
    ├── setup_database_module.sh
    └── alembic/
```

📖 **See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed documentation**

---

## 🎓 Learning Modules

### Module 1: Todo CRUD API
**🎯 Learn:** Basic CRUD operations, HTTP methods, Pydantic models

📂 **Location:** [01_todo_crud/](01_todo_crud/)

**Topics:**
- Route decorators (GET, POST, PUT, DELETE)
- Path and query parameters
- Request/response models
- Status codes
- Automatic documentation

**Run:**
```bash
python 01_todo_crud/01_todo_crud_api.py
```
Visit: http://localhost:8000/docs

---

### Module 2: Request Validation
**🎯 Learn:** Advanced validation, Field validators, custom validation

📂 **Location:** [02_request_validation/](02_request_validation/)

**Topics:**
- Field constraints (min_length, regex patterns)
- Email and complex type validation
- Custom validators
- Computed fields
- Error handling

**Run:**
```bash
python 02_request_validation/02_request_validation.py
```
Visit: http://localhost:8000/docs

---

### Module 3: Dependency Injection
**🎯 Learn:** DI patterns, authentication, testing with overrides

📂 **Location:** [03_dependency_injection/](03_dependency_injection/)

**Topics:**
- `Depends()` for reusable logic
- Function and class-based dependencies
- Authentication and authorization
- Rate limiting
- Testing with dependency overrides

**Documentation:**
- [Module README](03_dependency_injection/README.md)
- [Complete Tutorial](03_dependency_injection/03_DI_TUTORIAL.md)
- [Quick Reference](03_dependency_injection/DEPENDENCY_CHEATSHEET.md)

**Run:**
```bash
python 03_dependency_injection/03_dependency_injection.py
```
Visit: http://localhost:8000/docs

---

### Module 4: Database Integration
**🎯 Learn:** SQLModel/SQLAlchemy, migrations, multiple databases

📂 **Location:** [04_database_integration/](04_database_integration/)

**Topics:**
- Database session management
- CRUD operations with SQLModel
- Alembic migrations
- Model vs Schema separation
- SQLite → PostgreSQL migration

**Documentation:**
- [Module README](04_database_integration/README.md)
- [Complete Tutorial](04_database_integration/04_DATABASE_INTEGRATION_TUTORIAL.md)
- [Quick Reference](04_database_integration/DATABASE_QUICK_REFERENCE.md)
- [Practice Exercises](04_database_integration/database_exercises.py)

**Setup & Run:**
```bash
cd 04_database_integration
./setup_database_module.sh
python 05_book_api_sqlite.py  # Port 8001
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- (Optional) Docker for PostgreSQL

### 2. Setup Environment

```bash
# Clone/navigate to project
cd FASTAPI

# Create virtual environment
python -m venv fastapi-env

# Activate it
source fastapi-env/bin/activate  # macOS/Linux
# or
fastapi-env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Learning

```bash
# Begin with Module 1
cd 01_todo_crud
python 01_todo_crud_api.py
```

Open your browser: **http://localhost:8000/docs**

---

## 📚 What You'll Learn

### ✅ Core FastAPI Concepts
- HTTP methods and RESTful APIs
- Route decorators and path operations
- Path and query parameters
- Request/response models
- Automatic interactive documentation
- Error handling and status codes

### ✅ Data Validation
- Pydantic models and Field validators
- Type hints and validation
- Custom validation logic
- Complex data types (email, URLs, dates)
- Validation constraints and patterns

### ✅ Dependency Injection
- `Depends()` pattern
- Reusable dependencies
- Authentication and authorization
- Rate limiting and caching
- Testing with dependency overrides

### ✅ Database Integration
- SQLModel ORM
- Database sessions as dependencies
- CRUD operations
- Alembic migrations
- Multiple database support (SQLite/PostgreSQL)
- Model vs Schema separation

---

## 🧪 Interactive Documentation

Every API includes automatic interactive documentation:

1. **Start any module's API**
2. **Open browser** to `/docs` (Swagger UI)
3. **Test endpoints** directly in browser
4. **View schemas** and validation rules
5. **See responses** in real-time

**Example URLs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📝 Quick Examples

### Module 1 - Create a Todo
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Complete all modules",
    "completed": false
  }'
```

### Module 2 - Create User with Validation
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "StrongPass123!",
    "age": 25
  }'
```

### Module 3 - Protected Endpoint
```bash
curl -H "X-API-Key: admin_key_123" \
  http://localhost:8000/admin
```

### Module 4 - Create Book in Database
```bash
curl -X POST "http://localhost:8001/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "year": 1949,
    "isbn": "1234567890123"
  }'
```

---

## 🎯 Learning Path

**Recommended Order:**

1. **[Module 1: Todo CRUD](01_todo_crud/)** → Learn the basics
2. **[Module 2: Request Validation](02_request_validation/)** → Master validation
3. **[Module 3: Dependency Injection](03_dependency_injection/)** → Understand DI
4. **[Module 4: Database Integration](04_database_integration/)** → Build complete apps

**Each module builds on the previous one!**

---

## 📖 Documentation

### Project Documentation
| File | Description |
|------|-------------|
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Detailed project organization |
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide |
| [requirements.txt](requirements.txt) | Python dependencies |

### Module Documentation
Each module has its own README and additional resources:

| Module | Main README | Additional Docs |
|--------|-------------|----------------|
| **1** | [README.md](01_todo_crud/README.md) | - |
| **2** | [README.md](02_request_validation/README.md) | - |
| **3** | [README.md](03_dependency_injection/README.md) | [Tutorial](03_dependency_injection/03_DI_TUTORIAL.md), [Cheatsheet](03_dependency_injection/DEPENDENCY_CHEATSHEET.md) |
| **4** | [README.md](04_database_integration/README.md) | [Tutorial](04_database_integration/04_DATABASE_INTEGRATION_TUTORIAL.md), [Reference](04_database_integration/DATABASE_QUICK_REFERENCE.md), [Exercises](04_database_integration/database_exercises.py) |

---

## 🗂️ Module Overview

| Module | Files | Port(s) | Focus | Complexity |
|--------|-------|---------|-------|------------|
| **1** | 1 file | 8000 | Basic CRUD | ⭐ Beginner |
| **2** | 1 file | 8000 | Validation | ⭐⭐ Beginner |
| **3** | 4 files | 8000 | DI Patterns | ⭐⭐⭐ Intermediate |
| **4** | 10+ files | 8000-8002 | Databases | ⭐⭐⭐⭐ Advanced |

---

## 🔥 After Completing All Modules

### Next Steps
1. ✅ Build your own API from scratch
2. ✅ Add JWT authentication
3. ✅ Implement async operations
4. ✅ Add WebSocket support
5. ✅ Write comprehensive tests (pytest)
6. ✅ Deploy to production (Heroku, AWS, Railway)
7. ✅ Create a frontend (React, Vue, or templates)
8. ✅ Add caching (Redis)
9. ✅ Implement background tasks (Celery)
10. ✅ Monitor and log (Prometheus, ELK)

### Project Ideas
- **Blog API** - Posts, comments, tags, authentication
- **E-commerce API** - Products, orders, payments, inventory
- **Social Media API** - Users, posts, follows, likes
- **Project Management API** - Projects, tasks, teams, time tracking
- **Booking System API** - Reservations, availability, notifications

---

## 🛠️ Troubleshooting

### Common Issues

**Import errors:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
```bash
# Change port in the script or
lsof -ti:8000 | xargs kill
```

**Module 4 database errors:**
```bash
cd 04_database_integration
./setup_database_module.sh
alembic upgrade head
```

---

## 📦 Dependencies

See [requirements.txt](requirements.txt):

```
fastapi==0.109.0          # Web framework
uvicorn[standard]==0.27.0 # ASGI server
pydantic==2.5.3           # Data validation
sqlmodel>=0.0.14          # ORM (Module 4)
alembic>=1.13.0           # Migrations (Module 4)
psycopg2-binary>=2.9.9    # PostgreSQL (Module 4)
```

---

## 🌟 Resources

### Official Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

### Tutorials & Guides
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Real Python FastAPI Guide](https://realpython.com/fastapi-python-web-apis/)
- [TestDriven.io FastAPI](https://testdriven.io/blog/topics/fastapi/)

### Community
- [FastAPI GitHub](https://github.com/tiangolo/fastapi)
- [FastAPI Discord](https://discord.com/invite/VQjSZaeJmf)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/fastapi)

---

## 🎉 Ready to Start?

```bash
# Setup
pip install -r requirements.txt

# Start learning!
cd 01_todo_crud
python 01_todo_crud_api.py

# Open browser
http://localhost:8000/docs
```

**Happy Learning! 🚀**

---

## 📄 License

This is an educational project. Feel free to use, modify, and learn from it!

## 🤝 Contributing

This is a learning project, but suggestions and improvements are welcome!

---

**Built with ❤️ for learning FastAPI**
