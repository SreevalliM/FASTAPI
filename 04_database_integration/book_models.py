"""
Shared Book Models for Database
This file is imported by both the API and Alembic migrations.
"""
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime


class Book(SQLModel, table=True):
    """
    Book database model.
    This is imported by both the API files and Alembic env.py
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
