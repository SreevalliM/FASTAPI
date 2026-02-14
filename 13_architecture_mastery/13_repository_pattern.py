"""
Repository Pattern with FastAPI

Demonstrates the repository pattern with multiple backends:
- In-Memory Repository
- SQLite Repository (file-based)
- PostgreSQL Repository (connection string-based)
- Cached Repository (decorator pattern)

The repository pattern abstracts data access, making it easy to:
- Switch between different storage backends
- Test without database dependencies
- Add caching transparently
- Maintain clean separation of concerns

Run: uvicorn 13_repository_pattern:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Protocol
from abc import ABC, abstractmethod
from datetime import datetime
import json
import sqlite3
import asyncio
from contextlib import asynccontextmanager


# ====================================
# DOMAIN MODEL
# ====================================

class User:
    """Domain entity representing a user"""
    
    def __init__(
        self,
        id: int,
        email: str,
        username: str,
        full_name: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.email = email
        self.username = username
        self.full_name = full_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data["id"],
            email=data["email"],
            username=data["username"],
            full_name=data["full_name"],
            is_active=data.get("is_active", True),
            created_at=created_at
        )


# ====================================
# REPOSITORY INTERFACE (Port)
# ====================================

class UserRepository(ABC):
    """Abstract repository interface"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve user by username"""
        pass
    
    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[User]:
        """Retrieve all users with pagination"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete a user"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total users"""
        pass


# ====================================
# IN-MEMORY REPOSITORY (Adapter)
# ====================================

