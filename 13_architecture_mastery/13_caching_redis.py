"""
Redis Caching Strategies with FastAPI

Demonstrates various caching patterns:
- Cache-Aside (Lazy Loading)
- Write-Through Cache
- Write-Behind (Write-Back) Cache
- Cache Invalidation Strategies
- Cache Warming
- Distributed Caching

Prerequisites:
    pip install fastapi uvicorn redis aioredis
    docker run -d -p 6379:6379 redis:alpine

Run: uvicorn 13_caching_redis:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
import json
import asyncio
import hashlib
import time
from functools import wraps
import redis.asyncio as aioredis


# ====================================
# REDIS CONNECTION
# ====================================

redis_client: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = await aioredis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
            await redis_client.ping()
            print("✓ Connected to Redis")
        except Exception as e:
            print(f"✗ Redis connection failed: {e}")
            print("  Starting without cache...")
            redis_client = None
    return redis_client


# ====================================
# DOMAIN MODELS
# ====================================

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    stock: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CacheStats(BaseModel):
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.0


# ====================================
# IN-MEMORY DATABASE (Simulated)
# ====================================

# Simulated database
FAKE_DB: Dict[int, Product] = {}
NEXT_ID = 1

# Cache statistics
cache_stats = CacheStats()


def simulate_slow_db_query(delay: float = 0.5):
    """Simulate slow database query"""
    time.sleep(delay)


async def db_get_product(product_id: int) -> Optional[Product]:
    """Simulate database read"""
    simulate_slow_db_query(0.3)  # Simulate latency
    return FAKE_DB.get(product_id)


async def db_get_all_products() -> List[Product]:
    """Simulate database query for all products"""
    simulate_slow_db_query(0.5)
    return list(FAKE_DB.values())


async def db_get_products_by_category(category: str) -> List[Product]:
    """Simulate database query by category"""
    simulate_slow_db_query(0.4)
    return [p for p in FAKE_DB.values() if p.category == category]


async def db_create_product(product: Product) -> Product:
    """Simulate database write"""
    global NEXT_ID
    product.id = NEXT_ID
    NEXT_ID += 1
    FAKE_DB[product.id] = product
    simulate_slow_db_query(0.2)
    return product


async def db_update_product(product_id: int, product: Product) -> Optional[Product]:
    """Simulate database update"""
    if product_id not in FAKE_DB:
        return None
    product.id = product_id
    FAKE_DB[product_id] = product
    simulate_slow_db_query(0.2)
    return product


async def db_delete_product(product_id: int) -> bool:
    """Simulate database delete"""
    if product_id in FAKE_DB:
        del FAKE_DB[product_id]
        simulate_slow_db_query(0.2)
        return True
    return False


# ====================================
# CACHING UTILITIES
# ====================================

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a unique cache key"""
    key_parts = [prefix] + [str(arg) for arg in args]
    if kwargs:
        key_parts.append(hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest())
    return ":".join(key_parts)


async def set_cache(
    redis: aioredis.Redis,
    key: str,
    value: Any,
    ttl: int = 300
):
    """Set cache value with TTL"""
    if redis:
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif isinstance(value, BaseModel):
                value = value.json()
            
            await redis.set(key, value, ex=ttl)
        except Exception as e:
            print(f"Cache set error: {e}")


async def get_cache(
    redis: aioredis.Redis,
    key: str,
    model_class: Optional[type] = None
) -> Optional[Any]:
    """Get cache value"""
    if not redis:
        return None
    
    try:
        value = await redis.get(key)
        if value is None:
            return None
        
        if model_class:
            if isinstance(value, str):
                return model_class(**json.loads(value))
        
        return value
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


async def delete_cache(redis: aioredis.Redis, pattern: str):
    """Delete cache keys matching pattern"""
    if redis:
        try:
            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await redis.delete(*keys)
        except Exception as e:
            print(f"Cache delete error: {e}")


# ====================================
# CACHING PATTERNS
# ====================================

class CacheAsidePattern:
    """
    Cache-Aside (Lazy Loading) Pattern
    1. Check cache first
    2. If miss, query database
    3. Store result in cache
    4. Return result
    """
    
    @staticmethod
    async def get_product(
        product_id: int,
        redis: aioredis.Redis
    ) -> Optional[Product]:
        """Get product with cache-aside pattern"""
        cache_key = f"product:{product_id}"
        
        # Try cache first
        cached = await get_cache(redis, cache_key, Product)
        if cached:
            cache_stats.hits += 1
            return cached
        
        # Cache miss - query database
        cache_stats.misses += 1
        product = await db_get_product(product_id)
        
        if product:
            # Store in cache for future requests
            await set_cache(redis, cache_key, product, ttl=300)
        
        return product


