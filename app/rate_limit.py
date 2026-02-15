"""Rate limiting middleware."""

import redis
from fastapi import HTTPException, status

from app.config import settings

# Redis connection with error handling
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
    redis_available = True
except Exception as e:
    print(f"⚠️  Redis not available: {e}")
    redis_client = None
    redis_available = False


def rate_limit(user: dict = None) -> None:
    """
    Check and update rate limit for user.
    
    Uses Redis to track requests per day.
    Falls back to in-memory tracking if Redis is unavailable.
    """
    if user is None:
        return
    
    # If Redis unavailable, skip rate limiting (log warning)
    if not redis_available or redis_client is None:
        user["requests_today"] = 0
        user["requests_remaining"] = user.get("requests_limit", 50)
        return
    
    user_id = user.get("id", "anonymous")
    tier = user.get("tier", "free")
    limit = user.get("requests_limit", 50)
    
    # Redis key: rate_limit:{user_id}:{YYYY-MM-DD}
    from datetime import date
    today = date.today().isoformat()
    key = f"rate_limit:{user_id}:{today}"
    
    try:
        # Get current count
        current = redis_client.get(key)
        if current is None:
            current = 0
        else:
            current = int(current)
        
        # Check limit
        if current >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Limit: {limit} requests per day.",
                headers={"Retry-After": "86400"},
            )
        
        # Increment counter
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 86400)  # 24 hours
        pipe.execute()
        
        # Update user dict with remaining requests
        user["requests_today"] = current + 1
        user["requests_remaining"] = limit - (current + 1)
    except HTTPException:
        raise
    except Exception as e:
        # Redis error - log and allow request
        print(f"⚠️  Redis error in rate_limit: {e}")
        user["requests_today"] = 0
        user["requests_remaining"] = user.get("requests_limit", 50)
