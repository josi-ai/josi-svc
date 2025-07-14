"""
Redis client configuration and connection management.
"""
import logging
from typing import Optional
from redis import asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from josi.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Singleton Redis client manager."""
    
    _instance: Optional['RedisClient'] = None
    _redis: Optional[aioredis.Redis] = None
    _pool: Optional[ConnectionPool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        if self._redis is not None:
            return
            
        try:
            # Create connection pool with hiredis for performance
            self._pool = aioredis.ConnectionPool.from_url(
                settings.redis_url or "redis://localhost:6379/0",
                max_connections=50,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                connection_class=aioredis.Connection,
                parser_class=aioredis.connection.HiredisParser,  # Use hiredis for speed
            )
            
            self._redis = aioredis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._redis.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Don't fail the app if Redis is unavailable
            self._redis = None
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            await self._pool.disconnect()
            self._redis = None
            self._pool = None
            logger.info("Redis connection closed")
    
    @property
    def client(self) -> Optional[aioredis.Redis]:
        """Get Redis client instance."""
        return self._redis
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self._redis:
            return None
            
        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value in Redis.
        
        Args:
            key: Redis key
            value: Value to store
            ex: Expire time in seconds
            px: Expire time in milliseconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists
            
        Returns:
            True if successful, False otherwise
        """
        if not self._redis:
            return False
            
        try:
            result = await self._redis.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis."""
        if not self._redis or not keys:
            return 0
            
        try:
            return await self._redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0
    
    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        if not self._redis or not keys:
            return 0
            
        try:
            return await self._redis.exists(*keys)
        except Exception as e:
            logger.error(f"Redis EXISTS error for keys {keys}: {e}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key."""
        if not self._redis:
            return False
            
        try:
            return await self._redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL of a key in seconds."""
        if not self._redis:
            return -2  # Key doesn't exist
            
        try:
            return await self._redis.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -2
    
    async def scan_iter(self, match: Optional[str] = None, count: int = 100):
        """Scan keys matching pattern."""
        if not self._redis:
            return
            
        try:
            async for key in self._redis.scan_iter(match=match, count=count):
                yield key
        except Exception as e:
            logger.error(f"Redis SCAN error with pattern {match}: {e}")
    
    async def flushdb(self) -> bool:
        """Flush current database (use with caution)."""
        if not self._redis:
            return False
            
        try:
            await self._redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check Redis health."""
        if not self._redis:
            return False
            
        try:
            await self._redis.ping()
            return True
        except Exception:
            return False


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency to get Redis client."""
    if redis_client.client is None:
        await redis_client.initialize()
    return redis_client