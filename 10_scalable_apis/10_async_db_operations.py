"""
10. Scalable APIs - Async Database Operations
=============================================

This module demonstrates async database operations with different drivers.

Topics covered:
- SQLite with aiosqlite
- PostgreSQL simulation with asyncpg patterns
- Connection pooling
- Best practices for async DB operations

Installation:
    pip install aiosqlite databases sqlalchemy[asyncio]
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import aiosqlite
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

# ============================================================================
# Database Configuration
# ============================================================================

DATABASE_URL = "test_scalable_api.db"


# ============================================================================
# Pydantic Models
# ============================================================================

class UserCreate(BaseModel):
    name: str
    email: str
    age: int


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    created_at: str


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int


# ============================================================================
# Database Connection Pool
# ============================================================================

class DatabasePool:
    """
    Simple connection pool for SQLite (for demonstration).
    
    In production with PostgreSQL, use asyncpg.create_pool() or
    SQLAlchemy's async engine with pooling.
    """
    
    def __init__(self, database_url: str, pool_size: int = 5):
        self.database_url = database_url
        self.pool_size = pool_size
        self.pool: List[aiosqlite.Connection] = []
        self.semaphore = asyncio.Semaphore(pool_size)
    
    async def initialize(self):
        """Initialize connection pool"""
        for _ in range(self.pool_size):
            conn = await aiosqlite.connect(self.database_url)
            conn.row_factory = aiosqlite.Row
            self.pool.append(conn)
        print(f"✅ Database pool initialized with {self.pool_size} connections")
    
    async def close(self):
        """Close all connections"""
        for conn in self.pool:
            await conn.close()
        print("✅ Database pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool"""
        async with self.semaphore:
            conn = self.pool[0]  # Simplified: would rotate in real impl
            yield conn


# Global database pool
db_pool: Optional[DatabasePool] = None


# ============================================================================
# Lifespan Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup/shutdown)"""
    global db_pool
    
    # Startup
    print("\n" + "="*70)
    print("🚀 Starting Async DB Operations API")
    print("="*70)
    
    # Initialize database pool
    db_pool = DatabasePool(DATABASE_URL, pool_size=5)
    await db_pool.initialize()
    
    # Create tables
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        await conn.commit()
    
    print("✅ Database tables created")
    print("="*70 + "\n")
    
    yield
    
    # Shutdown
    await db_pool.close()
    print("\n👋 API shutdown complete\n")


app = FastAPI(
    title="Async DB Operations API",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# SECTION 1: Basic CRUD Operations (Async)
# ============================================================================

@app.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """
    Create a new user (async database operation).
    
    This uses async database driver (aiosqlite) for non-blocking I/O.
    """
    async with db_pool.acquire() as conn:
        try:
            cursor = await conn.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (user.name, user.email, user.age)
            )
            await conn.commit()
            
            # Fetch the created user
            row = await conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (cursor.lastrowid,)
            )
            user_row = await row.fetchone()
            
            return {
                "id": user_row['id'],
                "name": user_row['name'],
                "email": user_row['email'],
                "age": user_row['age'],
                "created_at": user_row['created_at']
            }
        except aiosqlite.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already exists")


@app.get("/users/", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 10):
    """
    List all users with pagination (async).
    
    This demonstrates async query execution.
    """
    async with db_pool.acquire() as conn:
        cursor = await conn.execute(
            "SELECT * FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, skip)
        )
        rows = await cursor.fetchall()
        
        return [
            {
                "id": row['id'],
                "name": row['name'],
                "email": row['email'],
                "age": row['age'],
                "created_at": row['created_at']
            }
            for row in rows
        ]


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get a single user by ID (async)"""
    async with db_pool.acquire() as conn:
        cursor = await conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": row['id'],
            "name": row['name'],
            "email": row['email'],
            "age": row['age'],
            "created_at": row['created_at']
        }


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate):
    """Update a user (async)"""
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?",
            (user.name, user.email, user.age, user_id)
        )
        await conn.commit()
        
        # Check if user exists
        cursor = await conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": row['id'],
            "name": row['name'],
            "email": row['email'],
            "age": row['age'],
            "created_at": row['created_at']
        }


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete a user (async)"""
    async with db_pool.acquire() as conn:
        cursor = await conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}


# ============================================================================
# SECTION 2: Concurrent Database Operations
# ============================================================================

