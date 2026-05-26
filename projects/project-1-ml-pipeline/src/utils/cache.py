"""Redis caching utilities for the ML pipeline."""

import json
import pickle
from typing import Any, Optional, Union

import redis
from redis.exceptions import RedisError

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class CacheManager:
    """Manage caching operations using Redis."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        decode_responses: bool = False,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        retry_on_timeout: bool = True,
        max_connections: int = 50,
    ):
        """Initialize cache manager.

        Args:
            host: Redis host (uses config if not provided)
            port: Redis port (uses config if not provided)
            db: Redis database number (uses config if not provided)
            password: Redis password (uses config if not provided)
            decode_responses: Whether to decode responses to strings
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Connection timeout in seconds
            retry_on_timeout: Whether to retry on timeout
            max_connections: Maximum number of connections in pool
        """
        config = get_config()

        self.host = host or config.redis_host
        self.port = port or config.redis_port
        self.db = db or config.redis_db
        self.password = password or config.redis_password

        try:
            # Create connection pool
            self.pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=decode_responses,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
                retry_on_timeout=retry_on_timeout,
                max_connections=max_connections,
            )

            # Create Redis client
            self.client = redis.Redis(connection_pool=self.pool)

            # Test connection
            self.client.ping()
            logger.info(f"Cache manager initialized (Redis {self.host}:{self.port}/{self.db})")
        except RedisError as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            raise

    def get(
        self,
        key: str,
        default: Optional[Any] = None,
        deserialize: bool = True,
    ) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key doesn't exist
            deserialize: Whether to deserialize value from JSON/pickle

        Returns:
            Cached value or default
        """
        try:
            value = self.client.get(key)

            if value is None:
                metrics.increment_cache_misses("redis")
                logger.debug(f"Cache miss: {key}")
                return default

            metrics.increment_cache_hits("redis")
            logger.debug(f"Cache hit: {key}")

            if deserialize and isinstance(value, bytes):
                try:
                    # Try JSON first
                    return json.loads(value.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Fall back to pickle
                    return pickle.loads(value)

            return value

        except RedisError as e:
            logger.error(f"Failed to get cache key '{key}': {e}")
            return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True,
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)
            serialize: Whether to serialize value to JSON/pickle

        Returns:
            True if successful, False otherwise
        """
        try:
            if serialize:
                try:
                    # Try JSON first
                    value = json.dumps(value)
                except (TypeError, ValueError):
                    # Fall back to pickle
                    value = pickle.dumps(value)

            if ttl:
                result = self.client.setex(key, ttl, value)
            else:
                result = self.client.set(key, value)

            logger.debug(f"Cache set: {key} (TTL: {ttl})")
            return bool(result)

        except RedisError as e:
            logger.error(f"Failed to set cache key '{key}': {e}")
            return False

    def delete(self, *keys: str) -> int:
        """Delete keys from cache.

        Args:
            *keys: Keys to delete

        Returns:
            Number of keys deleted
        """
        try:
            count = self.client.delete(*keys)
            logger.debug(f"Deleted {count} cache keys")
            return count
        except RedisError as e:
            logger.error(f"Failed to delete cache keys: {e}")
            return 0

    def exists(self, *keys: str) -> int:
        """Check if keys exist in cache.

        Args:
            *keys: Keys to check

        Returns:
            Number of keys that exist
        """
        try:
            return self.client.exists(*keys)
        except RedisError as e:
            logger.error(f"Failed to check cache keys: {e}")
            return 0

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key.

        Args:
            key: Cache key
            seconds: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.expire(key, seconds)
            return bool(result)
        except RedisError as e:
            logger.error(f"Failed to set expiration for key '{key}': {e}")
            return False

    def ttl(self, key: str) -> int:
        """Get time to live for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds (-1 if no expiration, -2 if key doesn't exist)
        """
        try:
            return self.client.ttl(key)
        except RedisError as e:
            logger.error(f"Failed to get TTL for key '{key}': {e}")
            return -2

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment value of a key.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value after increment, None on error
        """
        try:
            return self.client.incrby(key, amount)
        except RedisError as e:
            logger.error(f"Failed to increment key '{key}': {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement value of a key.

        Args:
            key: Cache key
            amount: Amount to decrement by

        Returns:
            New value after decrement, None on error
        """
        try:
            return self.client.decrby(key, amount)
        except RedisError as e:
            logger.error(f"Failed to decrement key '{key}': {e}")
            return None

    def flush(self, pattern: Optional[str] = None) -> int:
        """Flush cache keys matching pattern.

        Args:
            pattern: Key pattern to match (e.g., "user:*")
                    If None, flushes entire database

        Returns:
            Number of keys deleted
        """
        try:
            if pattern:
                # Delete keys matching pattern
                keys = list(self.client.scan_iter(match=pattern))
                if keys:
                    count = self.client.delete(*keys)
                    logger.info(f"Flushed {count} keys matching pattern '{pattern}'")
                    return count
                return 0
            else:
                # Flush entire database
                self.client.flushdb()
                logger.warning("Flushed entire cache database")
                return -1  # Unknown count
        except RedisError as e:
            logger.error(f"Failed to flush cache: {e}")
            return 0

    def get_info(self) -> dict:
        """Get Redis server information.

        Returns:
            Dictionary containing server information
        """
        try:
            return self.client.info()
        except RedisError as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {}

    def ping(self) -> bool:
        """Ping Redis server.

        Returns:
            True if server is responsive, False otherwise
        """
        try:
            return self.client.ping()
        except RedisError as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    def close(self) -> None:
        """Close Redis connections."""
        try:
            self.client.close()
            logger.info("Cache connections closed")
        except RedisError as e:
            logger.error(f"Error closing cache connections: {e}")

    def __enter__(self) -> "CacheManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class CachedProperty:
    """Decorator for caching property values in Redis."""

    def __init__(
        self,
        ttl: Optional[int] = None,
        key_prefix: Optional[str] = None,
    ):
        """Initialize cached property decorator.

        Args:
            ttl: Time to live in seconds
            key_prefix: Prefix for cache keys
        """
        self.ttl = ttl
        self.key_prefix = key_prefix or "cached_property"
        self.cache = get_cache_manager()

    def __call__(self, func):
        """Decorate function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """
        def wrapper(instance):
            # Generate cache key
            key = f"{self.key_prefix}:{instance.__class__.__name__}:{func.__name__}:{id(instance)}"

            # Try to get from cache
            value = self.cache.get(key)
            if value is not None:
                return value

            # Compute value
            value = func(instance)

            # Store in cache
            self.cache.set(key, value, ttl=self.ttl)

            return value

        return wrapper


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance.

    Returns:
        CacheManager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
