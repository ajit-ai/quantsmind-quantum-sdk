"""
Runtime Cache Module

This module provides cache management for the Runtime package.

Purpose
-------
Provide cache management for the QuantsMind SDK.

Responsibilities
----------------
- Manage cache entries
- Support cache policies
- Handle cache eviction
- Support cache statistics

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
time (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

from quantsmind.runtime.constants import DEFAULT_CACHE_SIZE, DEFAULT_CACHE_TTL
from quantsmind.runtime.enums import CachePolicy
from quantsmind.runtime.types import CacheEntry, CacheKey, CacheValue

logger = logging.getLogger(__name__)


class Cache:
    """Concrete implementation of a cache.

    This class provides cache management capabilities.

    Attributes:
        _cache: Cache storage
        _policy: Cache policy
        _max_size: Maximum cache size
        _ttl: Time to live
        _access_times: Access times for LRU
        _access_counts: Access counts for LFU
        _lock: Thread lock

    Example:
        >>> cache = Cache(policy=CachePolicy.LRU)
        >>> cache.set("key", "value")
        >>> value = cache.get("key")
    """

    def __init__(
        self,
        policy: CachePolicy = CachePolicy.LRU,
        max_size: int = DEFAULT_CACHE_SIZE,
        ttl: int = DEFAULT_CACHE_TTL,
    ) -> None:
        """Initialize a Cache.

        Args:
            policy: Cache policy
            max_size: Maximum cache size
            ttl: Time to live in seconds

        Example:
            >>> cache = Cache(policy=CachePolicy.LRU)
        """
        self._cache: dict[CacheKey, CacheEntry] = {}
        self._policy = policy
        self._max_size = max_size
        self._ttl = ttl
        self._access_times: dict[CacheKey, float] = {}
        self._access_counts: dict[CacheKey, int] = {}
        self._lock = threading.Lock()
        logger.debug(f"Created cache with policy={policy.value}, max_size={max_size}")

    @property
    def size(self) -> int:
        """Get the current cache size.

        Returns:
            Current cache size

        Example:
            >>> print(f"Cache size: {cache.size}")
        """
        with self._lock:
            return len(self._cache)

    @property
    def policy(self) -> CachePolicy:
        """Get the cache policy.

        Returns:
            Cache policy

        Example:
            >>> print(f"Policy: {cache.policy}")
        """
        return self._policy

    def set(self, key: CacheKey, value: CacheValue, ttl: int | None = None) -> None:
        """Set a cache entry.

        Args:
            key: Cache key
            value: Cache value
            ttl: Custom TTL

        Example:
            >>> cache.set("key", "value")
        """
        with self._lock:
            entry_ttl = ttl or self._ttl
            self._cache[key] = (value, time.time() + entry_ttl)
            self._access_times[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            
            # Evict if necessary
            if len(self._cache) > self._max_size:
                self._evict()

    def get(self, key: CacheKey) -> CacheValue | None:
        """Get a cache entry.

        Args:
            key: Cache key

        Returns:
            Cache value or None

        Example:
            >>> value = cache.get("key")
        """
        with self._lock:
            if key not in self._cache:
                return None

            value, expiry = self._cache[key]
            
            # Check TTL
            if time.time() > expiry:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                if key in self._access_counts:
                    del self._access_counts[key]
                return None

            # Update access tracking
            self._access_times[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            
            return value

    def has(self, key: CacheKey) -> bool:
        """Check if a key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise

        Example:
            >>> if cache.has("key"):
            ...     print("Key exists")
        """
        return self.get(key) is not None

    def delete(self, key: CacheKey) -> bool:
        """Delete a cache entry.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise

        Example:
            >>> deleted = cache.delete("key")
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                if key in self._access_counts:
                    del self._access_counts[key]
                return True
        return False

    def clear(self) -> None:
        """Clear the cache.

        Example:
            >>> cache.clear()
        """
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._access_counts.clear()
        logger.debug("Cleared cache")

    def _evict(self) -> None:
        """Evict an entry based on policy.

        Example:
            >>> cache._evict()
        """
        if not self._cache:
            return

        if self._policy == CachePolicy.LRU:
            self._evict_lru()
        elif self._policy == CachePolicy.LFU:
            self._evict_lfu()
        elif self._policy == CachePolicy.FIFO:
            self._evict_fifo()
        elif self._policy == CachePolicy.TTL:
            self._evict_ttl()

    def _evict_lru(self) -> None:
        """Evict least recently used entry.

        Example:
            >>> cache._evict_lru()
        """
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self.delete(lru_key)

    def _evict_lfu(self) -> None:
        """Evict least frequently used entry.

        Example:
            >>> cache._evict_lfu()
        """
        if not self._access_counts:
            return
        
        lfu_key = min(self._access_counts.keys(), key=lambda k: self._access_counts[k])
        self.delete(lfu_key)

    def _evict_fifo(self) -> None:
        """Evict first entry (simplified).

        Example:
            >>> cache._evict_fifo()
        """
        if self._cache:
            first_key = next(iter(self._cache))
            self.delete(first_key)

    def _evict_ttl(self) -> None:
        """Evict expired entries.

        Example:
            >>> cache._evict_ttl()
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time > expiry
        ]
        for key in expired_keys:
            self.delete(key)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics

        Example:
            >>> stats = cache.get_stats()
        """
        with self._lock:
            return {
                "size": self.size,
                "max_size": self._max_size,
                "policy": self._policy.value,
                "ttl": self._ttl,
                "hit_rate": 0.0,  # Simplified
            }


# Export
__all__ = [
    "Cache",
]
