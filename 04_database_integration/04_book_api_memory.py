"""
In-Memory Book API (Starting Point)
This is our baseline implementation before adding database integration.
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Book API - In Memory")

# Pydantic Models (Request/Response Schemas)
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1000, le=2100)
    isbn: Optional[str] = Field(None, pattern=r'^\d{13}$')
    description: Optional[str] = None

class BookCreate(BookBase):
    """Schema for creating a book"""
    pass

class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    isbn: Optional[str] = Field(None, pattern=r'^\d{13}$')
    description: Optional[str] = None

class Book(BookBase):
    """Schema for book response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# In-memory storage
books_db: List[dict] = []
next_id = 1

@app.get("/")
def root():
    return {
        "message": "Book API - In Memory Version",
        "endpoints": ["/books", "/books/{id}"]
    }

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    """Create a new book"""
    global next_id
    
    # Check for duplicate ISBN
    if book.isbn:
        for existing_book in books_db:
            if existing_book.get("isbn") == book.isbn:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Book with ISBN {book.isbn} already exists"
                )
    
    now = datetime.now()
    new_book = {
        "id": next_id,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "description": book.description,
        "created_at": now,
        "updated_at": now
    }
    books_db.append(new_book)
    next_id += 1
    
    return new_book

@app.get("/books", response_model=List[Book])
def get_books(
    skip: int = 0,
    limit: int = 100,
    author: Optional[str] = None,
    year: Optional[int] = None
):
    """Get all books with optional filtering"""
    filtered_books = books_db
    
    # Apply filters
    if author:
        filtered_books = [b for b in filtered_books if author.lower() in b["author"].lower()]
    if year:
        filtered_books = [b for b in filtered_books if b["year"] == year]
    
    # Apply pagination
    return filtered_books[skip : skip + limit]

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    """Get a specific book by ID"""
    for book in books_db:
        if book["id"] == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with id {book_id} not found"
    )

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate):
    """Update a book"""
    for book in books_db:
        if book["id"] == book_id:
            # Update only provided fields
            if book_update.title is not None:
                book["title"] = book_update.title
            if book_update.author is not None:
                book["author"] = book_update.author
            if book_update.year is not None:
                book["year"] = book_update.year
            if book_update.isbn is not None:
                book["isbn"] = book_update.isbn
            if book_update.description is not None:
                book["description"] = book_update.description
            
            book["updated_at"] = datetime.now()
            return book
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with id {book_id} not found"
    )

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    """Delete a book"""
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            books_db.pop(index)
            return
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with id {book_id} not found"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
