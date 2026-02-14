# 🎯 Module 4: SQLModel / SQLAlchemy Integration

## Complete Database Integration Learning Module

This module teaches you how to integrate databases with FastAPI, progressing from in-memory storage to production-ready database solutions.

---

## 📦 What's Included

### Core API Files
| File | Purpose | Port | Database |
|------|---------|------|----------|
| [04_book_api_memory.py](04_book_api_memory.py) | Baseline in-memory API | 8000 | None (in-memory) |
| [05_book_api_sqlite.py](05_book_api_sqlite.py) | SQLite implementation | 8001 | SQLite |
| [06_book_api_postgres.py](06_book_api_postgres.py) | Multi-database support | 8002 | SQLite/PostgreSQL |
| [book_models.py](book_models.py) | Shared database models | - | - |

### Documentation
| File | Description |
|------|-------------|
| [04_DATABASE_INTEGRATION_TUTORIAL.md](04_DATABASE_INTEGRATION_TUTORIAL.md) | Complete tutorial with examples |
| [DATABASE_QUICK_REFERENCE.md](DATABASE_QUICK_REFERENCE.md) | Quick reference cheatsheet |
| [database_exercises.py](database_exercises.py) | Hands-on practice exercises |

### Migration Files
| Path | Description |
|------|-------------|
| [alembic.ini](alembic.ini) | Alembic configuration |
| [alembic/env.py](alembic/env.py) | Migration environment setup |
| [alembic/versions/](alembic/versions/) | Migration version files |
| [alembic_guide.sh](alembic_guide.sh) | Alembic commands reference |

---

## 🚀 Quick Start

### 1. Setup
```bash
# Run setup script
./setup_database_module.sh

# Or manually:
source fastapi-env/bin/activate
pip install -r requirements.txt
```

### 2. Start Learning

#### Step 1: In-Memory Baseline
```bash
python 04_book_api_memory.py
# Visit: http://localhost:8000/docs
```

#### Step 2: SQLite Implementation
```bash
python 05_book_api_sqlite.py
# Visit: http://localhost:8001/docs
```

#### Step 3: PostgreSQL Support
```bash
# Option A: Use SQLite (default)
python 06_book_api_postgres.py

# Option B: Use PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost/bookstore"
python 06_book_api_postgres.py
# Visit: http://localhost:8002/docs
```

---

## 📚 Learning Path

### 1. Concepts (Read First)
Start with the [complete tutorial](04_DATABASE_INTEGRATION_TUTORIAL.md) which covers:
- Database session dependency
- CRUD operations
- Model vs Schema separation
- Alembic migrations
- SQLite to PostgreSQL migration

### 2. Practice (Hands-On)
Follow [database_exercises.py](database_exercises.py) for practical exercises:
- Run and test all three API versions
- Create and apply migrations
- Query databases directly
- Set up PostgreSQL
- Write tests

### 3. Reference (Quick Lookup)
Use [DATABASE_QUICK_REFERENCE.md](DATABASE_QUICK_REFERENCE.md) for:
- Command cheatsheet
- Code patterns
- Testing endpoints
- Common errors

---

## 🎓 What You'll Learn

### Core Concepts
✅ **Database Session Dependency** - Automatic session management with dependency injection  
✅ **CRUD Operations** - Create, Read, Update, Delete with SQLModel  
✅ **Model vs Schema Separation** - Database models vs API schemas  
✅ **Alembic Migrations** - Safe schema evolution  
✅ **Database Switching** - SQLite for dev, PostgreSQL for production  

### Hands-On Skills
✅ Build a complete Book API with database persistence  
✅ Write complex queries with filtering and pagination  
✅ Create and apply database migrations  
✅ Set up PostgreSQL locally or with Docker  
✅ Migrate data between databases  
✅ Test database endpoints  

---

## 🔧 Technologies Used

| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | Web framework | 0.109.0 |
| **SQLModel** | ORM (combines SQLAlchemy + Pydantic) | 0.0.14+ |
| **Alembic** | Database migrations | 1.13.0+ |
| **SQLite** | Development database | Built-in |
| **PostgreSQL** | Production database | 14+ |
| **psycopg2** | PostgreSQL driver | 2.9.9+ |

---

## 📋 Prerequisites

### Required
- Python 3.10+
- Basic FastAPI knowledge (modules 1-3)
- Understanding of SQL basics

### Optional (for PostgreSQL practice)
- Docker Desktop
- PostgreSQL 14+
- Database client (pgAdmin, DBeaver, etc.)

---

## 🗂️ Project Structure

```
FASTAPI/
├── 04_book_api_memory.py              # In-memory baseline
├── 05_book_api_sqlite.py              # SQLite version
├── 06_book_api_postgres.py            # Multi-database version
├── book_models.py                      # Shared models
│
├── 04_DATABASE_INTEGRATION_TUTORIAL.md # Main tutorial
├── DATABASE_QUICK_REFERENCE.md         # Cheatsheet
├── database_exercises.py               # Practice exercises
│
├── alembic.ini                         # Alembic config
├── alembic/
│   ├── env.py                          # Migration environment
│   ├── script.py.mako                  # Migration template
│   └── versions/                       # Migration files
│       ├── 001_initial_migration.py
│       └── 002_add_publisher.py
│
├── alembic_guide.sh                    # Alembic commands
├── setup_database_module.sh            # Setup script
│
└── requirements.txt                    # Dependencies
```

---

## 🎯 Getting Started Guide

### For Beginners

1. **Read the tutorial** ([04_DATABASE_INTEGRATION_TUTORIAL.md](04_DATABASE_INTEGRATION_TUTORIAL.md))
   - Understand core concepts
   - Follow code examples
   - Read best practices

2. **Run the examples**
   ```bash
   # Start with in-memory
   python 04_book_api_memory.py
   
   # Then try SQLite
   python 05_book_api_sqlite.py
   ```

3. **Complete exercises** ([database_exercises.py](database_exercises.py))
   - Start with Exercise 1
   - Work through each exercise
   - Check your understanding

4. **Reference as needed** ([DATABASE_QUICK_REFERENCE.md](DATABASE_QUICK_REFERENCE.md))
   - Quick command lookup
   - Code patterns
   - Testing examples

### For Advanced Users

1. **Jump to PostgreSQL**
   ```bash
   # Start PostgreSQL with Docker
   docker run --name postgres \
     -e POSTGRES_PASSWORD=mypassword \
     -e POSTGRES_DB=bookstore \
     -p 5432:5432 -d postgres:14
   
   # Set environment
   export DATABASE_URL="postgresql://postgres:mypassword@localhost/bookstore"
   
   # Run migrations
   alembic upgrade head
   
   # Start API
   python 06_book_api_postgres.py
   ```

2. **Complete advanced exercises**
   - Soft delete implementation
   - Full-text search
   - Database relationships
   - Async operations

3. **Build your own API**
   - Apply these patterns to your project
   - Experiment with different schemas
   - Optimize queries

---

## 📊 API Endpoints

All three implementations provide these endpoints:

### Books CRUD
- `POST /books` - Create a new book
- `GET /books` - List all books (with filters)
- `GET /books/{id}` - Get a specific book
- `PUT /books/{id}` - Update a book
- `DELETE /books/{id}` - Delete a book

### Utility
- `GET /` - API information
- `GET /health` - Health check (06 only)
- `GET /books/stats/summary` - Statistics

### Interactive Docs
- `/docs` - Swagger UI
- `/redoc` - ReDoc

---

## 🧪 Testing Examples