class WriteThroughPattern:
    """
    Write-Through Pattern
    1. Write to cache
    2. Write to database
    3. Return result
    
    Ensures cache is always in sync but slower writes
    """
    
    @staticmethod
    async def update_product(
        product_id: int,
        product: Product,
        redis: aioredis.Redis
    ) -> Optional[Product]:
        """Update product with write-through pattern"""
        # Update database
        updated = await db_update_product(product_id, product)
        
        if updated:
            # Update cache immediately
            cache_key = f"product:{product_id}"
            await set_cache(redis, cache_key, updated, ttl=300)
            
            # Invalidate related caches
            await delete_cache(redis, "products:*")
            await delete_cache(redis, f"category:{updated.category}:*")
        
        return updated


class WriteBehindPattern:
    """
    Write-Behind (Write-Back) Pattern
    1. Write to cache immediately
    2. Queue database write
    3. Async write to database
    
    Fast writes but risk of data loss
    """
    
    def __init__(self):
        self.write_queue: asyncio.Queue = asyncio.Queue()
    
    async def update_product(
        self,
        product_id: int,
        product: Product,
        redis: aioredis.Redis,
        background_tasks: BackgroundTasks
    ) -> Product:
        """Update product with write-behind pattern"""
        # Update cache immediately
        cache_key = f"product:{product_id}"
        product.id = product_id
        await set_cache(redis, cache_key, product, ttl=300)
        
        # Queue database write
        background_tasks.add_task(db_update_product, product_id, product)
        
        return product


# ====================================
# CACHING DECORATORS
# ====================================

def cache_result(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results
    Usage: @cache_result("products", ttl=60)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get Redis from DI (first argument is usually self or dependency)
            redis = kwargs.get('redis') or (args[0] if args else None)
            
            # Generate cache key
            cache_key = generate_cache_key(prefix, *args[1:], **{k: v for k, v in kwargs.items() if k != 'redis'})
            
            # Try cache
            if redis:
                cached = await get_cache(redis, cache_key)
                if cached:
                    cache_stats.hits += 1
                    try:
                        return [Product(**json.loads(item)) if isinstance(item, str) else Product(**item) 
                                for item in json.loads(cached)]
                    except:
                        return cached
            
            # Cache miss
            cache_stats.misses += 1
            result = await func(*args, **kwargs)
            
            # Store in cache
            if redis and result is not None:
                cache_value = json.dumps([p.dict() for p in result] if isinstance(result, list) else result)
                await set_cache(redis, cache_key, cache_value, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# ====================================
# FASTAPI APPLICATION
# ====================================

app = FastAPI(
    title="Redis Caching Patterns",
    description="Demonstrates various caching strategies with Redis",
    version="1.0.0"
)

# Initialize cache patterns
write_behind = WriteBehindPattern()


@app.on_event("startup")
async def startup():
    """Initialize Redis connection"""
    await get_redis()
    
    # Seed some data
    global NEXT_ID, FAKE_DB
    FAKE_DB = {
        1: Product(id=1, name="Laptop", description="High-performance laptop", 
                   price=999.99, category="Electronics", stock=50),
        2: Product(id=2, name="Mouse", description="Wireless mouse",
                   price=29.99, category="Electronics", stock=200),
        3: Product(id=3, name="Desk", description="Standing desk",
                   price=399.99, category="Furniture", stock=20)
    }
    NEXT_ID = 4


@app.on_event("shutdown")
async def shutdown():
    """Close Redis connection"""
    if redis_client:
        await redis_client.close()


@app.get("/")
async def root():
    """API information"""
    return {
        "message": "Redis Caching API",
        "patterns": {
            "cache_aside": "GET /products/{id} - Lazy loading",
            "write_through": "PUT /products/{id}/write-through - Immediate sync",
            "write_behind": "PUT /products/{id}/write-behind - Async write",
            "cached_query": "GET /products?category={cat} - Cached queries"
        },
        "redis_status": "connected" if redis_client else "disconnected",
        "endpoints": {
            "products": "/products",
            "cache_stats": "/cache/stats",
            "cache_clear": "/cache/clear"
        }
    }


# ====================================
# CACHE-ASIDE PATTERN ENDPOINTS
# ====================================

@app.get("/products/{product_id}")
async def get_product(
    product_id: int,
    redis: aioredis.Redis = Depends(get_redis)
):
    """
    Get product with Cache-Aside pattern
    - Check cache first
    - Query DB on miss
    - Store result in cache
    """
    start_time = time.time()
    product = await CacheAsidePattern.get_product(product_id, redis)
    elapsed = time.time() - start_time
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product": product,
        "cached": cache_stats.hits > 0,
        "response_time_ms": round(elapsed * 1000, 2),
        "pattern": "cache-aside"
    }


@app.get("/products")
@cache_result("products:all", ttl=60)
async def get_all_products(redis: aioredis.Redis = Depends(get_redis)):
    """
    Get all products (cached with decorator)
    Cache TTL: 60 seconds
    """
    return await db_get_all_products()


@app.get("/products/category/{category}")
async def get_products_by_category(
    category: str,
    redis: aioredis.Redis = Depends(get_redis)
):
    """
    Get products by category with caching
    Demonstrates cached queries
    """
    cache_key = f"category:{category}:products"
    start_time = time.time()
    
    # Try cache
    cached = await get_cache(redis, cache_key)
    if cached:
        cache_stats.hits += 1
        products = [Product(**json.loads(item)) for item in json.loads(cached)]
        elapsed = time.time() - start_time
        
        return {
            "products": products,
            "count": len(products),
            "cached": True,
            "response_time_ms": round(elapsed * 1000, 2)
        }
    
    # Cache miss
    cache_stats.misses += 1
    products = await db_get_products_by_category(category)
    
    # Store in cache
    cache_value = json.dumps([p.dict() for p in products])
    await set_cache(redis, cache_key, cache_value, ttl=120)
    
    elapsed = time.time() - start_time
    
    return {
        "products": products,
        "count": len(products),
        "cached": False,
        "response_time_ms": round(elapsed * 1000, 2)
    }


# ====================================
# WRITE-THROUGH PATTERN ENDPOINTS
# ====================================

@app.put("/products/{product_id}/write-through")
async def update_product_write_through(
    product_id: int,
    product: Product,
    redis: aioredis.Redis = Depends(get_redis)
):
    """
    Update product with Write-Through pattern
    - Update cache and database synchronously
    - Cache always in sync
    """
    start_time = time.time()
    updated = await WriteThroughPattern.update_product(product_id, product, redis)
    elapsed = time.time() - start_time
    
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product": updated,
        "pattern": "write-through",
        "response_time_ms": round(elapsed * 1000, 2)
    }


