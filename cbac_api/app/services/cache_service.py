"""
Cache Service for LLM responses and other expensive operations.

Implements in-memory caching with TTL to reduce API calls and improve performance.
"""

import logging
import hashlib
import time
from typing import Any, Optional, Dict
from threading import Lock

logger = logging.getLogger(__name__)


class CacheService:
    """Simple in-memory cache with TTL support"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Singleton pattern to share cache across service instances"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = {}
                    cls._instance._timestamps = {}
                    logger.info("Cache Service initialized")
        return cls._instance
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/missing
        """
        if key not in self._cache:
            return None
        
        # Check if expired
        timestamp = self._timestamps.get(key)
        if timestamp is None:
            return None
        
        # Return value if not expired
        return self._cache.get(key)
    
    def set(self, key: str, value: str, ttl: int = 604800) -> None:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 7 days)
        """
        expiry_time = time.time() + ttl
        self._cache[key] = value
        self._timestamps[key] = expiry_time
        logger.debug(f"Cached value for key: {key[:20]}... (TTL: {ttl}s)")
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
            logger.debug(f"Deleted cache key: {key[:20]}...")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._timestamps.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self._timestamps.items()
            if expiry < current_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
            del self._timestamps[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        current_time = time.time()
        active_entries = sum(
            1 for expiry in self._timestamps.values()
            if expiry > current_time
        )
        
        return {
            "total_entries": len(self._cache),
            "active_entries": active_entries,
            "expired_entries": len(self._cache) - active_entries
        }
    
    @staticmethod
    def create_cache_key(texts: list) -> str:
        """
        Create a cache key from behavior texts.
        
        Uses MD5 hash of sorted texts for consistent key generation.
        
        Args:
            texts: List of text strings
            
        Returns:
            Cache key string
        """
        # Sort texts for consistent hashing
        sorted_texts = sorted(texts)
        combined = "".join(sorted_texts)
        
        # Create hash
        text_hash = hashlib.md5(combined.encode()).hexdigest()
        
        return f"llm_statement:{text_hash[:16]}"
