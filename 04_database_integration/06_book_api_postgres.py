"""
Book API with PostgreSQL/SQLite support using SQLModel
Demonstrates: Environment-based database configuration, production-ready setup
"""
from fastapi import FastAPI, HTTPException, status, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager
import os

# ============================================================================
# DATABASE MODELS (Table definitions)
# ============================================================================
class Book(SQLModel, table=True):
    """
    Database Model - works with both SQLite and PostgreSQL
    """
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    author: str = Field(index=True, max_length=100)
    year: int
    isbn: Optional[str] = Field(default=None, unique=True, max_length=13, index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================
class BookCreate(SQLModel):
    """Schema for creating a book"""
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1000, le=2100)
    isbn: Optional[str] = Field(default=None, pattern=r'^\d{13}$')
    description: Optional[str] = None


class BookUpdate(SQLModel):
    """Schema for updating a book"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    isbn: Optional[str] = Field(None, pattern=r'^\d{13}$')
    description: Optional[str] = None


class BookRead(SQLModel):
    """Schema for reading a book"""
    id: int
    title: str
    author: str
    year: int
    isbn: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
class DatabaseConfig:
    """Database configuration based on environment variables"""
    
    @staticmethod
    def get_database_url() -> str:
        """
        Get database URL from environment variables.
        Falls back to SQLite if not specified.
        
        For PostgreSQL, set DATABASE_URL environment variable:
        export DATABASE_URL="postgresql://user:password@localhost/dbname"
        
        Or use individual components:
        export DB_USER="myuser"
        export DB_PASSWORD="mypassword"
        export DB_HOST="localhost"
        export DB_PORT="5432"
        export DB_NAME="bookstore"
        """
        # Check for full DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            return database_url
        
        # Check for PostgreSQL components
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        
        if db_user and db_password and db_name:
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Default to SQLite
        return "sqlite:///./books.db"
    
    @staticmethod
    def get_connect_args(database_url: str) -> dict:
        """Get connection arguments based on database type"""
        if database_url.startswith("sqlite"):
            return {"check_same_thread": False}
        return {}


# Initialize database
database_url = DatabaseConfig.get_database_url()
connect_args = DatabaseConfig.get_connect_args(database_url)

# Create engine
engine = create_engine(
    database_url,
    echo=True,  # Set to False in production
    connect_args=connect_args
)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


# ============================================================================
# DEPENDENCY: Database Session
# ============================================================================
def get_session():
    """Database session dependency"""
    with Session(engine) as session:
        yield session


# ============================================================================
# LIFESPAN CONTEXT MANAGER (Modern FastAPI approach)
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    This is the modern way to handle startup/shutdown in FastAPI.
    """
    # Startup
    print(f"🚀 Starting application with database: {database_url}")
    create_db_and_tables()
    print("✅ Database tables created")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================
app = FastAPI(
    title="Book API - Multi-Database Support",
    description="Book API supporting both SQLite and PostgreSQL",
    version="2.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    """Root endpoint with API information"""
    db_type = "PostgreSQL" if "postgresql" in database_url else "SQLite"
    return {
        "message": "Book API - Multi-Database Version",
        "database": db_type,
        "orm": "SQLModel",
        "endpoints": {
            "books": "/books",
            "book_detail": "/books/{id}",
            "statistics": "/books/stats/summary",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check(session: Session = Depends(get_session)):
    """Health check endpoint - verifies database connectivity"""
    try:
        # Try to execute a simple query
        session.exec(select(Book).limit(1)).first()
        db_type = "PostgreSQL" if "postgresql" in database_url else "SQLite"
        return {
            "status": "healthy",
            "database": db_type,
            "connected": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """Create a new book"""
    # Check for duplicate ISBN
    if book.isbn:
        existing_book = session.exec(
            select(Book).where(Book.isbn == book.isbn)
        ).first()
        
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN {book.isbn} already exists"
            )
    
    # Create new book
    db_book = Book.model_validate(book)
    
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    
    return db_book


@app.get("/books", response_model=List[BookRead])
def get_books(
    skip: int = 0,
    limit: int = 100,
    author: Optional[str] = None,
    year: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Get all books with filtering and pagination"""
    query = select(Book)
    
    if author:
        query = query.where(Book.author.contains(author))
    if year:
        query = query.where(Book.year == year)
    
    query = query.offset(skip).limit(limit)
    books = session.exec(query).all()
    
    return books


@app.get("/books/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: Session = Depends(get_session)):
    """Get a specific book by ID"""
    book = session.get(Book, book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    return book


@app.put("/books/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    session: Session = Depends(get_session)
):
    """Update a book"""
    db_book = session.get(Book, book_id)
    
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    # Update fields
    book_data = book_update.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    
    db_book.updated_at = datetime.now()
    
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    
    return db_book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    """Delete a book"""
    book = session.get(Book, book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    session.delete(book)
    session.commit()
    
    return None


@app.get("/books/stats/summary")
def get_statistics(session: Session = Depends(get_session)):
    """Get database statistics"""
    books = session.exec(select(Book)).all()
    
    if not books:
        return {
            "total_books": 0,
            "unique_authors": 0,
            "year_range": None,
            "years_covered": []
        }
    
    authors = set(book.author for book in books)
    years = sorted(set(book.year for book in books))
    
    return {
        "total_books": len(books),
        "unique_authors": len(authors),
        "year_range": {
            "earliest": min(years),
            "latest": max(years)
        },
        "years_covered": years
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