@app.post("/products/", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product"""
    async with db_pool.acquire() as conn:
        cursor = await conn.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (product.name, product.price, product.stock)
        )
        await conn.commit()
        
        row = await conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (cursor.lastrowid,)
        )
        product_row = await row.fetchone()
        
        return {
            "id": product_row['id'],
            "name": product_row['name'],
            "price": product_row['price'],
            "stock": product_row['stock']
        }


@app.get("/products/", response_model=List[ProductResponse])
async def list_products():
    """List all products"""
    async with db_pool.acquire() as conn:
        cursor = await conn.execute("SELECT * FROM products")
        rows = await cursor.fetchall()
        
        return [
            {
                "id": row['id'],
                "name": row['name'],
                "price": row['price'],
                "stock": row['stock']
            }
            for row in rows
        ]


@app.get("/dashboard/{user_id}")
async def get_user_dashboard(user_id: int):
    """
    Get user dashboard with concurrent queries.
    
    This demonstrates asyncio.gather() for running multiple
    database queries concurrently.
    """
    async def get_user_info():
        async with db_pool.acquire() as conn:
            cursor = await conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return await cursor.fetchone()
    
    async def get_user_orders():
        async with db_pool.acquire() as conn:
            cursor = await conn.execute(
                """
                SELECT o.*, p.name as product_name 
                FROM orders o 
                JOIN products p ON o.product_id = p.id 
                WHERE o.user_id = ?
                ORDER BY o.created_at DESC
                """,
                (user_id,)
            )
            return await cursor.fetchall()
    
    async def get_total_spent():
        async with db_pool.acquire() as conn:
            cursor = await conn.execute(
                "SELECT SUM(total_price) as total FROM orders WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            return result['total'] or 0
    
    # Run all queries concurrently!
    import time
    start = time.time()
    
    user, orders, total_spent = await asyncio.gather(
        get_user_info(),
        get_user_orders(),
        get_total_spent()
    )
    
    duration = time.time() - start
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email']
        },
        "orders": [dict(order) for order in orders],
        "total_spent": total_spent,
        "query_time": round(duration, 4),
        "note": "All queries ran concurrently!"
    }


# ============================================================================
# SECTION 3: Transactions
# ============================================================================

@app.post("/orders/")
async def create_order(user_id: int, product_id: int, quantity: int):
    """
    Create an order with transaction support.
    
    This demonstrates database transactions in async context.
    If any operation fails, everything is rolled back.
    """
    async with db_pool.acquire() as conn:
        try:
            # Start transaction
            await conn.execute("BEGIN")
            
            # Check product stock
            cursor = await conn.execute(
                "SELECT stock, price FROM products WHERE id = ?",
                (product_id,)
            )
            product = await cursor.fetchone()
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            if product['stock'] < quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            
            # Update stock
            await conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (quantity, product_id)
            )
            
            # Create order
            total_price = product['price'] * quantity
            cursor = await conn.execute(
                """
                INSERT INTO orders (user_id, product_id, quantity, total_price)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, product_id, quantity, total_price)
            )
            
            # Commit transaction
            await conn.commit()
            
            return {
                "order_id": cursor.lastrowid,
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity,
                "total_price": total_price,
                "message": "Order created successfully"
            }
            
        except Exception as e:
            # Rollback on error
            await conn.rollback()
            raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# SECTION 4: Comparison of Blocking vs Non-Blocking
# ============================================================================

@app.get("/performance/blocking-queries")
async def blocking_queries_demo():
    """
    ❌ ANTI-PATTERN: Sequential async queries
    
    Even though these are async, running them sequentially
    defeats the purpose of async!
    """
    import time
    start = time.time()
    
    async with db_pool.acquire() as conn:
        # These run ONE AFTER ANOTHER (slow!)
        users_cursor = await conn.execute("SELECT COUNT(*) FROM users")
        users_count = await users_cursor.fetchone()
        
        products_cursor = await conn.execute("SELECT COUNT(*) FROM products")
        products_count = await products_cursor.fetchone()
        
        orders_cursor = await conn.execute("SELECT COUNT(*) FROM orders")
        orders_count = await orders_cursor.fetchone()
    
    duration = time.time() - start
    
    return {
        "users": users_count[0],
        "products": products_count[0],
        "orders": orders_count[0],
        "query_time": round(duration, 4),
        "note": "Sequential execution - slower than it could be"
    }