### Using curl
```bash
# Create a book
curl -X POST http://localhost:8001/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "year": 1949,
    "isbn": "1234567890123"
  }'

# Get all books
curl http://localhost:8001/books

# Filter by author
curl "http://localhost:8001/books?author=Orwell"

# Get book by ID
curl http://localhost:8001/books/1

# Update book
curl -X PUT http://localhost:8001/books/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "Classic dystopian novel"}'

# Delete book
curl -X DELETE http://localhost:8001/books/1
```

### Using Python requests
```python
import requests

# Create book
response = requests.post(
    "http://localhost:8001/books",
    json={
        "title": "1984",
        "author": "George Orwell",
        "year": 1949
    }
)
print(response.json())

# Get books
books = requests.get("http://localhost:8001/books").json()
print(books)
```

---

## 🗄️ Database Commands

### SQLite
```bash
# Open database
sqlite3 books.db

# List tables
.tables

# Show table structure
.schema books

# Query books
SELECT * FROM books;

# Exit
.exit
```

### PostgreSQL
```bash
# Connect with Docker
docker exec -it postgres psql -U postgres -d bookstore

# Or directly
psql -U postgres -d bookstore

# List tables
\dt

# Show table structure
\d books

# Query books
SELECT * FROM books;

# Exit
\q
```

### Alembic
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Show history
alembic history

# Current version
alembic current
```

---

## 🐛 Troubleshooting

### Import errors
```bash
# Install dependencies
pip install -r requirements.txt

# Verify
python -c "import sqlmodel; print(sqlmodel.__version__)"
```

### Database locked (SQLite)
```bash
# Close all connections to the database
# Restart your application
```

### PostgreSQL connection refused
```bash
# Check if PostgreSQL is running
docker ps

# Or for local installation
pg_isready

# Restart PostgreSQL
docker restart postgres
```

### Migration conflicts
```bash
# Check current state
alembic current
alembic history

# Rollback if needed
alembic downgrade -1

# Reapply
alembic upgrade head
```

---

## 📖 Additional Resources

### Documentation
- [FastAPI SQL Databases Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Tools
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [pgAdmin 4](https://www.pgadmin.org/)
- [DBeaver](https://dbeaver.io/)
- [Postman](https://www.postman.com/)

---

## ✅ Success Checklist

After completing this module, you should be able to:

- [ ] Explain the difference between in-memory, SQLite, and PostgreSQL
- [ ] Create and use database session dependencies
- [ ] Perform CRUD operations with SQLModel
- [ ] Write complex queries with filters and pagination
- [ ] Distinguish between database models and API schemas
- [ ] Create and apply Alembic migrations
- [ ] Migrate data between databases
- [ ] Set up PostgreSQL locally or with Docker
- [ ] Test database endpoints
- [ ] Handle database errors gracefully
- [ ] Use environment variables for configuration
- [ ] Optimize queries with indexes
- [ ] Implement best practices for database integration

---

## 🚀 Next Steps

### Practice Projects
Build these APIs to solidify your learning:

1. **Todo List API** - Tasks with categories and due dates
2. **Blog API** - Posts, comments, and tags with relationships
3. **E-commerce API** - Products, orders, and inventory
4. **Social Media API** - Users, posts, and follows
5. **Project Management API** - Projects, tasks, and team members

### Advanced Topics
- Async database operations
- Connection pooling
- Database replication
- Caching strategies (Redis)
- Full-text search
- Database optimization
- Monitoring and logging

---

## 📞 Support

Having trouble? Here's how to get help:

1. **Read the tutorial** - Most questions are answered there
2. **Check the quick reference** - For syntax and commands
3. **Review exercises** - Solutions and examples included
4. **Check errors** - Read error messages carefully
5. **Consult documentation** - Official docs are comprehensive

---

## 🎉 Ready to Start?

```bash
# Setup
./setup_database_module.sh

# Learn
open 04_DATABASE_INTEGRATION_TUTORIAL.md

# Practice
python 04_book_api_memory.py

# Master
# Complete all exercises in database_exercises.py
```

**Happy Learning! 📚🚀**
