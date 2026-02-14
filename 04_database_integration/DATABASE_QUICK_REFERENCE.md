# 🚀 Database Integration Quick Reference

## Essential Commands

### Run Applications
```bash
# In-memory version
python 04_book_api_memory.py  # http://localhost:8000

# SQLite version
python 05_book_api_sqlite.py  # http://localhost:8001

# PostgreSQL/SQLite version
python 06_book_api_postgres.py  # http://localhost:8002
```

### Alembic Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Check status
alembic current
alembic history
```

### PostgreSQL Setup
```bash
# Using Docker (easiest)
docker run --name postgres \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=bookstore \
  -p 5432:5432 -d postgres:14

# Set environment variable
export DATABASE_URL="postgresql://postgres:mypassword@localhost/bookstore"

# Run migrations
alembic upgrade head

# Start API
python 06_book_api_postgres.py
```

---

## Code Patterns

### Database Session Dependency
```python
from sqlmodel import Session, create_engine

engine = create_engine("sqlite:///books.db")

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/books")
def get_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()
```

### CRUD Operations

**Create**
```python
db_book = Book.model_validate(book)
session.add(db_book)
session.commit()
session.refresh(db_book)
return db_book
```

**Read**
```python
# Single
book = session.get(Book, book_id)

# Multiple
books = session.exec(select(Book)).all()

# Filtered
query = select(Book).where(Book.author == "Orwell")
books = session.exec(query).all()
```

**Update**
```python
book_data = book_update.model_dump(exclude_unset=True)
for key, value in book_data.items():
    setattr(db_book, key, value)
session.add(db_book)
session.commit()
session.refresh(db_book)
```

**Delete**
```python
session.delete(book)
session.commit()
```

### Model Definition
```python
class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    author: str = Field(index=True, max_length=100)
    isbn: Optional[str] = Field(default=None, unique=True)
```

### Query Patterns
```python
# Simple select
select(Book)

# With filter
select(Book).where(Book.year > 2000)

# Multiple conditions
select(Book).where(
    and_(Book.year > 2000, Book.author == "Orwell")
)

# OR conditions
select(Book).where(
    or_(Book.author == "Orwell", Book.author == "Huxley")
)

# LIKE/contains
select(Book).where(Book.title.contains("Python"))

# Ordering
select(Book).order_by(Book.year.desc())

# Pagination
select(Book).offset(0).limit(10)
```

---

## Testing Endpoints

### Create Book
```bash
curl -X POST http://localhost:8001/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "year": 1949,
    "isbn": "1234567890123",
    "description": "Dystopian novel"
  }'
```

### Get All Books
```bash
curl http://localhost:8001/books
```

### Get Book by ID
```bash
curl http://localhost:8001/books/1
```

### Update Book
```bash
curl -X PUT http://localhost:8001/books/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nineteen Eighty-Four",
    "description": "Classic dystopian novel"
  }'
```

### Delete Book
```bash
curl -X DELETE http://localhost:8001/books/1
```

### Filter Books
```bash
# By author
curl "http://localhost:8001/books?author=Orwell"

# By year
curl "http://localhost:8001/books?year=1949"

# Pagination
curl "http://localhost:8001/books?skip=0&limit=10"
```

### Health Check
```bash
curl http://localhost:8002/health
```

### Statistics
```bash
curl http://localhost:8001/books/stats/summary
```

---

## Model vs Schema

| Purpose | Class | Fields |
|---------|-------|--------|
| **Table** | `Book(SQLModel, table=True)` | All fields + id, timestamps |
| **Input** | `BookCreate(SQLModel)` | Only user-provided fields |
| **Update** | `BookUpdate(SQLModel)` | All optional fields |
| **Output** | `BookRead(SQLModel)` | All fields including computed |

---

## Migration Workflow

1. **Modify Model**
   ```python
   class Book(SQLModel, table=True):
       # Add new field
       publisher: Optional[str] = None
   ```

2. **Generate Migration**
   ```bash
   alembic revision --autogenerate -m "add publisher"
   ```

3. **Review Migration**
   ```bash
   cat alembic/versions/002_add_publisher.py
   ```

4. **Apply Migration**
   ```bash
   alembic upgrade head
   ```

5. **Verify**
   ```bash
   alembic current
   ```

---

## Environment Variables

```bash
# SQLite (default)
python app.py

# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost/dbname"
python app.py

# Or individual components
export DB_USER="myuser"
export DB_PASSWORD="mypassword"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="bookstore"
python app.py
```

---

## Common Errors & Solutions

| Error | Solution |
|-------|----------|
| Table already exists | Use Alembic: `alembic upgrade head` |
| No such table | Create tables: `alembic upgrade head` |
| Connection refused | Check PostgreSQL is running |
| Duplicate key | Check unique constraints |
| Session closed | Use dependency injection properly |

---

## File Structure

```
FASTAPI/
├── 04_book_api_memory.py      # In-memory baseline
├── 05_book_api_sqlite.py      # SQLite version
├── 06_book_api_postgres.py    # Multi-database support
├── book_models.py              # Shared models
├── alembic.ini                 # Alembic config
├── alembic/
│   ├── env.py                  # Alembic environment
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
│       ├── 001_initial.py
│       └── 002_add_publisher.py
└── requirements.txt            # Dependencies
```

---

## Best Practices Checklist

- ✅ Use dependency injection for sessions
- ✅ Separate models and schemas
- ✅ Add indexes for queried fields
- ✅ Use Alembic for schema changes
- ✅ Validate input with Pydantic
- ✅ Handle errors gracefully
- ✅ Use environment variables for config
- ✅ Test with in-memory database
- ✅ SQLite for dev, PostgreSQL for prod
- ✅ Review autogenerated migrations

---

## Quick Installation

```bash
# Install dependencies
pip install fastapi uvicorn sqlmodel alembic psycopg2-binary

# Initialize Alembic (if needed)
alembic init alembic

# Run migrations
alembic upgrade head

# Start API
uvicorn 06_book_api_postgres:app --reload
```

---

## Resources

- **Tutorial**: `04_DATABASE_INTEGRATION_TUTORIAL.md`
- **Alembic Guide**: `alembic_guide.sh`
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLModel Docs**: https://sqlmodel.tiangolo.com
- **Alembic Docs**: https://alembic.sqlalchemy.org
