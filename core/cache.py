"""
SEIM Cache Management
Provides caching utilities for API responses, database queries, and static content
"""

import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework import status
from rest_framework.response import Response


class CacheManager:
    """Advanced cache management for SEIM application"""

    # Cache prefixes for different types of data
    PREFIXES = {
        "api_response": "api_resp",
        "user_data": "user",
        "program_data": "program",
        "application_data": "app",
        "document_data": "doc",
        "notification_data": "notif",
        "analytics_data": "analytics",
        "static_content": "static",
    }

    # Default cache timeouts (in seconds)
    TIMEOUTS = {
        "api_response": 300,  # 5 minutes
        "user_data": 600,  # 10 minutes
        "program_data": 1800,  # 30 minutes
        "application_data": 900,  # 15 minutes
        "document_data": 1200,  # 20 minutes
        "notification_data": 300,  # 5 minutes
        "analytics_data": 3600,  # 1 hour
        "static_content": 7200,  # 2 hours
    }

    @classmethod
    def get_cache_key(cls, prefix: str, identifier: str, version: str = "v1") -> str:
        """Generate a consistent cache key"""
        key_parts = [cls.PREFIXES.get(prefix, prefix), version, identifier]
        return ":".join(key_parts)

    @classmethod
    def get_cache_timeout(cls, cache_type: str) -> int:
        """Get cache timeout for a specific type"""
        return cls.TIMEOUTS.get(cache_type, 300)

    @classmethod
    def set_cache(
        cls,
        key: str,
        data: Any,
        timeout: int | None = None,
        cache_type: str = "api_response",
    ) -> bool:
        """Set cache with compression and error handling"""
        try:
            if timeout is None:
                timeout = cls.get_cache_timeout(cache_type)

            # Handle UUID serialization
            def serialize_uuid(obj):
                if hasattr(obj, "hex"):  # UUID objects
                    return str(obj)
                return obj

            # Convert data to JSON-serializable format
            if isinstance(data, (dict, list)):
                # Convert UUIDs to strings
                if isinstance(data, dict):
                    data = {k: serialize_uuid(v) for k, v in data.items()}
                elif isinstance(data, list):
                    data = [serialize_uuid(item) for item in data]

                # Compress data if it's large
                if len(str(data)) > 1000:
                    data = json.dumps(data, separators=(",", ":"), default=str)

            return cache.set(key, data, timeout)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    @classmethod
    def get_cache(cls, key: str, default: Any = None) -> Any:
        """Get cache with error handling and decompression"""
        try:
            data = cache.get(key, default)

            # Handle None values
            if data is None:
                return default

            # Decompress data if it's a string
            if isinstance(data, str) and (data.startswith("{") or data.startswith("[")):
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    pass

            return data
        except Exception as e:
            print(f"Cache get error: {e}")
            return default

    @classmethod
    def delete_cache(cls, key: str) -> bool:
        """Delete cache with error handling"""
        try:
            return cache.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    @classmethod
    def clear_pattern(cls, pattern: str) -> int:
        """Clear cache entries matching a pattern"""
        try:
            # This is a simplified version - in production, you might want to use Redis SCAN
            keys = cache.keys(pattern)
            deleted = 0
            for key in keys:
                if cache.delete(key):
                    deleted += 1
            return deleted
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0

    @classmethod
    def get_cache_stats(cls) -> dict[str, Any]:
        """Get cache statistics"""
        try:
            return {
                "cache_backend": settings.CACHES["default"]["BACKEND"],
                "cache_location": settings.CACHES["default"].get("LOCATION", "N/A"),
                "cache_timeout": settings.CACHES["default"].get("TIMEOUT", "N/A"),
                "cache_options": settings.CACHES["default"].get("OPTIONS", {}),
            }
        except Exception as e:
            return {"error": str(e)}


