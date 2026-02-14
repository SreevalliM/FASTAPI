"""
Rate Limiting Strategies with FastAPI

Demonstrates different rate limiting approaches:
- Fixed Window Rate Limiting
- Sliding Window Rate Limiting
- Token Bucket Algorithm
- Per-user and per-IP rate limiting
- Custom rate limiting with Redis

Install: pip install slowapi redis
Run: uvicorn 13_rate_limiting:app --reload
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional, Dict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import asyncio


# ====================================
# CUSTOM RATE LIMITERS
# ====================================

class TokenBucketLimiter:
    """
    Token Bucket Algorithm
    - Allows burst traffic
    - Tokens refill at a constant rate
    - Can accumulate tokens up to bucket capacity
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Dict] = {}
    
    def _get_bucket(self, key: str) -> Dict:
        """Get or create bucket for key"""
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": self.capacity,
                "last_update": time.time()
            }
        return self.buckets[key]
    
    def _refill_tokens(self, bucket: Dict):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - bucket["last_update"]
        tokens_to_add = elapsed * self.refill_rate
        
        bucket["tokens"] = min(
            self.capacity,
            bucket["tokens"] + tokens_to_add
        )
        bucket["last_update"] = now
    
    def allow_request(self, key: str, tokens_needed: int = 1) -> bool:
        """Check if request is allowed"""
        bucket = self._get_bucket(key)
        self._refill_tokens(bucket)
        
        if bucket["tokens"] >= tokens_needed:
            bucket["tokens"] -= tokens_needed
            return True
        return False
    
    def get_wait_time(self, key: str) -> float:
        """Get wait time until next token available"""
        bucket = self._get_bucket(key)
        self._refill_tokens(bucket)
        
        if bucket["tokens"] >= 1:
            return 0.0
        
        tokens_needed = 1 - bucket["tokens"]
        return tokens_needed / self.refill_rate


