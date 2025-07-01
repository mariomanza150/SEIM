"""
Cache Management Service for SGII
Centralized cache management with intelligent invalidation
"""

import hashlib
import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class SGIICacheManager:
    """Centralized cache management for SGII"""

    CACHE_TIMEOUTS = {
        "user_filters": 3600,  # 1 hour
        "table_stats": 300,  # 5 minutes
        "dropdown_options": 1800,  # 30 minutes
        "user_preferences": 86400,  # 24 hours
        "dashboard_stats": 600,  # 10 minutes
        "export_data": 1800,  # 30 minutes
        "search_results": 300,  # 5 minutes
        "bulk_action_history": 3600,  # 1 hour
    }

    CACHE_PREFIXES = {
        "datatable": "sgii:dt",
        "user": "sgii:user",
        "stats": "sgii:stats",
        "filters": "sgii:filters",
        "search": "sgii:search",
        "export": "sgii:export",
        "bulk": "sgii:bulk",
    }

    @classmethod
    def generate_cache_key(cls, prefix, *args, **kwargs):
        """
        Generate a consistent cache key

        Args:
            prefix: Cache prefix from CACHE_PREFIXES
            *args: Additional arguments for the key
            **kwargs: Keyword arguments for the key
        """
        base_prefix = cls.CACHE_PREFIXES.get(prefix, prefix)

        # Create key components
        key_parts = [base_prefix]
        key_parts.extend(str(arg) for arg in args)

        # Add kwargs in sorted order for consistency
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            kwargs_str = "_".join(f"{k}={v}" for k, v in sorted_kwargs)
            key_parts.append(kwargs_str)

        # Join and hash if too long
        cache_key = ":".join(key_parts)

        # Redis has a key length limit
        if len(cache_key) > 200:
            hash_suffix = hashlib.md5(cache_key.encode()).hexdigest()[:8]
            cache_key = f"{base_prefix}:hashed:{hash_suffix}"

        return cache_key

    @classmethod
    def get_user_filter_cache_key(cls, user_id, table_name, filter_hash=None):
        """Generate cache key for user's filter preferences"""
        return cls.generate_cache_key(
            "filters", "user", user_id, table_name, hash=filter_hash
        )

    @classmethod
    def get_table_stats_cache_key(cls, table_name, user_id=None):
        """Generate cache key for table statistics"""
        return cls.generate_cache_key("stats", "table", table_name, user=user_id)

    @classmethod
    def get_search_cache_key(cls, search_term, table_name, user_id=None):
        """Generate cache key for search results"""
        search_hash = hashlib.md5(search_term.encode()).hexdigest()[:8]
        return cls.generate_cache_key("search", table_name, search_hash, user=user_id)

    @classmethod
    def cache_table_stats(cls, table_name, stats, user_id=None):
        """Cache table statistics"""
        cache_key = cls.get_table_stats_cache_key(table_name, user_id)
        timeout = cls.CACHE_TIMEOUTS["table_stats"]
        cache.set(cache_key, stats, timeout)
        logger.debug(f"Cached table stats: {cache_key}")

    @classmethod
    def get_cached_table_stats(cls, table_name, user_id=None):
        """Retrieve cached table statistics"""
        cache_key = cls.get_table_stats_cache_key(table_name, user_id)
        return cache.get(cache_key)

    @classmethod
    def cache_user_filters(cls, user_id, table_name, filters):
        """Cache user's filter preferences"""
        filter_hash = hashlib.md5(
            json.dumps(filters, sort_keys=True).encode()
        ).hexdigest()[:8]
        cache_key = cls.get_user_filter_cache_key(user_id, table_name, filter_hash)
        timeout = cls.CACHE_TIMEOUTS["user_filters"]
        cache.set(cache_key, filters, timeout)

        # Also cache the current filters for the user/table combo
        current_key = cls.get_user_filter_cache_key(user_id, table_name, "current")
        cache.set(current_key, filters, timeout)

        logger.debug(f"Cached user filters: {cache_key}")

    @classmethod
    def get_cached_user_filters(cls, user_id, table_name):
        """Retrieve cached user filters"""
        cache_key = cls.get_user_filter_cache_key(user_id, table_name, "current")
        return cache.get(cache_key)

    @classmethod
    def cache_search_results(cls, search_term, table_name, results, user_id=None):
        """Cache search results"""
        cache_key = cls.get_search_cache_key(search_term, table_name, user_id)
        timeout = cls.CACHE_TIMEOUTS["search_results"]
        cache.set(cache_key, results, timeout)
        logger.debug(f"Cached search results: {cache_key}")

    @classmethod
    def get_cached_search_results(cls, search_term, table_name, user_id=None):
        """Retrieve cached search results"""
        cache_key = cls.get_search_cache_key(search_term, table_name, user_id)
        return cache.get(cache_key)

    @classmethod
    def cache_dropdown_options(cls, dropdown_type, options):
        """Cache dropdown options (countries, programs, etc.)"""
        cache_key = cls.generate_cache_key("datatable", "dropdown", dropdown_type)
        timeout = cls.CACHE_TIMEOUTS["dropdown_options"]
        cache.set(cache_key, options, timeout)
        logger.debug(f"Cached dropdown options: {cache_key}")

    @classmethod
    def get_cached_dropdown_options(cls, dropdown_type):
        """Retrieve cached dropdown options"""
        cache_key = cls.generate_cache_key("datatable", "dropdown", dropdown_type)
        return cache.get(cache_key)

    @classmethod
    def cache_export_data(cls, export_type, filters_hash, data):
        """Cache export data"""
        cache_key = cls.generate_cache_key("export", export_type, filters_hash)
        timeout = cls.CACHE_TIMEOUTS["export_data"]
        cache.set(cache_key, data, timeout)
        logger.debug(f"Cached export data: {cache_key}")

    @classmethod
    def get_cached_export_data(cls, export_type, filters_hash):
        """Retrieve cached export data"""
        cache_key = cls.generate_cache_key("export", export_type, filters_hash)
        return cache.get(cache_key)

    @classmethod
    def invalidate_user_cache(cls, user_id):
        """Invalidate all cache entries for a specific user"""
        patterns = [
            cls.generate_cache_key("user", user_id, "*"),
            cls.generate_cache_key("filters", "user", user_id, "*"),
            cls.generate_cache_key("stats", "*", user=user_id),
            cls.generate_cache_key("search", "*", user=user_id),
        ]

        cls._invalidate_patterns(patterns)
        logger.info(f"Invalidated cache for user {user_id}")

    @classmethod
    def invalidate_table_cache(cls, table_name):
        """Invalidate cache entries for a specific table"""
        patterns = [
            cls.generate_cache_key("stats", "table", table_name, "*"),
            cls.generate_cache_key("search", table_name, "*"),
            cls.generate_cache_key("datatable", table_name, "*"),
        ]

        cls._invalidate_patterns(patterns)
        logger.info(f"Invalidated cache for table {table_name}")

    @classmethod
    def invalidate_related_caches(cls, model_name, instance_id=None):
        """
        Invalidate caches when data changes

        Args:
            model_name: Name of the model that changed
            instance_id: ID of the specific instance (optional)
        """
        # Map model names to related cache patterns
        model_cache_map = {
            "Exchange": ["exchange", "dashboard", "stats"],
            "Document": ["document", "exchange", "stats"],
            "Timeline": ["timeline", "activity", "exchange"],
            "BulkAction": ["bulk", "stats"],
        }

        related_patterns = model_cache_map.get(model_name, [])

        patterns = []
        for pattern in related_patterns:
            patterns.extend(
                [
                    cls.generate_cache_key("stats", pattern, "*"),
                    cls.generate_cache_key("datatable", pattern, "*"),
                    cls.generate_cache_key("search", pattern, "*"),
                ]
            )

        # Always invalidate general stats
        patterns.append(cls.generate_cache_key("stats", "*"))

        cls._invalidate_patterns(patterns)
        logger.info(f"Invalidated related caches for {model_name} {instance_id or ''}")

    @classmethod
    def warm_cache(cls, user_id=None):
        """
        Pre-warm frequently accessed cache entries

        Args:
            user_id: User ID for user-specific cache warming
        """
        try:
            # Import here to avoid circular imports
            from .optimization import DataTableOptimizer

            # Warm dashboard stats
            DataTableOptimizer.get_dashboard_stats(user_id)

            # Warm popular destinations
            DataTableOptimizer.get_popular_destinations(user_id=user_id)

            # Warm dropdown options
            cls._warm_dropdown_options()

            logger.info(f"Cache warmed for user {user_id or 'all'}")

        except Exception as e:
            logger.error(f"Cache warming failed: {e}")

    @classmethod
    def _warm_dropdown_options(cls):
        """Warm dropdown option caches"""
        try:
            from ..models import Exchange

            # Countries
            countries = list(
                Exchange.objects.values_list("destination_country", flat=True)
                .distinct()
                .order_by("destination_country")
            )
            cls.cache_dropdown_options("countries", countries)

            # Programs
            programs = list(
                Exchange.objects.values_list("exchange_program", flat=True)
                .distinct()
                .order_by("exchange_program")
            )
            cls.cache_dropdown_options("programs", programs)

            # Universities
            universities = list(
                Exchange.objects.values_list("destination_university", flat=True)
                .distinct()
                .order_by("destination_university")
            )
            cls.cache_dropdown_options("universities", universities)

        except Exception as e:
            logger.error(f"Failed to warm dropdown options: {e}")

    @classmethod
    def _invalidate_patterns(cls, patterns):
        """
        Invalidate cache keys matching patterns
        Note: This is a simplified implementation.
        For production, consider using Redis pattern matching or cache tagging
        """
        try:
            # For Django's default cache backend, we need to track keys manually
            # In production with Redis, you would use SCAN with patterns

            # This is a basic implementation - extend based on your cache backend
            for pattern in patterns:
                # Remove wildcards for basic key deletion
                if "*" not in pattern:
                    cache.delete(pattern)

        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")

    @classmethod
    def get_cache_stats(cls):
        """Get cache statistics for monitoring"""
        try:
            # This would need to be implemented based on your cache backend
            # For Redis, you could get memory usage, hit rates, etc.
            return {
                "status": "active",
                "backend": settings.CACHES["default"]["BACKEND"],
                "timeouts": cls.CACHE_TIMEOUTS,
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"status": "error", "error": str(e)}

    @classmethod
    def clear_all_sgii_cache(cls):
        """Clear all SGII-related cache entries"""
        try:
            patterns = [f"{prefix}:*" for prefix in cls.CACHE_PREFIXES.values()]
            cls._invalidate_patterns(patterns)
            logger.info("Cleared all SGII cache entries")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


