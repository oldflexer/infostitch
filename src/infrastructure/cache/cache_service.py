"""Cache Service.

In-memory TTL cache for API responses.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

from cachetools import TTLCache


class CacheService:
    """In-memory TTL cache with maxsize limit."""

    def __init__(
        self,
        maxsize: int = 1000,
        ttl: int = 3600,  # 1 hour default
    ):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            del self._cache[key]
            return True
        except KeyError:
            return False

    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()

    def __contains__(self, key: str) -> bool:
        return key in self._cache

    def __len__(self) -> int:
        return len(self._cache)

    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "maxsize": self._cache.maxsize,
            "ttl": self._cache.ttl,
        }


class AsyncCacheService:
    """Async wrapper for cache service."""

    def __init__(self, cache: CacheService):
        self._cache = cache

    async def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._cache.set(key, value)

    async def delete(self, key: str) -> bool:
        return self._cache.delete(key)

    async def clear(self) -> None:
        self._cache.clear()


# Global cache instance
_cache_instance: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        from infrastructure.config import get_settings
        settings = get_settings()
        _cache_instance = CacheService(
            maxsize=1000,
            ttl=3600,
        )
    return _cache_instance
