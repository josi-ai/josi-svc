"""
Production-ready caching system with Redis and performance optimizations
"""
import json
import pickle
import hashlib
import asyncio
from typing import Any, Optional, Dict, List, Union, Callable
from functools import wraps
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class CacheManager:
    """Advanced caching manager with Redis backend"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client = None
        self.default_ttl = 3600  # 1 hour
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }
    
    async def initialize(self):
        """Initialize Redis connection, using settings.redis_url if available."""
        try:
            from josi.core.config import settings
            if settings.redis_url:
                self.redis_url = settings.redis_url
            import redis.asyncio as redis
            self.redis_client = redis.from_url(self.redis_url, decode_responses=False)
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except ImportError:
            logger.warning("Redis not available, using in-memory cache")
            self.redis_client = InMemoryCache()
        except Exception as e:
            logger.warning("Redis connection failed, using in-memory cache", error=str(e))
            self.redis_client = InMemoryCache()
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client and hasattr(self.redis_client, 'close'):
            await self.redis_client.close()
    
    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate consistent cache key from parameters"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"josi:{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            if not self.redis_client:
                return None
                
            cached_data = await self.redis_client.get(key)
            if cached_data:
                self.cache_stats["hits"] += 1
                return pickle.loads(cached_data)
            else:
                self.cache_stats["misses"] += 1
                return None
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.warning("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value"""
        try:
            if not self.redis_client:
                return False
                
            ttl = ttl or self.default_ttl
            serialized_data = pickle.dumps(value)
            
            await self.redis_client.setex(key, ttl, serialized_data)
            self.cache_stats["sets"] += 1
            return True
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.warning("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, pattern: str) -> int:
        """Delete cache keys matching pattern"""
        try:
            if not self.redis_client:
                return 0
                
            if hasattr(self.redis_client, 'keys'):
                keys = await self.redis_client.keys(pattern)
                if keys:
                    return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("Cache delete failed", pattern=pattern, error=str(e))
            return 0
    
    def cache_result(self, prefix: str, ttl: Optional[int] = None, 
                    key_func: Optional[Callable] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self.generate_cache_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    logger.debug("Cache hit", key=cache_key, function=func.__name__)
                    return cached_result
                
                # Execute function and cache result
                start_time = datetime.now()
                result = await func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                await self.set(cache_key, result, ttl)
                logger.debug("Cache miss - result cached", 
                           key=cache_key, 
                           function=func.__name__,
                           execution_time_ms=execution_time * 1000)
                
                return result
            return wrapper
        return decorator
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "errors": self.cache_stats["errors"],
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }


class InMemoryCache:
    """Fallback in-memory cache when Redis is not available"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
    
    async def get(self, key: str) -> Optional[bytes]:
        """Get value from in-memory cache"""
        item = self.cache.get(key)
        if item is None:
            return None
        
        value, expiry = item
        if expiry and datetime.now() > expiry:
            del self.cache[key]
            return None
        
        return value
    
    async def setex(self, key: str, ttl: int, value: bytes) -> bool:
        """Set value with expiry in in-memory cache"""
        # Simple LRU eviction
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
        return True
    
    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern (simplified)"""
        import fnmatch
        return [key for key in self.cache.keys() if fnmatch.fnmatch(key, pattern)]
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from cache"""
        deleted = 0
        for key in keys:
            if key in self.cache:
                del self.cache[key]
                deleted += 1
        return deleted
    
    async def ping(self) -> bool:
        """Ping test for compatibility"""
        return True


class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    @staticmethod
    def batch_process(items: List[Any], batch_size: int = 100) -> List[List[Any]]:
        """Split items into batches for processing"""
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    @staticmethod
    async def parallel_execute(tasks: List[Callable], max_concurrency: int = 10) -> List[Any]:
        """Execute tasks in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def bounded_task(task):
            async with semaphore:
                return await task()
        
        return await asyncio.gather(*[bounded_task(task) for task in tasks])
    
    @staticmethod
    def memoize_sync(max_size: int = 128):
        """Simple memoization decorator for synchronous functions"""
        def decorator(func):
            cache = {}
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = str(args) + str(sorted(kwargs.items()))
                if key in cache:
                    return cache[key]
                
                result = func(*args, **kwargs)
                
                if len(cache) >= max_size:
                    # Remove oldest item (simple FIFO)
                    oldest_key = next(iter(cache))
                    del cache[oldest_key]
                
                cache[key] = result
                return result
            
            return wrapper
        return decorator


# Specialized cache for astrological calculations
class AstrologyCache:
    """Specialized caching for astrological calculations"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    @property
    def cache_planetary_positions(self):
        """Cache planetary positions (long TTL as they don't change much)"""
        return self.cache_manager.cache_result("planetary_pos", ttl=86400)  # 24 hours
    
    @property
    def cache_house_cusps(self):
        """Cache house cusps"""
        return self.cache_manager.cache_result("house_cusps", ttl=86400)  # 24 hours
    
    @property
    def cache_chart_calculation(self):
        """Cache complete chart calculations"""
        return self.cache_manager.cache_result("chart_calc", ttl=7200)  # 2 hours
    
    @property
    def cache_compatibility(self):
        """Cache compatibility calculations"""
        return self.cache_manager.cache_result("compatibility", ttl=3600)  # 1 hour
    
    @property
    def cache_predictions(self):
        """Cache predictions (shorter TTL as they're time-sensitive)"""
        return self.cache_manager.cache_result("predictions", ttl=1800)  # 30 minutes
    
    @property
    def cache_divisional_charts(self):
        """Cache divisional charts"""
        return self.cache_manager.cache_result("divisional", ttl=86400)  # 24 hours
    
    async def invalidate_person_cache(self, person_id: str):
        """Invalidate all cache entries for a specific person"""
        patterns = [
            f"josi:chart_calc:*{person_id}*",
            f"josi:compatibility:*{person_id}*", 
            f"josi:predictions:*{person_id}*",
            f"josi:divisional:*{person_id}*"
        ]
        
        for pattern in patterns:
            await self.cache_manager.delete(pattern)
        
        logger.info("Cache invalidated for person", person_id=person_id)


# Global cache instances — URL resolved lazily from settings at initialize() time
cache_manager = CacheManager()
astrology_cache = AstrologyCache(cache_manager)

# Redis client for direct access
redis_client = cache_manager