def cache_api_response(
    timeout: int | None = None,
    key_func: Callable | None = None,
    cache_type: str = "api_response",
) -> Callable:
    """
    Decorator to cache API responses

    Args:
        timeout: Cache timeout in seconds
        key_func: Function to generate cache key
        cache_type: Type of cache for timeout determination
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [
                    func.__name__,
                    hashlib.md5(str(args).encode()).hexdigest()[:8],
                    hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()[:8],
                ]
                cache_key = CacheManager.get_cache_key(cache_type, ":".join(key_parts))

            # Try to get from cache
            cached_response = CacheManager.get_cache(cache_key)
            if cached_response is not None:
                return Response(cached_response, status=status.HTTP_200_OK)

            # Execute function and cache result
            response = func(*args, **kwargs)

            if hasattr(response, "data") and response.status_code == 200:
                CacheManager.set_cache(cache_key, response.data, timeout, cache_type)

            return response

        return wrapper

    return decorator


def cache_user_data(timeout: int | None = None) -> Callable:
    """Decorator to cache user-specific data"""

    def decorator(func):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            if not request.user.is_authenticated:
                return func(request, *args, **kwargs)

            # Generate user-specific cache key
            user_id = request.user.id
            key_parts = [
                func.__name__,
                str(user_id),
                hashlib.md5(str(args).encode()).hexdigest()[:8],
            ]
            cache_key = CacheManager.get_cache_key("user_data", ":".join(key_parts))

            # Try to get from cache
            cached_data = CacheManager.get_cache(cache_key)
            if cached_data is not None:
                return Response(cached_data, status=status.HTTP_200_OK)

            # Execute function and cache result
            response = func(request, *args, **kwargs)

            if hasattr(response, "data") and response.status_code == 200:
                CacheManager.set_cache(cache_key, response.data, timeout, "user_data")

            return response

        return wrapper

    return decorator


def invalidate_cache_pattern(pattern: str) -> callable:
    """Decorator to invalidate cache after function execution"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Invalidate cache
            CacheManager.clear_pattern(pattern)

            return result

        return wrapper

    return decorator


def cache_page_with_vary(timeout: int = 300, key_prefix: str = "page") -> callable:
    """Enhanced page caching with cookie variation"""

    def decorator(func):
        @method_decorator(cache_page(timeout, key_prefix=key_prefix))
        @method_decorator(vary_on_cookie)
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def cache_page_with_auth(timeout: int = 300, key_prefix: str = "auth_page"):
    """Decorator to cache pages only for authenticated users (function-based views only)."""
    from functools import wraps

    from django.views.decorators.cache import cache_page

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request, "user") or not request.user.is_authenticated:  # type: ignore[attr-defined]
                return view_func(request, *args, **kwargs)
            # Use cache_page directly for function-based views
            return cache_page(timeout, key_prefix=key_prefix)(view_func)(
                request, *args, **kwargs
            )

        return _wrapped_view

    return decorator


