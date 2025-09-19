"""Local Redis caching for performance optimization."""

import json
import hashlib
from typing import Any, Optional, Dict
from datetime import timedelta
import os
from loguru import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")


class CacheManager:
    """Local Redis cache manager for AgentAI."""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache
        
        if REDIS_AVAILABLE:
            try:
                redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info(f"Connected to Redis at {redis_url}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using memory cache")
                self.redis_client = None
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data."""
        data_str = json.dumps(data, sort_keys=True) if isinstance(data, dict) else str(data)
        hash_key = hashlib.md5(data_str.encode()).hexdigest()[:12]
        return f"agentai:{prefix}:{hash_key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            if self.redis_client:
                return self.redis_client.setex(key, ttl, json.dumps(value))
            else:
                self.memory_cache[key] = value
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                return self.memory_cache.pop(key, None) is not None
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def cache_analysis(self, requirements: Dict[str, Any], analysis: str) -> str:
        """Cache AI analysis results."""
        cache_key = self._generate_key("analysis", requirements)
        await self.set(cache_key, analysis, ttl=7200)  # 2 hours
        return cache_key
    
    async def get_cached_analysis(self, requirements: Dict[str, Any]) -> Optional[str]:
        """Get cached analysis if available."""
        cache_key = self._generate_key("analysis", requirements)
        return await self.get(cache_key)
    
    async def cache_code_generation(self, project_data: Dict[str, Any], code: str) -> str:
        """Cache code generation results."""
        cache_key = self._generate_key("code", project_data)
        await self.set(cache_key, code, ttl=3600)  # 1 hour
        return cache_key
    
    async def get_cached_code(self, project_data: Dict[str, Any]) -> Optional[str]:
        """Get cached code generation if available."""
        cache_key = self._generate_key("code", project_data)
        return await self.get(cache_key)
    
    async def cache_project_metadata(self, project_id: str, metadata: Dict[str, Any]) -> bool:
        """Cache project metadata."""
        cache_key = f"agentai:project:{project_id}"
        return await self.set(cache_key, metadata, ttl=1800)  # 30 minutes
    
    async def get_project_metadata(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get cached project metadata."""
        cache_key = f"agentai:project:{project_id}"
        return await self.get(cache_key)
    
    async def clear_project_cache(self, project_id: str) -> bool:
        """Clear all cache entries for a project."""
        try:
            if self.redis_client:
                # Get all keys matching pattern
                pattern = f"agentai:*{project_id}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    return bool(self.redis_client.delete(*keys))
            else:
                # Clear from memory cache
                keys_to_delete = [k for k in self.memory_cache.keys() if project_id in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    "type": "redis",
                    "connected": True,
                    "keys": info.get('db0', {}).get('keys', 0),
                    "memory_usage": info.get('used_memory_human', 'N/A'),
                    "hits": info.get('keyspace_hits', 0),
                    "misses": info.get('keyspace_misses', 0)
                }
            else:
                return {
                    "type": "memory",
                    "connected": True,
                    "keys": len(self.memory_cache),
                    "memory_usage": "N/A",
                    "hits": 0,
                    "misses": 0
                }
        except Exception as e:
            return {
                "type": "error",
                "connected": False,
                "error": str(e)
            }


# Global cache instance
cache_manager = CacheManager()