class SlidingWindowLimiter:
    """
    Sliding Window Algorithm
    - More accurate than fixed window
    - Prevents burst at window boundaries
    - Tracks timestamps of each request
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def _cleanup_old_requests(self, key: str):
        """Remove requests outside the window"""
        cutoff_time = time.time() - self.window_seconds
        
        while self.requests[key] and self.requests[key][0] < cutoff_time:
            self.requests[key].popleft()
    
    def allow_request(self, key: str) -> bool:
        """Check if request is allowed"""
        self._cleanup_old_requests(key)
        
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(time.time())
            return True
        return False
    
    def get_remaining_requests(self, key: str) -> int:
        """Get number of remaining requests in window"""
        self._cleanup_old_requests(key)
        return max(0, self.max_requests - len(self.requests[key]))
    
    def get_reset_time(self, key: str) -> float:
        """Get time until window resets"""
        if not self.requests[key]:
            return 0.0
        
        oldest_request = self.requests[key][0]
        reset_time = oldest_request + self.window_seconds
        return max(0.0, reset_time - time.time())


class FixedWindowCounter:
    """
    Fixed Window Algorithm
    - Simple and memory efficient
    - Can have burst at window boundaries
    - Resets at fixed intervals
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.windows: Dict[str, Dict] = {}
    
    def _get_current_window(self, key: str) -> Dict:
        """Get or create current window"""
        now = time.time()
        window_start = int(now / self.window_seconds) * self.window_seconds
        
        if key not in self.windows or self.windows[key]["start"] != window_start:
            self.windows[key] = {
                "start": window_start,
                "count": 0
            }
        
        return self.windows[key]
    
    def allow_request(self, key: str) -> bool:
        """Check if request is allowed"""
        window = self._get_current_window(key)
        
        if window["count"] < self.max_requests:
            window["count"] += 1
            return True
        return False
    
    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests in current window"""
        window = self._get_current_window(key)
        return max(0, self.max_requests - window["count"])


# ====================================
# REDIS-BASED RATE LIMITER
# ====================================

class RedisRateLimiter:
    """
    Redis-based rate limiter for distributed systems
    Note: Requires Redis connection
    """
    
    def __init__(self, redis_client=None, max_requests: int = 100, window: int = 60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window
    
    async def allow_request(self, key: str) -> bool:
        """Check if request allowed using Redis"""
        if self.redis is None:
            return True  # Fallback if Redis not available
        
        try:
            # Use Redis INCR with EXPIRE
            count_key = f"ratelimit:{key}"
            current = await self.redis.incr(count_key)
            
            if current == 1:
                await self.redis.expire(count_key, self.window)
            
            return current <= self.max_requests
        except Exception as e:
            print(f"Redis error: {e}")
            return True  # Fail open on Redis errors


# ====================================
# FASTAPI APPLICATION
# ====================================

app = FastAPI(
    title="Rate Limiting Examples",
    description="Demonstrates various rate limiting strategies",
    version="1.0.0"
)

# Initialize SlowAPI limiter (simple approach)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize custom limiters
token_bucket = TokenBucketLimiter(capacity=10, refill_rate=2.0)  # 10 tokens, refill 2/sec
sliding_window = SlidingWindowLimiter(max_requests=5, window_seconds=60)  # 5 req/min
fixed_window = FixedWindowCounter(max_requests=10, window_seconds=60)  # 10 req/min


# ====================================
# HELPER FUNCTIONS
# ====================================

def get_client_id(request: Request, api_key: Optional[str] = Header(None)) -> str:
    """Get client identifier (IP or API key)"""
    if api_key:
        return f"key:{api_key}"
    return f"ip:{request.client.host}"


# ====================================
# API ENDPOINTS
# ====================================

@app.get("/")
async def root():
    """API information"""
    return {
        "message": "Rate Limiting API",
        "strategies": {
            "fixed_window": "Simple, can burst at boundaries",
            "sliding_window": "More accurate, prevents boundary bursts",
            "token_bucket": "Allows controlled bursts",
            "slowapi": "Easy integration with decorators"
        },
        "endpoints": {
            "slowapi": "/slowapi/basic",
            "fixed_window": "/fixed-window/data",
            "sliding_window": "/sliding-window/data",
            "token_bucket": "/token-bucket/data",
            "per_user": "/user/data"
        }
    }


# ====================================
# SLOWAPI EXAMPLES (Decorator-based)
# ====================================

@app.get("/slowapi/basic")
@limiter.limit("5/minute")
async def slowapi_basic(request: Request):
    """
    Basic rate limiting with SlowAPI
    Limit: 5 requests per minute per IP
    """
    return {
        "message": "Success",
        "rate_limit": "5 requests per minute",
        "strategy": "SlowAPI (fixed window)"
    }


@app.get("/slowapi/multiple")
@limiter.limit("10/second;100/minute;500/hour")
async def slowapi_multiple(request: Request):
    """
    Multiple rate limits
    10/sec, 100/min, 500/hour - strictest applies
    """
    return {
        "message": "Success",
        "rate_limit": "10/sec, 100/min, 500/hour",
        "strategy": "SlowAPI (multiple limits)"
    }


@app.get("/slowapi/exempt")
@limiter.exempt
async def slowapi_exempt(request: Request):
    """Endpoint exempt from rate limiting"""
    return {
        "message": "No rate limit on this endpoint",
        "strategy": "Exempt"
    }


# ====================================
# FIXED WINDOW EXAMPLES
# ====================================

@app.get("/fixed-window/data")
async def fixed_window_endpoint(request: Request):
    """
    Fixed window rate limiting
    Limit: 10 requests per 60 seconds
    """
    client_id = get_client_id(request)
    
    if not fixed_window.allow_request(client_id):
        remaining = fixed_window.get_remaining_requests(client_id)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "strategy": "Fixed Window",
                "limit": "10 requests per minute",
                "remaining": remaining
            }
        )
    
    remaining = fixed_window.get_remaining_requests(client_id)
    return {
        "message": "Success",
        "strategy": "Fixed Window",
        "remaining_requests": remaining,
        "window": "60 seconds"
    }


# ====================================
# SLIDING WINDOW EXAMPLES
# ====================================

@app.get("/sliding-window/data")
async def sliding_window_endpoint(request: Request):
    """
    Sliding window rate limiting
    Limit: 5 requests per 60 seconds
    More accurate than fixed window
    """
    client_id = get_client_id(request)
    
    if not sliding_window.allow_request(client_id):
        remaining = sliding_window.get_remaining_requests(client_id)
        reset_time = sliding_window.get_reset_time(client_id)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "strategy": "Sliding Window",
                "limit": "5 requests per minute",
                "remaining": remaining,
                "reset_in_seconds": round(reset_time, 2)
            }
        )
    
    remaining = sliding_window.get_remaining_requests(client_id)
    reset_time = sliding_window.get_reset_time(client_id)
    
    return {
        "message": "Success",
        "strategy": "Sliding Window",
        "remaining_requests": remaining,
        "reset_in_seconds": round(reset_time, 2)
    }


# ====================================
# TOKEN BUCKET EXAMPLES
# ====================================

@app.get("/token-bucket/data")
async def token_bucket_endpoint(request: Request):
    """
    Token bucket rate limiting
    Capacity: 10 tokens, refills at 2 tokens/second
    Allows controlled bursts
    """
    client_id = get_client_id(request)
    
    if not token_bucket.allow_request(client_id, tokens_needed=1):
        wait_time = token_bucket.get_wait_time(client_id)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "strategy": "Token Bucket",
                "capacity": 10,
                "refill_rate": "2 tokens/second",
                "retry_after_seconds": round(wait_time, 2)
            }
        )
    
    return {
        "message": "Success",
        "strategy": "Token Bucket",
        "info": "Allows bursts up to 10 requests, refills at 2/second"
    }


@app.get("/token-bucket/expensive")
async def expensive_operation(request: Request):
    """
    Expensive operation requiring multiple tokens
    Costs 5 tokens (simulates heavier operation)
    """
    client_id = get_client_id(request)
    tokens_needed = 5
    
    if not token_bucket.allow_request(client_id, tokens_needed=tokens_needed):
        wait_time = token_bucket.get_wait_time(client_id)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Insufficient tokens",
                "strategy": "Token Bucket",
                "tokens_needed": tokens_needed,
                "retry_after_seconds": round(wait_time, 2)
            }
        )
    
    return {
        "message": "Expensive operation completed",
        "tokens_consumed": tokens_needed,
        "strategy": "Token Bucket"
    }


# ====================================
# PER-USER RATE LIMITING
# ====================================

# User-specific limiters
user_limiters: Dict[str, SlidingWindowLimiter] = {}

def get_user_limiter(api_key: str) -> SlidingWindowLimiter:
    """Get or create limiter for specific user"""
    if api_key not in user_limiters:
        # Premium users get higher limits
        if api_key.startswith("premium_"):
            user_limiters[api_key] = SlidingWindowLimiter(100, 60)
        else:
            user_limiters[api_key] = SlidingWindowLimiter(10, 60)
    return user_limiters[api_key]


@app.get("/user/data")
async def user_specific_rate_limit(api_key: Optional[str] = Header(None)):
    """
    Per-user rate limiting with different tiers
    Free: 10 requests/minute
    Premium: 100 requests/minute
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required in header"
        )
    
    limiter = get_user_limiter(api_key)
    
    if not limiter.allow_request(api_key):
        remaining = limiter.get_remaining_requests(api_key)
        reset_time = limiter.get_reset_time(api_key)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "remaining": remaining,
                "reset_in_seconds": round(reset_time, 2)
            }
        )
    
    remaining = limiter.get_remaining_requests(api_key)
    tier = "premium" if api_key.startswith("premium_") else "free"
    limit = 100 if tier == "premium" else 10
    
    return {
        "message": "Success",
        "tier": tier,
        "limit": f"{limit} requests/minute",
        "remaining": remaining
    }


# ====================================
# STATISTICS ENDPOINT
# ====================================

@app.get("/stats")
async def get_stats():
    """Get rate limiting statistics"""
    return {
        "active_clients": {
            "token_bucket": len(token_bucket.buckets),
            "sliding_window": len(sliding_window.requests),
            "fixed_window": len(fixed_window.windows),
            "user_specific": len(user_limiters)
        },
        "configurations": {
            "token_bucket": {
                "capacity": token_bucket.capacity,
                "refill_rate": token_bucket.refill_rate
            },
            "sliding_window": {
                "max_requests": sliding_window.max_requests,
                "window_seconds": sliding_window.window_seconds
            },
            "fixed_window": {
                "max_requests": fixed_window.max_requests,
                "window_seconds": fixed_window.window_seconds
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Rate Limiting API...")
    print("Test with: curl http://localhost:8000/slowapi/basic")
    print("Or use the interactive docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