class APICacheMiddleware:
    """Middleware for automatic API response caching"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Only cache GET requests to API endpoints
        if request.method == "GET" and request.path.startswith("/api/"):
            # Generate cache key
            cache_key = self._generate_cache_key(request)

            # Try to get from cache
            cached_response = CacheManager.get_cache(cache_key)
            if cached_response is not None:
                return HttpResponse(
                    json.dumps(cached_response).encode("utf-8"),
                    content_type="application/json",
                    status=200,
                )

        response = self.get_response(request)

        # Cache successful JSON GET API responses only (skip CSV, Excel, file streams, etc.)
        if (
            request.method == "GET"
            and request.path.startswith("/api/")
            and response.status_code == 200
        ):
            ctype = (response.get("Content-Type") or "").lower()
            if "application/json" in ctype:
                try:
                    data = json.loads(response.content)
                    cache_key = self._generate_cache_key(request)
                    CacheManager.set_cache(cache_key, data, cache_type="api_response")
                except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                    pass

        return response

    def _generate_cache_key(self, request: HttpRequest) -> str:
        """Generate cache key for request"""
        key_parts = [
            "api_middleware",
            request.path,
            hashlib.md5(str(request.GET).encode()).hexdigest()[:8],
        ]

        # Include user ID if authenticated
        if hasattr(request, "user") and request.user.is_authenticated:  # type: ignore[attr-defined]
            key_parts.append(f"user_{request.user.id}")  # type: ignore[attr-defined]

        return CacheManager.get_cache_key("api_response", ":".join(key_parts))


class CachePerformanceMonitor:
    """Monitor cache performance and statistics"""

    def __init__(self):
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "errors": 0}

    def record_hit(self):
        """Record a cache hit"""
        self.stats["hits"] += 1

    def record_miss(self):
        """Record a cache miss"""
        self.stats["misses"] += 1

    def record_set(self):
        """Record a cache set"""
        self.stats["sets"] += 1

    def record_delete(self):
        """Record a cache delete"""
        self.stats["deletes"] += 1

    def record_error(self):
        """Record a cache error"""
        self.stats["errors"] += 1

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.stats["hits"] + self.stats["misses"]
        return (self.stats["hits"] / total * 100) if total > 0 else 0

    def get_stats(self) -> dict[str, Any]:
        """Get complete statistics"""
        return {
            **self.stats,
            "hit_rate": self.get_hit_rate(),
            "total_operations": sum(self.stats.values()),
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = dict.fromkeys(self.stats, 0)


# Global cache performance monitor
cache_monitor = CachePerformanceMonitor()


# Utility functions for common caching patterns
def cache_program_data(
    program_id: int, timeout: int | None = None
) -> dict[str, Any]:
    """Cache program data"""
    cache_key = CacheManager.get_cache_key("program_data", f"program_{program_id}")
    return CacheManager.get_cache(cache_key, {})


def set_program_cache(
    program_id: int, data: dict[str, Any], timeout: int | None = None
) -> bool:
    """Set program data cache"""
    cache_key = CacheManager.get_cache_key("program_data", f"program_{program_id}")
    return CacheManager.set_cache(cache_key, data, timeout, "program_data")


def cache_application_data(
    application_id: int, timeout: int | None = None
) -> dict[str, Any]:
    """Cache application data"""
    cache_key = CacheManager.get_cache_key("application_data", f"app_{application_id}")
    return CacheManager.get_cache(cache_key, {})


def set_application_cache(
    application_id: int, data: dict[str, Any], timeout: int | None = None
) -> bool:
    """Set application data cache"""
    cache_key = CacheManager.get_cache_key("application_data", f"app_{application_id}")
    return CacheManager.set_cache(cache_key, data, timeout, "application_data")


def invalidate_user_cache(user_id: int) -> bool:
    """Invalidate all cache entries for a specific user"""
    pattern = f"user:*user_{user_id}*"
    return CacheManager.clear_pattern(pattern) > 0


def invalidate_program_cache(program_id: int) -> bool:
    """Invalidate cache for a specific program"""
    cache_key = CacheManager.get_cache_key("program_data", f"program_{program_id}")
    return CacheManager.delete_cache(cache_key)


def invalidate_application_cache(application_id: int) -> bool:
    """Invalidate cache for a specific application"""
    cache_key = CacheManager.get_cache_key("application_data", f"app_{application_id}")
    return CacheManager.delete_cache(cache_key)


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key for analytics metrics."""
    import hashlib

    key_base = prefix + ":" + ":".join([str(arg) for arg in args])
    if kwargs:
        key_base += ":" + ":".join([f"{k}={v}" for k, v in sorted(kwargs.items())])
    return hashlib.md5(key_base.encode()).hexdigest()


def cache_analytics(timeout: int = 1800):
    """Decorator to cache analytics results."""

    def decorator(func):
        from functools import wraps

        from django.core.cache import cache

        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(
                f"analytics:{func.__name__}", *args, **kwargs
            )
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator
