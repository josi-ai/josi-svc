"""
Cache decorator for automatic request caching with Redis.
"""
import json
import hashlib
import inspect
import functools
import logging
from typing import Any, Callable, Optional, Union, List, Dict
from datetime import datetime, date
from uuid import UUID

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from .client import get_redis

logger = logging.getLogger(__name__)


def generate_cache_key(
    prefix: str,
    func_name: str,
    args: tuple,
    kwargs: dict,
    include_org: bool = True
) -> str:
    """
    Generate a unique cache key from function arguments.
    
    Args:
        prefix: Cache key prefix
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments
        include_org: Include organization_id in key
        
    Returns:
        Unique cache key string
    """
    # Filter out non-serializable arguments
    cache_parts = [prefix, func_name]
    
    # Extract organization_id if present
    org_id = None
    if include_org:
        for arg in args:
            if hasattr(arg, 'id') and hasattr(arg, '__class__'):
                if arg.__class__.__name__ == 'Organization':
                    org_id = str(arg.id)
                    break
    
    if org_id:
        cache_parts.append(f"org:{org_id}")
    
    # Process arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            cache_parts.append(str(arg))
        elif isinstance(arg, (UUID, datetime, date)):
            cache_parts.append(str(arg))
        elif isinstance(arg, BaseModel):
            # For Pydantic models, use their dict representation
            cache_parts.append(json.dumps(arg.model_dump(), sort_keys=True))
        elif hasattr(arg, 'id'):
            # For objects with ID (like Person, Organization)
            cache_parts.append(f"{arg.__class__.__name__}:{arg.id}")
    
    # Process keyword arguments
    for key, value in sorted(kwargs.items()):
        if key in ['db', 'organization', 'request', 'response']:
            continue  # Skip dependency injection arguments
            
        if isinstance(value, (str, int, float, bool)):
            cache_parts.append(f"{key}:{value}")
        elif isinstance(value, (UUID, datetime, date)):
            cache_parts.append(f"{key}:{value}")
        elif isinstance(value, list):
            cache_parts.append(f"{key}:{','.join(map(str, value))}")
        elif isinstance(value, BaseModel):
            cache_parts.append(f"{key}:{value.model_dump_json()}")
    
    # Create hash of all parts for consistent length
    cache_string = ":".join(cache_parts)
    cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
    
    # Return readable prefix with hash
    return f"{prefix}:{func_name}:{cache_hash}"


def cache(
    expire: int = 3600,  # 1 hour default
    prefix: str = "josi",
    include_org: bool = True,
    key_builder: Optional[Callable] = None,
    condition: Optional[Callable] = None,
    skip_cache_header: str = "X-Skip-Cache"
):
    """
    Cache decorator for FastAPI endpoints.
    
    Args:
        expire: Cache expiration in seconds
        prefix: Cache key prefix
        include_org: Include organization in cache key
        key_builder: Custom key builder function
        condition: Function to determine if result should be cached
        skip_cache_header: Header to skip cache
    
    Usage:
        @router.get("/endpoint")
        @cache(expire=3600)
        async def get_data(...):
            return data
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if caching is disabled via header
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request and request.headers.get(skip_cache_header):
                logger.debug(f"Skipping cache for {func.__name__} due to header")
                return await func(*args, **kwargs)
            
            # Get Redis client
            redis = await get_redis()
            if not redis.client:
                # Redis not available, proceed without cache
                return await func(*args, **kwargs)
            
            # Generate cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = generate_cache_key(
                    prefix, func.__name__, args, kwargs, include_org
                )
            
            # Try to get from cache
            try:
                cached_value = await redis.get(cache_key)
                if cached_value:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    # Deserialize the cached value
                    cached_data = json.loads(cached_value)
                    
                    # If it's a ResponseModel, reconstruct it
                    if isinstance(cached_data, dict) and 'success' in cached_data:
                        from josi.api.response import ResponseModel
                        return ResponseModel(**cached_data)
                    return cached_data
            except Exception as e:
                logger.error(f"Cache retrieval error: {e}")
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Check condition if provided
            if condition and not condition(result):
                return result
            
            # Store in cache
            try:
                # Handle different response types
                if hasattr(result, 'model_dump'):
                    # Pydantic model
                    cache_value = json.dumps(jsonable_encoder(result))
                elif hasattr(result, '__dict__'):
                    # Regular object
                    cache_value = json.dumps(jsonable_encoder(result.__dict__))
                else:
                    # Primitive or dict
                    cache_value = json.dumps(jsonable_encoder(result))
                
                # Store with expiration
                await redis.set(cache_key, cache_value, ex=expire)
                
                # Track cache dependencies for invalidation
                await _track_cache_dependency(cache_key, args, kwargs)
                
            except Exception as e:
                logger.error(f"Cache storage error: {e}")
            
            return result
        
        return wrapper
    return decorator


async def _track_cache_dependency(cache_key: str, args: tuple, kwargs: dict):
    """Track which database records are associated with this cache key."""
    # This will be implemented when we set up cache invalidation
    pass


class CacheKeyWrapper:
    """Helper class for building complex cache keys."""
    
    def __init__(self, prefix: str = "josi"):
        self.prefix = prefix
        self.parts = [prefix]
    
    def add(self, key: str, value: Any) -> 'CacheKeyWrapper':
        """Add a key-value pair to the cache key."""
        if isinstance(value, (UUID, datetime, date)):
            self.parts.append(f"{key}:{value}")
        elif isinstance(value, BaseModel):
            self.parts.append(f"{key}:{value.model_dump_json()}")
        else:
            self.parts.append(f"{key}:{value}")
        return self
    
    def build(self) -> str:
        """Build the final cache key."""
        cache_string = ":".join(self.parts)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        return f"{self.prefix}:{cache_hash}"


def cache_key_wrapper(prefix: str = "josi") -> CacheKeyWrapper:
    """Create a new cache key wrapper."""
    return CacheKeyWrapper(prefix)


async def invalidate_cache(
    pattern: Optional[str] = None,
    keys: Optional[List[str]] = None,
    tags: Optional[List[str]] = None
) -> int:
    """
    Invalidate cache entries.
    
    Args:
        pattern: Redis key pattern to match (e.g., "josi:person:*")
        keys: Specific keys to invalidate
        tags: Cache tags to invalidate (not implemented yet)
        
    Returns:
        Number of keys deleted
    """
    redis = await get_redis()
    if not redis.client:
        return 0
    
    deleted_count = 0
    
    # Delete specific keys
    if keys:
        deleted_count += await redis.delete(*keys)
    
    # Delete by pattern
    if pattern:
        keys_to_delete = []
        async for key in redis.scan_iter(match=pattern):
            keys_to_delete.append(key)
            
        if keys_to_delete:
            deleted_count += await redis.delete(*keys_to_delete)
    
    logger.info(f"Invalidated {deleted_count} cache keys")
    return deleted_count


# Specific cache decorators for common use cases
def cache_person_data(expire: int = 7200):
    """Cache decorator specifically for person-related endpoints."""
    return cache(expire=expire, prefix="person")


def cache_chart_data(expire: int = 86400):
    """Cache decorator for chart calculations (24 hours)."""
    return cache(expire=expire, prefix="chart")


def cache_prediction_data(expire: int = 3600):
    """Cache decorator for predictions (1 hour)."""
    return cache(expire=expire, prefix="prediction")


def cache_panchang_data(expire: int = 21600):
    """Cache decorator for panchang data (6 hours)."""
    return cache(expire=expire, prefix="panchang")