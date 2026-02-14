"""
🧪 FastAPI Application for Testing Examples
============================================
Sample API with various endpoints to demonstrate testing techniques:
- Simple endpoints
- Dependency injection
- Database operations
- Authentication

This API is used as the subject for testing examples in test_testing_basics.py

Run the API:
    uvicorn 11_api_for_testing:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime
import sqlite3

# ==================== FastAPI App ====================

app = FastAPI(
    title="Testing Example API",
    description="Sample API for demonstrating testing techniques",
    version="1.0.0"
)

security = HTTPBearer()

# ==================== In-Memory Databases ====================

# Simulated database
users_db: Dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
}

products_db: Dict[int, dict] = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
}

# ==================== Pydantic Models ====================

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str = "user"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "user"

class Product(BaseModel):
    id: int
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

class ProductCreate(BaseModel):
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(gt=0)

class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    created_at: datetime

# ==================== Dependencies ====================

def get_database():
    """
    Database dependency (simulated)
    This will be overridden in tests
    """
    return {"users": users_db, "products": products_db}

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: dict = Depends(get_database)
) -> User:
    """
    Verify token and return current user
    In tests, this can be overridden to bypass authentication
    """
    token = credentials.credentials
    
    # Simple token validation (user_id as token)
    try:
        user_id = int(token)
        user_data = db["users"].get(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return User(**user_data)
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require admin role
    Can be overridden in tests
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# ==================== API Endpoints ====================

@app.get("/")
def root():
    """Simple endpoint for basic testing"""
    return {"message": "Welcome to Testing Example API", "status": "ok"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# ==================== User Endpoints ====================

@app.get("/users", response_model=List[User])
def list_users(db: dict = Depends(get_database)):
    """Get all users"""
    return list(db["users"].values())

@app.get("/users/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: dict = Depends(get_database)):
    """Get user by ID"""
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return User(**user)

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: dict = Depends(get_database),
    admin: User = Depends(require_admin)  # Requires admin
):
    """Create new user (admin only)"""
    new_id = max(db["users"].keys()) + 1 if db["users"] else 1
    user_data = user.model_dump()
    user_data["id"] = new_id
    db["users"][new_id] = user_data
    return User(**user_data)

# ==================== Product Endpoints ====================

@app.get("/products", response_model=List[Product])
def list_products(db: dict = Depends(get_database)):
    """Get all products"""
    return list(db["products"].values())

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, db: dict = Depends(get_database)):
    """Get product by ID"""
    product = db["products"].get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    return Product(**product)

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: dict = Depends(get_database),
    admin: User = Depends(require_admin)  # Requires admin
):
    """Create new product (admin only)"""
    new_id = max(db["products"].keys()) + 1 if db["products"] else 1
    product_data = product.model_dump()
    product_data["id"] = new_id
    db["products"][new_id] = product_data
    return Product(**product_data)

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: dict = Depends(get_database),
    admin: User = Depends(require_admin)  # Requires admin
):
    """Delete product (admin only)"""
    if product_id not in db["products"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    del db["products"][product_id]
    return None

# ==================== Order Endpoints ====================

orders_db: List[dict] = []

@app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: dict = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Create new order"""
    # Verify user exists
    if order.user_id not in db["users"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {order.user_id} not found"
        )
    
    # Verify product exists
    product = db["products"].get(order.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {order.product_id} not found"
        )
    
    # Check stock
    if product["stock"] < order.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product['stock']}"
        )
    
    # Calculate total
    total_price = product["price"] * order.quantity
    
    # Update stock
    product["stock"] -= order.quantity
    
    # Create order
    order_id = len(orders_db) + 1
    order_data = {
        "id": order_id,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total_price": total_price,
        "created_at": datetime.utcnow()
    }
    orders_db.append(order_data)
    
    return Order(**order_data)

@app.get("/orders", response_model=List[Order])
def list_orders(current_user: User = Depends(get_current_user)):
    """Get all orders (authenticated users only)"""
    return orders_db

# ==================== External Service Simulation ====================

def get_external_api_client():
    """
    Simulates external API dependency
    Will be mocked in tests
    """
    class ExternalAPIClient:
        def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
            """Simulates calling external API"""
            # In real app, this would call external service
            rates = {
                ("USD", "EUR"): 0.85,
                ("USD", "GBP"): 0.73,
                ("EUR", "USD"): 1.18,
            }
            return rates.get((from_currency, to_currency), 1.0)
    
    return ExternalAPIClient()

@app.get("/convert/{amount}")
def convert_currency(
    amount: float,
    from_currency: str = "USD",
    to_currency: str = "EUR",
    api_client = Depends(get_external_api_client)
):
    """
    Convert currency using external API
    Perfect for demonstrating mocking
    """
    rate = api_client.get_exchange_rate(from_currency, to_currency)
    converted = amount * rate
    
    return {
        "amount": amount,
        "from": from_currency,
        "to": to_currency,
        "rate": rate,
        "converted": round(converted, 2)
    }

# ==================== Database Connection Simulation ====================

class DatabaseConnection:
    """Simulates a database connection that needs to be mocked"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str):
        """Execute SQL query"""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

def get_db_connection():
    """Dependency that returns DB connection - will be mocked in tests"""
    db = DatabaseConnection()
    try:
        yield db
    finally:
        db.disconnect()

@app.get("/stats/users")
def get_user_stats(db: DatabaseConnection = Depends(get_db_connection)):
    """
    Get user statistics
    Demonstrates testing with database mocking
    """
    # In real app, this would query actual database
    # In tests, we'll mock this dependency
    return {
        "total_users": len(users_db),
        "roles": {
            "admin": sum(1 for u in users_db.values() if u["role"] == "admin"),
            "user": sum(1 for u in users_db.values() if u["role"] == "user"),
        }
    }

# ==================== Run App ====================

if __name__ == "__main__":
    import uvicorn
    print("🧪 Starting Testing Example API...")
    print("📖 Docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