# Signal handlers for automatic cache invalidation
@receiver(post_save, sender="exchange.Exchange")
def invalidate_exchange_cache(sender, instance, **kwargs):
    """Invalidate exchange-related cache when Exchange is saved"""
    SGIICacheManager.invalidate_related_caches("Exchange", instance.id)
    SGIICacheManager.invalidate_user_cache(
        instance.student.id if instance.student else None
    )


@receiver(post_delete, sender="exchange.Exchange")
def invalidate_exchange_cache_on_delete(sender, instance, **kwargs):
    """Invalidate exchange-related cache when Exchange is deleted"""
    SGIICacheManager.invalidate_related_caches("Exchange", instance.id)
    SGIICacheManager.invalidate_user_cache(
        instance.student.id if instance.student else None
    )


@receiver(post_save, sender="exchange.Document")
def invalidate_document_cache(sender, instance, **kwargs):
    """Invalidate document-related cache when Document is saved"""
    SGIICacheManager.invalidate_related_caches("Document", instance.id)
    if instance.exchange and instance.exchange.student:
        SGIICacheManager.invalidate_user_cache(instance.exchange.student.id)


@receiver(post_save, sender="exchange.Timeline")
def invalidate_timeline_cache(sender, instance, **kwargs):
    """Invalidate timeline-related cache when Timeline is saved"""
    SGIICacheManager.invalidate_related_caches("Timeline", instance.id)
    if instance.exchange and instance.exchange.student:
        SGIICacheManager.invalidate_user_cache(instance.exchange.student.id)


@receiver(post_save, sender="exchange.BulkAction")
def invalidate_bulk_action_cache(sender, instance, **kwargs):
    """Invalidate bulk action cache when BulkAction is saved"""
    SGIICacheManager.invalidate_related_caches("BulkAction", instance.id)
    SGIICacheManager.invalidate_user_cache(instance.performed_by.id)
