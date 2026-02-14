"""
Book API with SQLite using SQLModel
Demonstrates: Database session dependency, CRUD operations, Model vs Schema separation
"""
from fastapi import FastAPI, HTTPException, status, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional, List
from datetime import datetime

# ============================================================================
# DATABASE MODELS (Table definitions)
# ============================================================================
class Book(SQLModel, table=True):
    """
    Database Model - Represents the actual database table
    This class defines what gets stored in the database
    """
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    author: str = Field(index=True, max_length=100)
    year: int
    isbn: Optional[str] = Field(default=None, unique=True, max_length=13)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# PYDANTIC SCHEMAS (Request/Response models)
# ============================================================================
class BookCreate(SQLModel):
    """Schema for creating a book - only fields the user provides"""
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1000, le=2100)
    isbn: Optional[str] = Field(default=None, pattern=r'^\d{13}$')
    description: Optional[str] = None


class BookUpdate(SQLModel):
    """Schema for updating a book - all fields are optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    isbn: Optional[str] = Field(None, pattern=r'^\d{13}$')
    description: Optional[str] = None


class BookRead(SQLModel):
    """Schema for reading a book - what gets returned in responses"""
    id: int
    title: str
    author: str
    year: int
    isbn: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


# ============================================================================
# DATABASE SETUP
# ============================================================================
# SQLite database URL
sqlite_file_name = "books.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Create engine with connection arguments for SQLite
connect_args = {"check_same_thread": False}  # Needed for SQLite
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


# ============================================================================
# DEPENDENCY: Database Session
# ============================================================================
def get_session():
    """
    Dependency that provides a database session.
    The session is automatically closed after the request.
    """
    with Session(engine) as session:
        yield session


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================
app = FastAPI(title="Book API - SQLite with SQLModel")

@app.on_event("startup")
def on_startup():
    """Create tables on application startup"""
    create_db_and_tables()


@app.get("/")
def root():
    return {
        "message": "Book API - SQLite Version",
        "database": "SQLite",
        "orm": "SQLModel",
        "endpoints": ["/books", "/books/{id}"]
    }


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """
    Create a new book
    
    The session dependency is injected automatically by FastAPI
    """
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
    
    # Create new book from schema
    db_book = Book.model_validate(book)
    
    # Add to session and commit
    session.add(db_book)
    session.commit()
    session.refresh(db_book)  # Refresh to get the generated ID
    
    return db_book


@app.get("/books", response_model=List[BookRead])
def get_books(
    skip: int = 0,
    limit: int = 100,
    author: Optional[str] = None,
    year: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """
    Get all books with optional filtering and pagination
    """
    # Start with base query
    query = select(Book)
    
    # Apply filters
    if author:
        query = query.where(Book.author.contains(author))
    if year:
        query = query.where(Book.year == year)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
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
    """Update a book - only provided fields are updated"""
    # Get existing book
    db_book = session.get(Book, book_id)
    
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    # Update only provided fields
    book_data = book_update.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    
    # Update timestamp
    db_book.updated_at = datetime.now()
    
    # Commit changes
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


# ============================================================================
# STATISTICS ENDPOINT (Bonus - demonstrates aggregations)
# ============================================================================
@app.get("/books/stats/summary")
def get_statistics(session: Session = Depends(get_session)):
    """Get database statistics"""
    books = session.exec(select(Book)).all()
    
    if not books:
        return {"total_books": 0, "authors": 0, "years": []}
    
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
