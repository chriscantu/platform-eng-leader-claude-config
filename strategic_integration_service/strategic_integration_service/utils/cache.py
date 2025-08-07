"""Advanced caching system for Strategic Integration Service.

Multi-tier caching strategy:
1. Redis (fast, distributed)
2. File-based (persistent, local fallback)
3. Memory (ultra-fast, session-scoped)
"""

import hashlib
import json
import pickle
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union

import structlog

logger = structlog.get_logger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend with TTL support."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return time.time() > entry["expires_at"]

    def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if self._is_expired(entry):
            del self._cache[key]
            return None

        logger.debug("Cache hit (memory)", key=key[:50])
        return entry["value"]

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in memory cache."""
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time(),
        }
        logger.debug("Cache set (memory)", key=key[:50], ttl=ttl)

    def delete(self, key: str) -> None:
        """Delete value from memory cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug("Cache delete (memory)", key=key[:50])

    def clear(self) -> None:
        """Clear all memory cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info("Memory cache cleared", entries_removed=count)

    def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        if key not in self._cache:
            return False
        return not self._is_expired(self._cache[key])


class FileCache(CacheBackend):
    """File-based cache backend with TTL support."""

    def __init__(self, cache_dir: Union[str, Path] = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        # Create safe filename from cache key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"

    def _is_expired(self, metadata: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return time.time() > metadata.get("expires_at", 0)

    def get(self, key: str) -> Optional[Any]:
        """Get value from file cache."""
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with cache_path.open("rb") as f:
                data = pickle.load(f)

            if self._is_expired(data["metadata"]):
                cache_path.unlink(missing_ok=True)
                return None

            logger.debug("Cache hit (file)", key=key[:50], file=cache_path.name)
            return data["value"]

        except Exception as e:
            logger.warning("File cache read error", key=key[:50], error=str(e))
            cache_path.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in file cache."""
        cache_path = self._get_cache_path(key)

        data = {
            "value": value,
            "metadata": {
                "expires_at": time.time() + ttl,
                "created_at": time.time(),
                "key": key,
            },
        }

        try:
            with cache_path.open("wb") as f:
                pickle.dump(data, f)
            logger.debug("Cache set (file)", key=key[:50], ttl=ttl)
        except Exception as e:
            logger.error("File cache write error", key=key[:50], error=str(e))

    def delete(self, key: str) -> None:
        """Delete value from file cache."""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            logger.debug("Cache delete (file)", key=key[:50])

    def clear(self) -> None:
        """Clear all file cache entries."""
        count = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
            count += 1
        logger.info("File cache cleared", entries_removed=count)

    def exists(self, key: str) -> bool:
        """Check if key exists in file cache."""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return False

        try:
            with cache_path.open("rb") as f:
                data = pickle.load(f)
            return not self._is_expired(data["metadata"])
        except Exception:
            return False


class RedisCache(CacheBackend):
    """Redis cache backend (optional, requires redis-py)."""

    def __init__(
        self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None
    ):
        try:
            import redis

            self.redis = redis.Redis(
                host=host, port=port, db=db, password=password, decode_responses=False
            )
            # Test connection
            self.redis.ping()
            self.available = True
            logger.info("Redis cache initialized", host=host, port=port, db=db)
        except ImportError:
            logger.warning("Redis not available - install redis-py for Redis caching")
            self.available = False
        except Exception as e:
            logger.warning("Redis connection failed", error=str(e))
            self.available = False

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self.available:
            return None

        try:
            data = self.redis.get(key)
            if data is None:
                return None

            value = pickle.loads(data)
            logger.debug("Cache hit (Redis)", key=key[:50])
            return value
        except Exception as e:
            logger.warning("Redis cache read error", key=key[:50], error=str(e))
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in Redis cache."""
        if not self.available:
            return

        try:
            data = pickle.dumps(value)
            self.redis.setex(key, ttl, data)
            logger.debug("Cache set (Redis)", key=key[:50], ttl=ttl)
        except Exception as e:
            logger.error("Redis cache write error", key=key[:50], error=str(e))

    def delete(self, key: str) -> None:
        """Delete value from Redis cache."""
        if not self.available:
            return

        try:
            self.redis.delete(key)
            logger.debug("Cache delete (Redis)", key=key[:50])
        except Exception as e:
            logger.warning("Redis cache delete error", key=key[:50], error=str(e))

    def clear(self) -> None:
        """Clear all Redis cache entries."""
        if not self.available:
            return

        try:
            count = self.redis.dbsize()
            self.redis.flushdb()
            logger.info("Redis cache cleared", entries_removed=count)
        except Exception as e:
            logger.error("Redis cache clear error", error=str(e))

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        if not self.available:
            return False

        try:
            return bool(self.redis.exists(key))
        except Exception:
            return False


class MultiTierCache:
    """Multi-tier cache with memory, file, and optional Redis backends."""

    def __init__(
        self,
        enable_memory: bool = True,
        enable_file: bool = True,
        enable_redis: bool = False,
        cache_dir: Union[str, Path] = ".cache",
        redis_config: Optional[Dict[str, Any]] = None,
    ):
        self.backends = []

        # Memory cache (fastest)
        if enable_memory:
            self.memory_cache = MemoryCache()
            self.backends.append(self.memory_cache)

        # Redis cache (fast, distributed)
        if enable_redis:
            redis_config = redis_config or {}
            self.redis_cache = RedisCache(**redis_config)
            if self.redis_cache.available:
                self.backends.append(self.redis_cache)

        # File cache (persistent fallback)
        if enable_file:
            self.file_cache = FileCache(cache_dir)
            self.backends.append(self.file_cache)

        logger.info(
            "Multi-tier cache initialized", backends=[type(b).__name__ for b in self.backends]
        )

    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters."""
        # Create deterministic key from parameters
        key_data = json.dumps(kwargs, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """Get value from cache using fastest available backend."""
        key = self._generate_key(prefix, **kwargs)

        for backend in self.backends:
            value = backend.get(key)
            if value is not None:
                # Populate faster caches if value found in slower backend
                self._populate_faster_caches(key, value, backend)
                return value

        return None

    def set(self, prefix: str, value: Any, ttl: int = 300, **kwargs) -> None:
        """Set value in all available cache backends."""
        key = self._generate_key(prefix, **kwargs)

        for backend in self.backends:
            backend.set(key, value, ttl)

    def delete(self, prefix: str, **kwargs) -> None:
        """Delete value from all cache backends."""
        key = self._generate_key(prefix, **kwargs)

        for backend in self.backends:
            backend.delete(key)

    def clear(self, confirm: bool = False) -> None:
        """Clear all cache backends."""
        if not confirm:
            logger.warning("Cache clear called without confirmation - skipping")
            return

        for backend in self.backends:
            backend.clear()

    def _populate_faster_caches(self, key: str, value: Any, found_backend: CacheBackend) -> None:
        """Populate faster cache tiers when value found in slower tier."""
        found_index = self.backends.index(found_backend)

        # Populate all faster backends (lower indices)
        for i in range(found_index):
            self.backends[i].set(key, value)
