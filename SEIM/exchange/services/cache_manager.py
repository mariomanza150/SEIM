"""
Cache management for SGII.
Provides centralized caching strategies and utilities.
"""
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional, List


class CacheManager:
    """Centralized cache management for SGII."""
    
    # Cache timeouts in seconds
    TIMEOUTS = {
        'university_list': 86400,      # 24 hours
        'country_list': 86400,         # 24 hours
        'exchange_stats': 3600,        # 1 hour
        'user_permissions': 1800,      # 30 minutes
        'document_types': 86400,       # 24 hours
        'exchange_detail': 300,        # 5 minutes
        'exchange_list': 600,          # 10 minutes
        'analytics_data': 7200,        # 2 hours
        'report_data': 3600,          # 1 hour
    }
    
    @classmethod
    def get_or_set(cls, key: str, callable_func: Callable, timeout: Optional[int] = None) -> Any:
        """Get from cache or set if not exists."""
        if timeout is None:
            # Extract key prefix to determine timeout
            key_prefix = key.split(':')[0]
            timeout = cls.TIMEOUTS.get(key_prefix, 300)  # Default 5 minutes
            
        value = cache.get(key)
        if value is None:
            value = callable_func()
            cache.set(key, value, timeout)
        return value
    
    @classmethod
    def delete(cls, key: str) -> None:
        """Delete a specific cache key."""
        cache.delete(key)
    
    @classmethod
    def delete_many(cls, keys: List[str]) -> None:
        """Delete multiple cache keys."""
        cache.delete_many(keys)
    
    @classmethod
    def invalidate_pattern(cls, pattern: str) -> None:
        """Invalidate all cache keys matching pattern."""
        if hasattr(cache, '_cache') and hasattr(cache._cache, 'delete_pattern'):
            # For Redis backend
            cache._cache.delete_pattern(f"*{pattern}*")
        else:
            # For other backends, we'd need to track keys
            # This is a limitation of non-Redis backends
            pass
    
    @classmethod
    def invalidate_exchange(cls, exchange_id: int) -> None:
        """Invalidate all caches related to an exchange."""
        keys = [
            f'exchange_detail:{exchange_id}',
            f'exchange_documents:{exchange_id}',
            f'exchange_timeline:{exchange_id}',
            f'exchange_comments:{exchange_id}',
            'exchange_stats',
            'exchange_list:*',  # This would need pattern matching
        ]
        cls.delete_many([k for k in keys if ':*' not in k])
        
        # For pattern-based keys
        cls.invalidate_pattern(f'exchange_list')
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> None:
        """Invalidate all caches related to a user."""
        keys = [
            f'user_permissions:{user_id}',
            f'user_exchanges:{user_id}',
            f'user_profile:{user_id}',
        ]
        cls.delete_many(keys)
    
    @classmethod
    def make_key(cls, prefix: str, params: dict) -> str:
        """Generate cache key from prefix and parameters."""
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}:{param_hash}"
    
    @classmethod
    def clear_all(cls) -> None:
        """Clear all cache. Use with caution!"""
        cache.clear()


def cache_view(timeout: Optional[int] = None, key_prefix: Optional[str] = None):
    """
    Decorator to cache view responses.
    
    Usage:
        @cache_view(timeout=3600, key_prefix='exchange_list')
        def my_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key
            if key_prefix:
                cache_key = CacheManager.make_key(
                    key_prefix,
                    {
                        'path': request.path,
                        'query': dict(request.GET),
                        'user': request.user.id if request.user.is_authenticated else None,
                        'args': args,
                        'kwargs': kwargs,
                    }
                )
            else:
                cache_key = CacheManager.make_key(
                    func.__name__,
                    {
                        'path': request.path,
                        'query': dict(request.GET),
                    }
                )
            
            # Check cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Call view
            response = func(request, *args, **kwargs)
            
            # Cache response if successful
            if hasattr(response, 'status_code') and 200 <= response.status_code < 300:
                cache.set(cache_key, response, timeout or 300)
            
            return response
        return wrapper
    return decorator


def cache_method(timeout: Optional[int] = None):
    """
    Decorator to cache method results.
    
    Usage:
        @cache_method(timeout=3600)
        def expensive_calculation(self, param):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key
            cache_key = CacheManager.make_key(
                f"{self.__class__.__name__}.{func.__name__}",
                {
                    'instance_id': getattr(self, 'id', id(self)),
                    'args': args,
                    'kwargs': kwargs,
                }
            )
            
            # Try to get from cache
            return CacheManager.get_or_set(
                cache_key,
                lambda: func(self, *args, **kwargs),
                timeout
            )
        return wrapper
    return decorator


# Example usage functions

def get_cached_universities():
    """Get list of universities with caching."""
    from exchange.models import University
    
    return CacheManager.get_or_set(
        'university_list',
        lambda: list(University.objects.values('id', 'name', 'country', 'code'))
    )


def get_cached_countries():
    """Get list of countries with caching."""
    from django_countries import countries
    
    return CacheManager.get_or_set(
        'country_list',
        lambda: list(countries)
    )


def get_cached_exchange_stats():
    """Get exchange statistics with caching."""
    from exchange.services.optimized_queries import OptimizedQueries
    
    return CacheManager.get_or_set(
        'exchange_stats',
        lambda: OptimizedQueries.get_exchange_statistics()
    )


def get_cached_document_types():
    """Get document types with caching."""
    from exchange.models import DocumentType
    
    return CacheManager.get_or_set(
        'document_types',
        lambda: list(DocumentType.objects.values('id', 'name', 'required', 'category'))
    )
