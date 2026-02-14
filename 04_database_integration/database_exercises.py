"""
Practical Exercise: Database Integration with FastAPI
Complete these exercises to master database integration concepts.
"""

# ============================================================================
# EXERCISE 1: Run and Test the In-Memory API
# ============================================================================

"""
TASK:
1. Run 04_book_api_memory.py
2. Test all CRUD endpoints using curl or the /docs interface
3. Restart the server and observe what happens to your data

COMMANDS:
python 04_book_api_memory.py

Then visit: http://localhost:8000/docs

QUESTIONS TO ANSWER:
- What happens to the data when you restart the server?
- What's the limitation of this approach?
- When would you use this approach?
"""

# ============================================================================
# EXERCISE 2: SQLite Implementation
# ============================================================================

"""
TASK:
1. Run 05_book_api_sqlite.py
2. Add several books
3. Stop the server
4. Restart the server
5. Check if books are still there

COMMANDS:
python 05_book_api_sqlite.py

OBSERVE:
- A new file 'books.db' should appear
- Data persists across restarts

QUESTIONS TO ANSWER:
- Where is the data stored?
- What's the advantage over in-memory storage?
- Can you see the SQL being executed? (Check the console output)
"""

# ============================================================================
# EXERCISE 3: Database Exploration
# ============================================================================

"""
TASK:
1. Explore the SQLite database using sqlite3 command-line tool
2. View the table structure
3. Query the data directly

COMMANDS:
sqlite3 books.db

Then in sqlite3:
.tables                    -- List all tables
.schema books             -- Show table structure
SELECT * FROM books;      -- Query all books
SELECT * FROM books WHERE author LIKE '%Orwell%';
.exit                     -- Exit sqlite3

QUESTIONS TO ANSWER:
- What columns does the books table have?
- Are there any indexes created?
- Can you see the timestamps?
"""

# ============================================================================
# EXERCISE 4: Add a New Field with Migration
# ============================================================================

"""
TASK:
1. Add a 'publisher' field to the Book model in book_models.py
2. Create an Alembic migration
3. Apply the migration
4. Test the API with the new field

STEP-BY-STEP:

1. Edit book_models.py and add:
   publisher: Optional[str] = Field(default=None, max_length=200)

2. Create migration:
   alembic revision --autogenerate -m "add publisher field"

3. Apply migration:
   alembic upgrade head

4. Test:
   - Create a book with publisher field
   - Update an existing book to add publisher
   - Query books to see publisher field

EXPECTED OUTCOME:
- New migration file created
- Database updated with publisher column
- API accepts and returns publisher field
"""

# ============================================================================
# EXERCISE 5: Complex Queries
# ============================================================================

"""
TASK:
Create a new endpoint that finds books by multiple criteria

ADD THIS TO 05_book_api_sqlite.py or 06_book_api_postgres.py:
"""

from fastapi import Query
from sqlmodel import or_, and_

