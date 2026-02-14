# 📁 FastAPI Learning Project Structure

## Overview

This project is organized into self-contained modules, each focusing on a specific FastAPI concept. Each module has its own folder with all related files.

## 🗂️ Project Structure

```
FASTAPI/
├── README.md                          # Main project documentation
├── QUICKSTART.md                      # Quick start guide
├── PROJECT_STRUCTURE.md              # This file
├── requirements.txt                   # Project dependencies
├── fastapi-env/                      # Virtual environment
│
├── 01_todo_crud/                     # Module 1: Basic CRUD
│   ├── README.md                     # Module guide
│   └── 01_todo_crud_api.py          # Todo API implementation
│
├── 02_request_validation/            # Module 2: Validation
│   ├── README.md                     # Module guide
│   └── 02_request_validation.py     # User API with validation
│
├── 03_dependency_injection/          # Module 3: Dependency Injection
│   ├── README.md                     # Module guide
│   ├── 03_dependency_injection.py   # DI examples
│   ├── 03_DI_TUTORIAL.md           # Detailed tutorial
│   ├── DEPENDENCY_CHEATSHEET.md    # Quick reference
│   └── test_dependency_injection.py # Tests
│
└── 04_database_integration/         # Module 4: Database Integration
    ├── README.md                     # Module guide (04_DATABASE_MODULE_README.md)
    ├── 04_book_api_memory.py        # In-memory baseline
    ├── 05_book_api_sqlite.py        # SQLite implementation
    ├── 06_book_api_postgres.py      # PostgreSQL support
    ├── book_models.py                # Shared database models
    ├── 04_DATABASE_INTEGRATION_TUTORIAL.md  # Complete tutorial
    ├── DATABASE_QUICK_REFERENCE.md   # Quick reference
    ├── database_exercises.py         # Practice exercises
    ├── alembic.ini                   # Alembic configuration
    ├── alembic_guide.sh             # Migration commands
    ├── setup_database_module.sh     # Setup script
    └── alembic/                      # Migration files
        ├── env.py
        ├── script.py.mako
        └── versions/
            ├── 001_initial_migration.py
            └── 002_add_publisher.py
```

## 📚 Learning Path

### Module 1: Todo CRUD API
**Focus:** Basic CRUD operations with FastAPI

- Build a simple Todo API
- Learn HTTP methods (GET, POST, PUT, DELETE)
- Work with Pydantic models
- Use path and query parameters

📂 Location: [01_todo_crud/](01_todo_crud/)

### Module 2: Request Validation
**Focus:** Advanced input validation

- Validate user input with Pydantic
- Use Field validators and constraints
- Handle validation errors
- Work with complex data types

📂 Location: [02_request_validation/](02_request_validation/)

### Module 3: Dependency Injection
**Focus:** Dependency injection patterns

- Understand DI concepts
- Create reusable dependencies
- Implement authentication
- Test with dependency overrides

📂 Location: [03_dependency_injection/](03_dependency_injection/)

### Module 4: Database Integration
**Focus:** SQLModel/SQLAlchemy integration

- Database session management
- CRUD with SQLModel
- Alembic migrations
- SQLite → PostgreSQL migration

📂 Location: [04_database_integration/](04_database_integration/)

## 🚀 Getting Started

### 1. Setup Environment

```bash
# Create/activate virtual environment
python -m venv fastapi-env
source fastapi-env/bin/activate  # macOS/Linux
# or
fastapi-env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Start with Module 1

```bash
cd 01_todo_crud
python 01_todo_crud_api.py
```

Visit: http://localhost:8000/docs

### 3. Progress Through Modules

Work through each module in order, as concepts build on each other.

## 📖 Documentation Files

Each module contains its own documentation:

| Module | Main Doc | Additional Docs |
|--------|----------|----------------|
| 1 | README.md | - |
| 2 | README.md | - |
| 3 | README.md | 03_DI_TUTORIAL.md, DEPENDENCY_CHEATSHEET.md |
| 4 | 04_DATABASE_MODULE_README.md | 04_DATABASE_INTEGRATION_TUTORIAL.md, DATABASE_QUICK_REFERENCE.md |

## 🧪 Running Tests

```bash
# Module 3 tests
cd 03_dependency_injection
pytest test_dependency_injection.py

# Add more tests as you build
```

## 🔧 Running Different Modules

Each module runs independently:

```bash
# Module 1 - Port 8000
python 01_todo_crud/01_todo_crud_api.py

# Module 2 - Port 8000
python 02_request_validation/02_request_validation.py

# Module 3 - Port 8000
python 03_dependency_injection/03_dependency_injection.py

# Module 4 - Multiple ports
python 04_database_integration/04_book_api_memory.py     # Port 8000
python 04_database_integration/05_book_api_sqlite.py     # Port 8001
python 04_database_integration/06_book_api_postgres.py   # Port 8002
```

## 💡 Tips

1. **Start from Module 1** - Concepts build progressively
2. **Read the README** - Each module has specific instructions
3. **Use the docs** - Interactive docs at `/docs` endpoint
4. **Complete exercises** - Hands-on practice reinforces learning
5. **Keep modules running** - Different ports allow comparison

## 🗄️ Database Files

Module 4 creates database files in its directory:

```
04_database_integration/
├── books.db              # SQLite database (created at runtime)
└── alembic/
    └── versions/         # Migration history
```

These are gitignored and created when you run the applications.

## 🎯 Next Steps

After completing all modules:

1. Build your own API project
2. Combine concepts from all modules
3. Deploy to production
4. Explore advanced topics (async, websockets, etc.)

## 📞 Module Quick Links

- [Module 1: Todo CRUD](01_todo_crud/)
- [Module 2: Request Validation](02_request_validation/)
- [Module 3: Dependency Injection](03_dependency_injection/)
- [Module 4: Database Integration](04_database_integration/)

## 🔄 Updates

When adding new modules:

1. Create a new numbered directory (e.g., `05_new_module/`)
2. Add module files
3. Create module README.md
4. Update this file
5. Update main README.md

---

**Ready to learn? Start with [Module 1](01_todo_crud/)!** 🚀
