"""
Caching system for TermoApp with Redis support and in-memory fallback.
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict, List
from functools import wraps
import os
try:
    from .logger import logger, log_with_context
except ImportError:
    from logger import logger, log_with_context

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")

class CacheManager:
    """Cache manager with Redis and in-memory fallback."""
    
    def __init__(self, redis_url: str = None, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self._memory_cache = {}
        self._redis_client = None
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self._redis_client = redis.from_url(redis_url) # pyright: ignore[reportPossiblyUnboundVariable]
                # Test connection
                self._redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache.")
                self._redis_client = None
        else:
            logger.info("Using in-memory cache")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments."""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            key_parts.append(str(arg))
        
        # Add keyword arguments (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if self._redis_client:
                value = self._redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                if key in self._memory_cache:
                    item = self._memory_cache[key]
                    if time.time() < item['expires_at']:
                        return item['value']
                    else:
                        del self._memory_cache[key]
        except Exception as e:
            log_with_context(logger, "ERROR", f"Cache get error: {e}", key=key)
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            
            if self._redis_client:
                return self._redis_client.setex(key, ttl, json.dumps(value))
            else:
                self._memory_cache[key] = {
                    'value': value,
                    'expires_at': time.time() + ttl
                }
                return True
        except Exception as e:
            log_with_context(logger, "ERROR", f"Cache set error: {e}", key=key)
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if self._redis_client:
                return bool(self._redis_client.delete(key))
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    return True
        except Exception as e:
            log_with_context(logger, "ERROR", f"Cache delete error: {e}", key=key)
        
        return False
    
    def clear(self, pattern: str = None) -> bool:
        """Clear cache entries matching pattern."""
        try:
            if self._redis_client and pattern:
                keys = self._redis_client.keys(pattern)
                if keys:
                    return bool(self._redis_client.delete(*keys))
            else:
                if pattern:
                    # Simple pattern matching for memory cache
                    keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
                    for key in keys_to_delete:
                        del self._memory_cache[key]
                else:
                    self._memory_cache.clear()
                return True
        except Exception as e:
            log_with_context(logger, "ERROR", f"Cache clear error: {e}", pattern=pattern)
        
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if self._redis_client:
                return bool(self._redis_client.exists(key))
            else:
                if key in self._memory_cache:
                    item = self._memory_cache[key]
                    if time.time() < item['expires_at']:
                        return True
                    else:
                        del self._memory_cache[key]
        except Exception as e:
            log_with_context(logger, "ERROR", f"Cache exists error: {e}", key=key)
        
        return False

# Global cache instance
cache_manager = CacheManager(
    redis_url=os.getenv('REDIS_URL'),
    default_ttl=int(os.getenv('CACHE_TTL', 3600))
)

def cached(prefix: str, ttl: int = None, key_generator: callable = None):
    """
    Decorator for caching function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_generator: Custom key generation function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                log_with_context(logger, "DEBUG", "Cache hit", 
                               function=func.__name__, cache_key=cache_key)
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            log_with_context(logger, "DEBUG", "Cache miss - stored result", 
                           function=func.__name__, cache_key=cache_key)
            
            return result
        return wrapper
    return decorator

# Cache-specific functions for common operations
class GoogleSheetsCache:
    """Cache operations for Google Sheets data."""
    
    @staticmethod
    @cached("sheets_metadata", ttl=300)  # 5 minutes
    def get_sheet_metadata(sheet_id: str) -> List[str]:
        """Cache sheet metadata."""
        try:
            from .utils import SheetsHandler
        except ImportError:
            from utils import SheetsHandler
        sh = SheetsHandler(sheet_id)
        return sh.obter_metadados()
    
    @staticmethod
    @cached("sheets_search", ttl=600)  # 10 minutes
    def search_assets(sheet_id: str, search_term: str, sheet_names: List[str]) -> List[tuple]:
        """Cache asset search results."""
        try:
            from .utils import SheetsHandler
        except ImportError:
            from utils import SheetsHandler
        sh = SheetsHandler(sheet_id)
        return sh.buscar_palavra_em_abas(search_term, sheet_names)
    
    @staticmethod
    def invalidate_sheet_cache(sheet_id: str):
        """Invalidate all cache entries for a specific sheet."""
        cache_manager.clear(f"sheets_*{sheet_id}*")

class TemplateCache:
    """Cache operations for document templates."""
    
    @staticmethod
    @cached("template_list", ttl=3600)  # 1 hour
    def get_available_templates() -> Dict[str, str]:
        """Cache available templates."""
        try:
            from .utils import modelos
        except ImportError:
            from utils import modelos
        return modelos
    
    @staticmethod
    def invalidate_template_cache():
        """Invalidate template cache."""
        cache_manager.clear("template_*")

class DocumentCache:
    """Cache operations for generated documents."""
    
    @staticmethod
    @cached("doc_generation", ttl=1800)  # 30 minutes
    def get_document_data(user_data: dict, assets: list) -> dict:
        """Cache document generation data."""
        # This would cache the processed document data
        return {
            'user_data': user_data,
            'assets': assets,
            'processed_at': time.time()
        }
    
    @staticmethod
    def invalidate_user_documents(user_name: str):
        """Invalidate cache for a specific user's documents."""
        cache_manager.clear(f"doc_generation*{user_name}*")

# Utility functions for cache management
def clear_all_caches():
    """Clear all application caches."""
    cache_manager.clear()
    logger.info("All caches cleared")

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    if cache_manager._redis_client:
        info = cache_manager._redis_client.info()
        return {
            'type': 'redis',
            'connected_clients': info.get('connected_clients', 0),
            'used_memory': info.get('used_memory_human', '0B'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0)
        }
    else:
        return {
            'type': 'memory',
            'cache_size': len(cache_manager._memory_cache),
            'memory_usage': 'N/A'
        } 