@app.get("/performance/concurrent-queries")
async def concurrent_queries_demo():
    """
    ✅ BEST PRACTICE: Concurrent async queries
    
    Running queries concurrently is much faster!
    """
    import time
    start = time.time()
    
    async def count_users():
        async with db_pool.acquire() as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM users")
            result = await cursor.fetchone()
            return result[0]
    
    async def count_products():
        async with db_pool.acquire() as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM products")
            result = await cursor.fetchone()
            return result[0]
    
    async def count_orders():
        async with db_pool.acquire() as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM orders")
            result = await cursor.fetchone()
            return result[0]
    
    # Run all queries concurrently
    users, products, orders = await asyncio.gather(
        count_users(),
        count_products(),
        count_orders()
    )
    
    duration = time.time() - start
    
    return {
        "users": users,
        "products": products,
        "orders": orders,
        "query_time": round(duration, 4),
        "note": "Concurrent execution - much faster!"
    }


# ============================================================================
# SECTION 5: Best Practices
# ============================================================================

@app.get("/best-practices")
async def db_best_practices():
    """Database operation best practices"""
    return {
        "connection_pooling": {
            "description": "Always use connection pooling in production",
            "libraries": {
                "PostgreSQL": "asyncpg.create_pool()",
                "MySQL": "aiomysql.create_pool()",
                "MongoDB": "motor with connection pooling",
                "Redis": "aioredis with connection pooling"
            },
            "benefits": [
                "Reuse connections (faster)",
                "Limit concurrent connections",
                "Better resource management"
            ]
        },
        "concurrent_queries": {
            "description": "Use asyncio.gather() for independent queries",
            "example": "user, orders, profile = await asyncio.gather(...)",
            "speedup": "Can be 3-5x faster for multiple queries"
        },
        "transactions": {
            "description": "Use transactions for data integrity",
            "pattern": "BEGIN -> operations -> COMMIT (or ROLLBACK on error)",
            "critical_for": ["Order processing", "Payment operations", "Multi-table updates"]
        },
        "query_optimization": {
            "tips": [
                "Use indexes on frequently queried columns",
                "Avoid N+1 queries (use JOINs)",
                "Use LIMIT for pagination",
                "Select only needed columns",
                "Use prepared statements (prevents SQL injection)"
            ]
        },
        "error_handling": {
            "tips": [
                "Always handle database exceptions",
                "Rollback transactions on errors",
                "Log database errors for debugging",
                "Return meaningful error messages to users"
            ]
        }
    }


# ============================================================================
# Utility Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "title": "Async DB Operations API",
        "description": "Learn async database operations with FastAPI",
        "endpoints": {
            "create_user": "POST /users/",
            "list_users": "GET /users/",
            "get_user": "GET /users/{user_id}",
            "user_dashboard": "GET /dashboard/{user_id}",
            "create_product": "POST /products/",
            "create_order": "POST /orders/",
            "performance_comparison": "GET /performance/concurrent-queries",
            "best_practices": "GET /best-practices"
        },
        "database": {
            "type": "SQLite (async)",
            "driver": "aiosqlite",
            "connection_pool": "Custom pool with semaphore",
            "note": "In production, use PostgreSQL with asyncpg"
        },
        "docs": "/docs"
    }


@app.post("/seed-data")
async def seed_sample_data():
    """Seed database with sample data for testing"""
    async with db_pool.acquire() as conn:
        # Add sample users
        await conn.execute(
            "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
            (1, "Alice Johnson", "alice@example.com", 28)
        )
        await conn.execute(
            "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
            (2, "Bob Smith", "bob@example.com", 35)
        )
        
        # Add sample products
        await conn.execute(
            "INSERT OR IGNORE INTO products (id, name, price, stock) VALUES (?, ?, ?, ?)",
            (1, "Laptop", 999.99, 10)
        )
        await conn.execute(
            "INSERT OR IGNORE INTO products (id, name, price, stock) VALUES (?, ?, ?, ?)",
            (2, "Mouse", 29.99, 50)
        )
        
        await conn.commit()
    
    return {"message": "Sample data seeded successfully"}


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 Starting Async DB Operations API")
    print("="*70)
    print("\nFeatures:")
    print("  • Async database operations with aiosqlite")
    print("  • Connection pooling")
    print("  • Concurrent query execution")
    print("  • Transaction support")
    print("\nTry:")
    print("  • http://localhost:8001/docs")
    print("  • POST http://localhost:8001/seed-data (seed sample data)")
    print("  • GET http://localhost:8001/dashboard/1")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