class InMemoryUserRepository(UserRepository):
    """In-memory implementation - great for testing"""
    
    def __init__(self):
        self._storage: Dict[int, User] = {}
        self._next_id = 1
    
    async def create(self, user: User) -> User:
        if user.id is None or user.id == 0:
            user.id = self._next_id
            self._next_id += 1
        
        # Check for duplicates
        if any(u.email == user.email for u in self._storage.values()):
            raise ValueError("Email already exists")
        if any(u.username == user.username for u in self._storage.values()):
            raise ValueError("Username already exists")
        
        self._storage[user.id] = user
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self._storage.get(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        for user in self._storage.values():
            if user.email == email:
                return user
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        for user in self._storage.values():
            if user.username == username:
                return user
        return None
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[User]:
        users = list(self._storage.values())
        
        if active_only:
            users = [u for u in users if u.is_active]
        
        return users[skip:skip + limit]
    
    async def update(self, user: User) -> User:
        if user.id not in self._storage:
            raise ValueError("User not found")
        
        self._storage[user.id] = user
        return user
    
    async def delete(self, user_id: int) -> bool:
        if user_id in self._storage:
            del self._storage[user_id]
            return True
        return False
    
    async def count(self) -> int:
        return len(self._storage)


# ====================================
# SQLITE REPOSITORY (Adapter)
# ====================================

class SQLiteUserRepository(UserRepository):
    """SQLite implementation - persistent file-based storage"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    async def create(self, user: User) -> User:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (email, username, full_name, is_active, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user.email,
                user.username,
                user.full_name,
                user.is_active,
                user.created_at.isoformat()
            ))
            conn.commit()
            user.id = cursor.lastrowid
            return user
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Constraint violation: {e}")
        finally:
            conn.close()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User.from_dict(dict(row))
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User.from_dict(dict(row))
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User.from_dict(dict(row))
        return None
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM users"
        if active_only:
            query += " WHERE is_active = 1"
        query += " LIMIT ? OFFSET ?"
        
        cursor.execute(query, (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        return [User.from_dict(dict(row)) for row in rows]
    
    async def update(self, user: User) -> User:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET email = ?, username = ?, full_name = ?, is_active = ?
            WHERE id = ?
        """, (
            user.email,
            user.username,
            user.full_name,
            user.is_active,
            user.id
        ))
        
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError("User not found")
        
        conn.commit()
        conn.close()
        return user
    
    async def delete(self, user_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return deleted
    
    async def count(self) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count


# ====================================
# CACHED REPOSITORY (Decorator Pattern)
# ====================================

class CachedUserRepository(UserRepository):
    """
    Caching decorator for any repository implementation.
    Demonstrates the Decorator pattern for transparent caching.
    """
    
    def __init__(self, repository: UserRepository, ttl: int = 300):
        self.repository = repository
        self.ttl = ttl  # Time to live in seconds
        self._cache: Dict[str, tuple[any, datetime]] = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self._cache:
            return False
        
        value, timestamp = self._cache[key]
        age = (datetime.utcnow() - timestamp).total_seconds()
        return age < self.ttl
    
    def _get_from_cache(self, key: str) -> Optional[any]:
        """Get value from cache if valid"""
        if self._is_cache_valid(key):
            return self._cache[key][0]
        return None
    
    def _set_cache(self, key: str, value: any):
        """Set cache value with timestamp"""
        self._cache[key] = (value, datetime.utcnow())
    
    def _invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache entries matching pattern"""
        if pattern is None:
            self._cache.clear()
        else:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
    
    async def create(self, user: User) -> User:
        result = await self.repository.create(user)
        self._invalidate_cache()  # Invalidate all caches
        return result
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        cache_key = f"user:id:{user_id}"
        cached = self._get_from_cache(cache_key)
        
        if cached is not None:
            return cached
        
        user = await self.repository.get_by_id(user_id)
        if user:
            self._set_cache(cache_key, user)
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        cache_key = f"user:email:{email}"
        cached = self._get_from_cache(cache_key)
        
        if cached is not None:
            return cached
        
        user = await self.repository.get_by_email(email)
        if user:
            self._set_cache(cache_key, user)
        return user
    
    async def get_by_username(self, username: str) -> Optional[User]:
        cache_key = f"user:username:{username}"
        cached = self._get_from_cache(cache_key)
        
        if cached is not None:
            return cached
        
        user = await self.repository.get_by_username(username)
        if user:
            self._set_cache(cache_key, user)
        return user
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[User]:
        cache_key = f"users:skip:{skip}:limit:{limit}:active:{active_only}"
        cached = self._get_from_cache(cache_key)
        
        if cached is not None:
            return cached
        
        users = await self.repository.get_all(skip, limit, active_only)
        self._set_cache(cache_key, users)
        return users
    
    async def update(self, user: User) -> User:
        result = await self.repository.update(user)
        self._invalidate_cache(f"user:id:{user.id}")
        self._invalidate_cache("users:")  # Invalidate list caches
        return result
    
    async def delete(self, user_id: int) -> bool:
        result = await self.repository.delete(user_id)
        if result:
            self._invalidate_cache(f"user:id:{user_id}")
            self._invalidate_cache("users:")
        return result
    
    async def count(self) -> int:
        cache_key = "users:count"
        cached = self._get_from_cache(cache_key)
        
        if cached is not None:
            return cached
        
        count = await self.repository.count()
        self._set_cache(cache_key, count)
        return count


# ====================================
# DTOs (Data Transfer Objects)
# ====================================

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    created_at: str


# ====================================
# FASTAPI APPLICATION
# ====================================

app = FastAPI(
    title="Repository Pattern Example",
    description="Demonstrates repository pattern with multiple backends",
    version="1.0.0"
)

# Repository selection
# Change this to switch between implementations!
REPOSITORY_TYPE = "cached_memory"  # Options: memory, sqlite, cached_memory, cached_sqlite

def get_base_repository() -> UserRepository:
    """Factory function to create repository based on configuration"""
    if REPOSITORY_TYPE == "memory":
        return InMemoryUserRepository()
    elif REPOSITORY_TYPE == "sqlite":
        return SQLiteUserRepository("users.db")
    elif REPOSITORY_TYPE == "cached_memory":
        return CachedUserRepository(InMemoryUserRepository(), ttl=60)
    elif REPOSITORY_TYPE == "cached_sqlite":
        return CachedUserRepository(SQLiteUserRepository("users.db"), ttl=60)
    else:
        return InMemoryUserRepository()

# Singleton instance (in production, use proper DI container)
_repository_instance = None

def get_repository() -> UserRepository:
    """Dependency injection for repository"""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = get_base_repository()
    return _repository_instance


# API Routes
@app.get("/")
async def root():
    """API information"""
    return {
        "message": "Repository Pattern API",
        "repository_type": REPOSITORY_TYPE,
        "features": [
            "Multiple backend implementations",
            "Transparent caching",
            "Easy to test",
            "Clean separation of concerns"
        ],
        "endpoints": {
            "users": "/users",
            "stats": "/stats",
            "docs": "/docs"
        }
    }


@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    request: CreateUserRequest,
    repository: UserRepository = Depends(get_repository)
):
    """Create a new user"""
    user = User(
        id=0,  # Will be assigned by repository
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        is_active=request.is_active
    )
    
    try:
        created_user = await repository.create(user)
        return UserResponse(**created_user.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    repository: UserRepository = Depends(get_repository)
):
    """List users with pagination"""
    users = await repository.get_all(skip, limit, active_only)
    return [UserResponse(**u.to_dict()) for u in users]


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    repository: UserRepository = Depends(get_repository)
):
    """Get user by ID"""
    user = await repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user.to_dict())


@app.get("/users/by-email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: EmailStr,
    repository: UserRepository = Depends(get_repository)
):
    """Get user by email"""
    user = await repository.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user.to_dict())


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    repository: UserRepository = Depends(get_repository)
):
    """Update user"""
    user = await repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if request.email is not None:
        user.email = request.email
    if request.username is not None:
        user.username = request.username
    if request.full_name is not None:
        user.full_name = request.full_name
    if request.is_active is not None:
        user.is_active = request.is_active
    
    try:
        updated_user = await repository.update(user)
        return UserResponse(**updated_user.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    repository: UserRepository = Depends(get_repository)
):
    """Delete user"""
    deleted = await repository.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/stats")
async def get_stats(repository: UserRepository = Depends(get_repository)):
    """Get repository statistics"""
    total_users = await repository.count()
    all_users = await repository.get_all()
    active_users = sum(1 for u in all_users if u.is_active)
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "repository_type": REPOSITORY_TYPE
    }


if __name__ == "__main__":
    import uvicorn
    print(f"Starting server with {REPOSITORY_TYPE} repository...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