@app.get("/books/advanced-search")
def advanced_search(
    title: Optional[str] = None,
    author: Optional[str] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """
    Search books with multiple optional filters
    
    YOUR TASK: Implement this function!
    
    REQUIREMENTS:
    - If title provided: search books containing the title (case-insensitive)
    - If author provided: search books by author (case-insensitive)
    - If min_year provided: only books published on or after min_year
    - If max_year provided: only books published on or before max_year
    - All filters should work together (AND logic)
    
    HINTS:
    - Start with: query = select(Book)
    - Use .where() to add conditions
    - Use Book.title.contains() for partial matching
    - Use Book.year >= min_year for year filtering
    
    TEST CASES:
    - /books/advanced-search?author=Orwell
    - /books/advanced-search?min_year=1940&max_year=1950
    - /books/advanced-search?title=Python&min_year=2020
    """
    query = select(Book)
    
    # TODO: Add your filter logic here
    
    # Execute query
    books = session.exec(query).all()
    return books


# ============================================================================
# EXERCISE 6: Aggregation Queries
# ============================================================================

"""
TASK:
Create an endpoint that provides detailed statistics

ADD THIS ENDPOINT:
"""

from sqlalchemy import func

@app.get("/books/stats/detailed")
def detailed_statistics(session: Session = Depends(get_session)):
    """
    Return detailed book statistics
    
    YOUR TASK: Implement this function!
    
    REQUIREMENTS:
    Calculate and return:
    - Total number of books
    - Number of unique authors
    - Average publication year
    - Earliest publication year
    - Latest publication year
    - Books per author (dictionary)
    - Books per decade (dictionary)
    
    HINTS:
    - Get all books: session.exec(select(Book)).all()
    - Use Python collections: Counter, defaultdict
    - Group by decade: year // 10 * 10
    
    EXPECTED OUTPUT:
    {
        "total_books": 10,
        "unique_authors": 5,
        "avg_year": 1995,
        "earliest_year": 1949,
        "latest_year": 2023,
        "books_per_author": {
            "George Orwell": 2,
            "Aldous Huxley": 1
        },
        "books_per_decade": {
            "1940": 2,
            "2020": 3
        }
    }
    """
    books = session.exec(select(Book)).all()
    
    # TODO: Calculate statistics
    
    return {
        "total_books": 0,  # Replace with actual count
        "unique_authors": 0,  # Replace with calculation
        # ... add more statistics
    }


# ============================================================================
# EXERCISE 7: PostgreSQL Setup
# ============================================================================

"""
TASK:
Set up PostgreSQL and migrate your SQLite data to it

STEPS:

1. Start PostgreSQL with Docker:
   docker run --name postgres \\
     -e POSTGRES_PASSWORD=mypassword \\
     -e POSTGRES_DB=bookstore \\
     -p 5432:5432 -d postgres:14

2. Verify it's running:
   docker ps

3. Connect and explore:
   docker exec -it postgres psql -U postgres -d bookstore
   
   In psql:
   \\dt                    -- List tables (should be empty)
   \\q                     -- Quit

4. Set environment variable:
   export DATABASE_URL="postgresql://postgres:mypassword@localhost/bookstore"

5. Run migrations:
   alembic upgrade head

6. Start the API:
   python 06_book_api_postgres.py

7. Check health endpoint:
   curl http://localhost:8002/health

8. Add some books

9. Verify in PostgreSQL:
   docker exec -it postgres psql -U postgres -d bookstore
   SELECT * FROM books;

QUESTIONS TO ANSWER:
- Can you connect to PostgreSQL?
- Are migrations applied successfully?
- Can you see the books in PostgreSQL?
- What's the difference in performance compared to SQLite?
"""

# ============================================================================
# EXERCISE 8: Data Migration Script
# ============================================================================

"""
TASK:
Create a script to migrate data from SQLite to PostgreSQL

CREATE FILE: migrate_data.py
"""

from sqlmodel import Session, create_engine, select
from book_models import Book

def migrate_sqlite_to_postgres():
    """
    Migrate all books from SQLite to PostgreSQL
    
    YOUR TASK: Complete this function!
    
    REQUIREMENTS:
    1. Connect to both databases
    2. Read all books from SQLite
    3. Create new books in PostgreSQL
    4. Handle conflicts (check if book exists)
    5. Print progress
    
    HINTS:
    - Use separate engines for SQLite and PostgreSQL
    - Check for existing ISBN before inserting
    - Skip id field (let PostgreSQL generate it)
    """
    
    # TODO: Create SQLite engine
    sqlite_engine = create_engine("sqlite:///books.db")
    
    # TODO: Create PostgreSQL engine
    postgres_url = "postgresql://postgres:mypassword@localhost/bookstore"
    postgres_engine = create_engine(postgres_url)
    
    # TODO: Read from SQLite
    with Session(sqlite_engine) as sqlite_session:
        books = []  # Get all books from SQLite
    
    # TODO: Write to PostgreSQL
    with Session(postgres_engine) as pg_session:
        pass  # Write books to PostgreSQL
    
    print(f"Migration complete!")

if __name__ == "__main__":
    migrate_sqlite_to_postgres()


# ============================================================================
# EXERCISE 9: Test Your API
# ============================================================================

"""
TASK:
Write tests for your Book API

CREATE FILE: test_book_api.py
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from book_models import Book

# TODO: Import your app
# from your_api_file import app, get_session

@pytest.fixture(name="session")
def session_fixture():
    """
    Create a test database session
    
    YOUR TASK: Complete this fixture!
    
    REQUIREMENTS:
    - Use in-memory SQLite: "sqlite:///:memory:"
    - Create all tables
    - Yield session
    - Clean up after test
    """
    # TODO: Create test engine
    engine = create_engine("sqlite:///:memory:")
    
    # TODO: Create tables
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create test client with overridden dependency
    
    YOUR TASK: Complete this fixture!
    """
    # TODO: Override get_session dependency
    # app.dependency_overrides[get_session] = lambda: session
    
    # TODO: Create and return TestClient
    # client = TestClient(app)
    # yield client
    
    pass


def test_create_book(client: TestClient):
    """
    Test creating a book
    
    YOUR TASK: Write this test!
    
    TEST CASES:
    - Create valid book
    - Create book with missing fields
    - Create book with invalid year
    - Create duplicate ISBN
    """
    # TODO: Test POST /books
    pass


def test_get_books(client: TestClient):
    """
    Test getting all books
    
    YOUR TASK: Write this test!
    """
    # TODO: Test GET /books
    pass


def test_get_book(client: TestClient):
    """
    Test getting a specific book
    
    YOUR TASK: Write this test!
    
    TEST CASES:
    - Get existing book
    - Get non-existent book (should return 404)
    """
    # TODO: Test GET /books/{id}
    pass


# ============================================================================
# EXERCISE 10: Advanced Features
# ============================================================================

"""
TASK:
Implement these advanced database features:

1. SOFT DELETE
   - Add 'deleted_at' field
   - Modify delete endpoint to set deleted_at instead of actual deletion
   - Filter out deleted books in list endpoints

2. FULL-TEXT SEARCH (PostgreSQL only)
   - Add GIN index for text search
   - Create search endpoint using text search

3. RELATIONSHIPS
   - Create Author table
   - Create relationship between Book and Author
   - Update queries to use joins

4. CACHING
   - Add Redis for caching frequently accessed books
   - Implement cache-aside pattern

5. ASYNC OPERATIONS
   - Convert to async FastAPI endpoints
   - Use async database drivers

BONUS CHALLENGES:
- Implement pagination with cursor-based navigation
- Add database connection pooling
- Implement read replicas
- Add database backup scripts
"""

# ============================================================================
# SOLUTIONS CHECKLIST
# ============================================================================

"""
Once you complete the exercises, you should be able to:

□ Explain the difference between in-memory, SQLite, and PostgreSQL
□ Create and use database session dependencies
□ Perform CRUD operations with SQLModel
□ Distinguish between database models and API schemas
□ Create and apply Alembic migrations
□ Write complex database queries with filters
□ Migrate data between databases
□ Test database endpoints
□ Set up PostgreSQL locally
□ Use environment variables for database configuration

If you can check all these boxes, you've mastered database integration!
"""

# ============================================================================
# ADDITIONAL PRACTICE IDEAS
# ============================================================================

"""
Build these complete APIs with database integration:

1. TODO LIST API
   - Tasks with categories and priorities
   - User authentication
   - Due dates and reminders

2. BLOG API
   - Posts, comments, and tags
   - Author relationships
   - Full-text search

3. E-COMMERCE API
   - Products, categories, and inventory
   - Shopping cart and orders
   - Payment tracking

4. SOCIAL MEDIA API
   - Users, posts, and follows
   - Likes and comments
   - Feed generation

5. PROJECT MANAGEMENT API
   - Projects, tasks, and subtasks
   - Team members and assignments
   - Time tracking
"""

print("🎯 Ready to practice? Start with Exercise 1!")
print("📖 Refer to 04_DATABASE_INTEGRATION_TUTORIAL.md for detailed guidance")
print("🚀 Good luck!")
