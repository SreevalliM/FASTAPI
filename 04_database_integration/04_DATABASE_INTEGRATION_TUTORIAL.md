# 📚 Database Integration with FastAPI & SQLModel

## Complete Guide: SQLModel, SQLAlchemy, and Alembic Migrations

This tutorial covers database integration in FastAPI, progressing from in-memory storage to production-ready database solutions.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Setup & Installation](#setup--installation)
3. [Progression Path](#progression-path)
4. [Core Concepts](#core-concepts)
5. [Database Session Dependency](#database-session-dependency)
6. [CRUD Operations](#crud-operations)
7. [Model vs Schema Separation](#model-vs-schema-separation)
8. [Alembic Migrations](#alembic-migrations)
9. [SQLite to PostgreSQL Migration](#sqlite-to-postgresql-migration)
10. [Best Practices](#best-practices)

---

## Overview

### What You'll Learn

- ✅ Database session management with dependency injection
- ✅ CRUD operations using SQLModel
- ✅ Difference between database models and Pydantic schemas
- ✅ Database migrations with Alembic
- ✅ Switching between SQLite and PostgreSQL

### Files in This Module

| File | Description | Database |
|------|-------------|----------|
| `04_book_api_memory.py` | Baseline in-memory API | None |
| `05_book_api_sqlite.py` | SQLite implementation | SQLite |
| `06_book_api_postgres.py` | Multi-database support | SQLite/PostgreSQL |
| `book_models.py` | Shared database models | - |
| `alembic/` | Migration files | - |

---

## Setup & Installation

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually
pip install sqlmodel alembic psycopg2-binary
```

### 2. Verify Installation

```bash
python -c "import sqlmodel; print('SQLModel:', sqlmodel.__version__)"
python -c "import alembic; print('Alembic:', alembic.__version__)"
```

---

## Progression Path

### Step 1: In-Memory API (Baseline)

**File:** `04_book_api_memory.py`

```bash
# Run the in-memory version
python 04_book_api_memory.py
# Visit: http://localhost:8000/docs
```

**Characteristics:**
- ✅ Simple and fast
- ✅ Good for prototyping
- ❌ Data lost on restart
- ❌ Not suitable for production

**Test it:**
```bash
# Create a book
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "1984", "author": "George Orwell", "year": 1949}'

# Get all books
curl http://localhost:8000/books
```

### Step 2: SQLite Implementation

**File:** `05_book_api_sqlite.py`

```bash
# Run the SQLite version
python 05_book_api_sqlite.py
# Visit: http://localhost:8001/docs
```

**Characteristics:**
- ✅ Data persists across restarts
- ✅ No external database server needed
- ✅ Perfect for development
- ⚠️ Limited concurrency

**What Changed:**
1. Added `Book` SQLModel with `table=True`
2. Created database engine and session
3. Implemented `get_session()` dependency
4. Updated CRUD operations to use database

### Step 3: PostgreSQL Support

**File:** `06_book_api_postgres.py`

```bash
# Run with SQLite (default)
python 06_book_api_postgres.py

# Run with PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost/bookstore"
python 06_book_api_postgres.py
```

**Characteristics:**
- ✅ Production-ready
- ✅ High concurrency
- ✅ ACID compliance
- ✅ Advanced features (JSON, full-text search, etc.)

---

## Core Concepts

### 1. Database Session Dependency

**What is a Session?**
- A session is a workspace for database operations
- It tracks changes and manages transactions
- Must be properly opened and closed

**Implementation:**

```python
from sqlmodel import Session, create_engine

engine = create_engine("sqlite:///books.db")

def get_session():
    """
    Dependency that provides a database session.
    FastAPI will call this function for each request.
    """
    with Session(engine) as session:
        yield session  # Session is provided to the endpoint
        # Session is automatically closed after yield
```

**Usage in Endpoints:**

```python
@app.get("/books")
def get_books(session: Session = Depends(get_session)):
    # session is automatically injected
    books = session.exec(select(Book)).all()
    return books
```

**Benefits:**
- ✅ Automatic session management
- ✅ Proper cleanup even if exceptions occur
- ✅ DRY (Don't Repeat Yourself) principle
- ✅ Easy to test (can inject mock sessions)

---

### 2. CRUD Operations

CRUD = **C**reate, **R**ead, **U**pdate, **D**elete

#### Create

```python
@app.post("/books", response_model=BookRead)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    # 1. Convert Pydantic schema to database model
    db_book = Book.model_validate(book)
    
    # 2. Add to session
    session.add(db_book)
    
    # 3. Commit changes to database
    session.commit()
    
    # 4. Refresh to get auto-generated fields (id, timestamps)
    session.refresh(db_book)
    
    return db_book
```

#### Read (Single)

```python
@app.get("/books/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: Session = Depends(get_session)):
    # Get by primary key - simple and efficient
    book = session.get(Book, book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return book
```

#### Read (Multiple with Filtering)

```python
@app.get("/books", response_model=List[BookRead])
def get_books(
    skip: int = 0,
    limit: int = 100,
    author: Optional[str] = None,
    session: Session = Depends(get_session)
):
    # Build query
    query = select(Book)
    
    # Add filters
    if author:
        query = query.where(Book.author.contains(author))
    
    # Add pagination
    query = query.offset(skip).limit(limit)
    
    # Execute
    books = session.exec(query).all()
    return books
```

#### Update

```python
@app.put("/books/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    session: Session = Depends(get_session)
):
    # 1. Get existing book
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 2. Update only provided fields
    book_data = book_update.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    
    # 3. Update timestamp
    db_book.updated_at = datetime.now()
    
    # 4. Commit
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    
    return db_book
```

#### Delete

```python
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    session.delete(book)
    session.commit()
    return None
```

---

### 3. Model vs Schema Separation

This is a crucial concept for clean architecture.

#### Database Model (Table Definition)

```python
class Book(SQLModel, table=True):
    """
    DATABASE MODEL
    - Defines the actual database table structure
    - Includes table configuration (indexes, constraints)
    - Has database-specific fields (id, timestamps)
    """
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    author: str = Field(index=True, max_length=100)
    year: int
    isbn: Optional[str] = Field(default=None, unique=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

#### Pydantic Schemas (Request/Response)

```python
class BookCreate(SQLModel):
    """
    INPUT SCHEMA
    - Only fields the user provides
    - No id, no timestamps
    - Used for POST requests
    """
    title: str
    author: str
    year: int
    isbn: Optional[str] = None


class BookUpdate(SQLModel):
    """
    UPDATE SCHEMA
    - All fields are optional
    - Allows partial updates
    - Used for PUT/PATCH requests
    """
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    isbn: Optional[str] = None


class BookRead(SQLModel):
    """
    OUTPUT SCHEMA
    - Complete representation
    - Includes id and timestamps
    - Used for GET responses
    """
    id: int
    title: str
    author: str
    year: int
    isbn: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### Why Separate?

| Aspect | Reason |
|--------|--------|
| **Security** | Don't expose internal fields (passwords, internal IDs) |
| **Flexibility** | Input and output can have different fields |
| **Validation** | Different validation rules for create vs update |
| **API Evolution** | Change API without changing database |
| **Documentation** | Clear contract for API consumers |

**Example:**

```python
# User creates a book (no id, no timestamps)
POST /books
{
  "title": "1984",
  "author": "George Orwell",
  "year": 1949
}

# System returns complete book (with id and timestamps)
Response:
{
  "id": 1,
  "title": "1984",
  "author": "George Orwell",
  "year": 1949,
  "isbn": null,
  "created_at": "2026-02-14T12:00:00",
  "updated_at": "2026-02-14T12:00:00"
}
```

---

## Database Session Dependency

### Pattern Explained

```python
# 1. Define the dependency function
def get_session():
    with Session(engine) as session:
        yield session
        # Session auto-closes here

# 2. Use it in endpoints
@app.get("/books")
def get_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()
```

### What Happens Behind the Scenes?

1. Request arrives at `/books`
2. FastAPI sees `Depends(get_session)`
3. FastAPI calls `get_session()`
4. `get_session()` creates a session
5. Session is passed to `get_books()`
6. Endpoint executes
7. Response is sent
8. Control returns to `get_session()`
9. Session is automatically closed (after `yield`)

### Benefits

✅ **No manual session management** - FastAPI handles it
✅ **Automatic cleanup** - Even if exceptions occur
✅ **Testable** - Easy to inject mock sessions
✅ **Consistent** - Same pattern across all endpoints

### Testing with Mock Session

```python
def test_get_books():
    # Create test session
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Add test data
        book = Book(title="Test", author="Test Author", year=2024)
        session.add(book)
        session.commit()
        
        # Override dependency
        def override_get_session():
            yield session
        
        app.dependency_overrides[get_session] = override_get_session
        
        # Test
        response = client.get("/books")
        assert response.status_code == 200
```

---

## Alembic Migrations

### What are Migrations?

Migrations are version control for your database schema. They allow you to:
- Track schema changes over time
- Apply changes to production safely
- Rollback if something goes wrong
- Share schema changes with team members

### Why Use Migrations?

❌ **Without Migrations:**
```python
# Drop all tables and recreate
SQLModel.metadata.drop_all(engine)  # ⚠️ DATA LOSS!
SQLModel.metadata.create_all(engine)
```

✅ **With Migrations:**
```bash
# Safely add a new column
alembic revision -m "add publisher column"
alembic upgrade head  # Preserves existing data
```

### Setup Alembic

Already done in this project! But here's how:

```bash
# 1. Initialize Alembic
alembic init alembic

# 2. Configure database URL in alembic.ini
# sqlalchemy.url = sqlite:///./books.db

# 3. Update env.py to import your models
# from book_models import Book

# 4. Create initial migration
alembic revision --autogenerate -m "initial"

# 5. Apply migration
alembic upgrade head
```

### Migration Commands

```bash
# Create a new migration
alembic revision -m "description"

# Auto-generate migration from model changes
alembic revision --autogenerate -m "add column"

# Apply all pending migrations
alembic upgrade head

# Apply migrations step by step
alembic upgrade +1  # Next one
alembic upgrade +2  # Next two

# Rollback migrations
alembic downgrade -1  # Previous version
alembic downgrade base  # All the way back

# View migration history
alembic history

# Check current version
alembic current
```

### Migration File Anatomy

```python
"""Add publisher column

Revision ID: 002
Revises: 001
Create Date: 2026-02-14 12:30:00
"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '002'
down_revision = '001'  # Previous migration

def upgrade() -> None:
    """Apply changes"""
    op.add_column('books',
        sa.Column('publisher', sa.String(200), nullable=True)
    )

def downgrade() -> None:
    """Revert changes"""
    op.drop_column('books', 'publisher')
```

### Common Migration Operations

#### Add Column

```python
def upgrade():
    op.add_column('books',
        sa.Column('publisher', sa.String(200), nullable=True)
    )
```

#### Drop Column

```python
def upgrade():
    op.drop_column('books', 'old_column')
```

#### Add Index

```python
def upgrade():
    op.create_index('ix_books_publisher', 'books', ['publisher'])
```

#### Rename Column

```python
def upgrade():
    op.alter_column('books', 'old_name', new_column_name='new_name')
```

### Workflow Example

**Scenario:** Add a `publisher` field to Book model

1. **Update the model:**
```python
class Book(SQLModel, table=True):
    # ... existing fields ...
    publisher: Optional[str] = Field(default=None, max_length=200)
```

2. **Create migration:**
```bash
alembic revision --autogenerate -m "add publisher field"
```

3. **Review generated migration:**
```bash
cat alembic/versions/002_add_publisher.py
```

4. **Apply migration:**
```bash
alembic upgrade head
```

5. **Verify:**
```bash
alembic current
# Output: 002 (head), add publisher field
```

---

## SQLite to PostgreSQL Migration

### Why Migrate?

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Concurrency** | Limited | High |
| **Database Size** | < 1 TB | > 1 TB |
| **Concurrent Writes** | 1 at a time | Many |
| **Data Types** | 5 types | 40+ types |
| **Full-text Search** | Basic | Advanced |
| **JSON Support** | Basic | Native |
| **Production Use** | Small apps | Enterprise |

### Step-by-Step Migration

#### 1. Setup PostgreSQL

```bash
# macOS
brew install postgresql@14
brew services start postgresql@14

# Ubuntu
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Or use Docker
docker run --name postgres \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=bookstore \
  -p 5432:5432 \
  -d postgres:14
```

#### 2. Create Database

```bash
# Using psql
psql -U postgres
CREATE DATABASE bookstore;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE bookstore TO myuser;
\q
```

#### 3. Update Configuration

**Option A: Environment Variable**
```bash
export DATABASE_URL="postgresql://myuser:mypassword@localhost/bookstore"
python 06_book_api_postgres.py
```

**Option B: Update alembic.ini**
```ini
# alembic.ini
sqlalchemy.url = postgresql://myuser:mypassword@localhost/bookstore
```

#### 4. Run Migrations

```bash
# Apply all migrations to PostgreSQL
alembic upgrade head
```

#### 5. Verify

```bash
# Connect to PostgreSQL
psql -U myuser -d bookstore

# Check tables
\dt

# Check book table structure
\d books

# Query books
SELECT * FROM books;
```

### Data Migration

If you have data in SQLite and want to migrate it:

```python
# export_sqlite_to_postgres.py
from sqlmodel import Session, create_engine, select
from book_models import Book

# Source (SQLite)
sqlite_engine = create_engine("sqlite:///books.db")

# Destination (PostgreSQL)
postgres_engine = create_engine(
    "postgresql://myuser:mypassword@localhost/bookstore"
)

# Read from SQLite
with Session(sqlite_engine) as source:
    books = source.exec(select(Book)).all()

# Write to PostgreSQL
with Session(postgres_engine) as dest:
    for book in books:
        # Create new instance without id (let PostgreSQL generate it)
        new_book = Book(
            title=book.title,
            author=book.author,
            year=book.year,
            isbn=book.isbn,
            description=book.description,
            created_at=book.created_at,
            updated_at=book.updated_at
        )
        dest.add(new_book)
    dest.commit()

print(f"Migrated {len(books)} books to PostgreSQL")
```

Run migration:
```bash
python export_sqlite_to_postgres.py
```

---

## Best Practices

### 1. Database Session Management

✅ **DO:**
```python
def get_session():
    with Session(engine) as session:
        yield session  # Auto-closes
```

❌ **DON'T:**
```python
session = Session(engine)  # Never closes!
```

### 2. Query Optimization

✅ **DO:** Use select() for queries
```python
query = select(Book).where(Book.author == "Orwell")
books = session.exec(query).all()
```

❌ **DON'T:** Load all then filter in Python
```python
books = session.exec(select(Book)).all()
books = [b for b in books if b.author == "Orwell"]  # Slow!
```

### 3. Indexes

✅ **DO:** Add indexes for frequently queried fields
```python
class Book(SQLModel, table=True):
    author: str = Field(index=True)  # Fast author queries
    isbn: str = Field(unique=True, index=True)  # Fast ISBN lookup
```

### 4. Validation

✅ **DO:** Validate at schema level
```python
class BookCreate(SQLModel):
    year: int = Field(ge=1000, le=2100)  # Valid years
    isbn: Optional[str] = Field(pattern=r'^\d{13}$')  # Valid ISBN
```

### 5. Migrations

✅ **DO:**
- Review autogenerated migrations
- Test migrations on copy of production data
- Keep migrations in version control
- Never modify applied migrations

❌ **DON'T:**
- Auto-apply migrations in production
- Delete migration files
- Modify migrations after applying
- Use `drop_all()` in production

### 6. Environment Configuration

✅ **DO:** Use environment variables
```python
database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
```

❌ **DON'T:** Hardcode credentials
```python
database_url = "postgresql://admin:password123@localhost/db"  # ⚠️
```

### 7. Error Handling

✅ **DO:** Handle database errors gracefully
```python
try:
    session.add(book)
    session.commit()
except IntegrityError:
    session.rollback()
    raise HTTPException(status_code=400, detail="Duplicate ISBN")
```

### 8. Testing

✅ **DO:** Use in-memory database for tests
```python
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

---

## Practice Exercises

### Exercise 1: Add Genre Field

1. Add `genre` field to Book model
2. Create and apply migration
3. Update CRUD endpoints
4. Test with various genres

### Exercise 2: Search Functionality

Implement advanced search:
```python
@app.get("/books/search")
def search_books(
    q: str,  # Search query
    session: Session = Depends(get_session)
):
    query = select(Book).where(
        or_(
            Book.title.contains(q),
            Book.author.contains(q),
            Book.description.contains(q)
        )
    )
    return session.exec(query).all()
```

### Exercise 3: Advanced Filters

Add compound filtering:
```python
@app.get("/books")
def get_books(
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    genres: Optional[List[str]] = Query(None),
    session: Session = Depends(get_session)
):
    # Implement filtering logic
    pass
```

### Exercise 4: Pagination Metadata

Return pagination info:
```python
class PaginatedResponse(BaseModel):
    items: List[BookRead]
    total: int
    page: int
    pages: int

@app.get("/books", response_model=PaginatedResponse)
def get_books(page: int = 1, size: int = 10, ...):
    # Implement pagination with metadata
    pass
```

---

## Troubleshooting

### Common Issues

**1. "Table already exists" error**
```bash
# Solution: Use Alembic or drop existing tables
alembic upgrade head  # Preferred

# Or in development only:
rm books.db
python your_app.py
```

**2. "No such table" error**
```bash
# Solution: Create tables
alembic upgrade head

# Or if not using Alembic:
# Add in your startup code:
SQLModel.metadata.create_all(engine)
```

**3. Migration conflicts**
```bash
# Solution: Check migration history
alembic history
alembic current

# If needed, rollback and reapply
alembic downgrade -1
alembic upgrade head
```

**4. PostgreSQL connection refused**
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string
echo $DATABASE_URL

# Test connection
psql postgresql://user:password@localhost/dbname
```

---

## Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Tutorials
- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel Tutorial](https://sqlmodel.tiangolo.com/tutorial/)

### Tools
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL management
- [DBeaver](https://dbeaver.io/) - Universal database tool

---

## Summary

### Key Takeaways

1. ✅ **Database Session Dependency** - Use `Depends(get_session)` for automatic session management
2. ✅ **CRUD Operations** - add, get, exec, commit, refresh, delete
3. ✅ **Model Separation** - Database models vs API schemas serve different purposes
4. ✅ **Migrations** - Use Alembic for safe schema evolution
5. ✅ **Database Choice** - SQLite for development, PostgreSQL for production

### Progression Reminder

```
In-Memory → SQLite → PostgreSQL
   (Dev)      (Dev)    (Production)
```

### Next Steps

1. ✅ Complete the practice exercises
2. ✅ Experiment with different query patterns
3. ✅ Set up PostgreSQL locally
4. ✅ Practice creating and applying migrations
5. ✅ Build your own API with database integration

---

**Happy Coding! 🚀**