# ====================================
# WRITE-BEHIND PATTERN ENDPOINTS
# ====================================

@app.put("/products/{product_id}/write-behind")
async def update_product_write_behind(
    product_id: int,
    product: Product,
    background_tasks: BackgroundTasks,
    redis: aioredis.Redis = Depends(get_redis)
):
    """
    Update product with Write-Behind pattern
    - Update cache immediately
    - Queue database write
    - Fast response
    """
    start_time = time.time()
    updated = await write_behind.update_product(
        product_id, product, redis, background_tasks
    )
    elapsed = time.time() - start_time
    
    return {
        "product": updated,
        "pattern": "write-behind",
        "response_time_ms": round(elapsed * 1000, 2),
        "note": "Database write queued in background"
    }


# ====================================
# CACHE MANAGEMENT ENDPOINTS
# ====================================

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    total_requests = cache_stats.hits + cache_stats.misses
    hit_rate = (cache_stats.hits / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "hits": cache_stats.hits,
        "misses": cache_stats.misses,
        "total_requests": total_requests,
        "hit_rate_percent": round(hit_rate, 2),
        "redis_connected": redis_client is not None
    }


@app.post("/cache/clear")
async def clear_cache(redis: aioredis.Redis = Depends(get_redis)):
    """Clear all cached data"""
    if not redis:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    await redis.flushdb()
    
    # Reset stats
    cache_stats.hits = 0
    cache_stats.misses = 0
    
    return {"message": "Cache cleared successfully"}


@app.delete("/cache/product/{product_id}")
async def invalidate_product_cache(
    product_id: int,
    redis: aioredis.Redis = Depends(get_redis)
):
    """Invalidate cache for specific product"""
    if not redis:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    cache_key = f"product:{product_id}"
    await redis.delete(cache_key)
    
    return {"message": f"Cache invalidated for product {product_id}"}


@app.get("/cache/keys")
async def list_cache_keys(redis: aioredis.Redis = Depends(get_redis)):
    """List all cache keys (for debugging)"""
    if not redis:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    keys = []
    async for key in redis.scan_iter():
        ttl = await redis.ttl(key)
        keys.append({"key": key, "ttl_seconds": ttl})
    
    return {"keys": keys, "count": len(keys)}


# ====================================
# CREATE/DELETE ENDPOINTS
# ====================================

@app.post("/products", status_code=201)
async def create_product(
    product: Product,
    redis: aioredis.Redis = Depends(get_redis)
):
    """Create new product"""
    created = await db_create_product(product)
    
    # Cache the new product
    cache_key = f"product:{created.id}"
    await set_cache(redis, cache_key, created, ttl=300)
    
    # Invalidate list caches
    await delete_cache(redis, "products:*")
    await delete_cache(redis, f"category:{created.category}:*")
    
    return {"product": created}


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    redis: aioredis.Redis = Depends(get_redis)
):
    """Delete product"""
    deleted = await db_delete_product(product_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Invalidate caches
    await redis.delete(f"product:{product_id}")
    await delete_cache(redis, "products:*")
    await delete_cache(redis, "category:*")


if __name__ == "__main__":
    import uvicorn
    print("Starting Redis Caching API...")
    print("Make sure Redis is running: docker run -d -p 6379:6379 redis:alpine")
    uvicorn.run(app, host="0.0.0.0", port=8000)
