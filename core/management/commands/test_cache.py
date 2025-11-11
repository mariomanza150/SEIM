import time

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand

from core.cache import CacheManager, generate_cache_key


class Command(BaseCommand):
    help = "Test and monitor the caching system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Run cache performance tests",
        )
        parser.add_argument(
            "--test-set-get",
            action="store_true",
            help="Test cache set/get operations",
        )
        parser.add_argument(
            "--test-clear",
            action="store_true",
            help="Test cache clear operation",
        )
        parser.add_argument(
            "--test-performance",
            action="store_true",
            help="Test cache performance",
        )
        parser.add_argument(
            "--status",
            action="store_true",
            help="Show cache status and configuration",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all cache",
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="Show cache statistics",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose output",
        )

    def handle(self, *args, **options):
        if options["status"]:
            self.show_cache_status()
        elif options["test"] or options["test_set_get"] or options["test_clear"] or options["test_performance"]:
            self.run_cache_tests()
        elif options["clear"]:
            self.clear_cache()
        elif options["stats"]:
            self.show_cache_stats()
        else:
            self.stdout.write("Use --help to see available options")

    def show_cache_status(self):
        """Show cache configuration and status."""
        self.stdout.write("🔍 Cache Configuration Status")
        self.stdout.write("=" * 50)

        # Show cache backends
        self.stdout.write("\n📋 Cache Backends:")
        for alias, config in settings.CACHES.items():
            self.stdout.write(f'  {alias}: {config["BACKEND"]}')
            self.stdout.write(f'    Location: {config.get("LOCATION", "N/A")}')
            self.stdout.write(f'    Timeout: {config.get("TIMEOUT", "default")}s')
            self.stdout.write(f'    Key Prefix: {config.get("KEY_PREFIX", "none")}')

        # Show session configuration
        self.stdout.write("\n🔐 Session Configuration:")
        self.stdout.write(f'  Engine: {getattr(settings, "SESSION_ENGINE", "default")}')
        self.stdout.write(
            f'  Cache Alias: {getattr(settings, "SESSION_CACHE_ALIAS", "default")}'
        )
        self.stdout.write(
            f'  Cookie Age: {getattr(settings, "SESSION_COOKIE_AGE", "default")}s'
        )

        # Show middleware configuration
        self.stdout.write("\n⚙️ Cache Middleware:")
        if "django.middleware.cache.UpdateCacheMiddleware" in settings.MIDDLEWARE:
            self.stdout.write("  ✅ UpdateCacheMiddleware: Enabled")
        else:
            self.stdout.write("  ❌ UpdateCacheMiddleware: Disabled")

        if "django.middleware.cache.FetchFromCacheMiddleware" in settings.MIDDLEWARE:
            self.stdout.write("  ✅ FetchFromCacheMiddleware: Enabled")
        else:
            self.stdout.write("  ❌ FetchFromCacheMiddleware: Disabled")

        # Show cache timeouts
        self.stdout.write("\n⏱️ Cache Timeouts:")
        for name, timeout in CacheManager.TIMEOUTS.items():
            self.stdout.write(f"  {name}: {timeout}s")

    def run_cache_tests(self):
        """Run cache performance tests."""
        self.stdout.write("🧪 Running Cache Performance Tests")
        self.stdout.write("=" * 50)

        # Test 1: Basic set/get operations
        self.stdout.write("\n📝 Test 1: Basic Set/Get Operations")
        start_time = time.time()

        test_data = {
            "string": "test_string",
            "number": 42,
            "list": [1, 2, 3, 4, 5],
            "dict": {"key": "value", "nested": {"data": "test"}},
            "boolean": True,
            "null": None,
        }

        for key, value in test_data.items():
            cache_key = f"test_basic_{key}"
            cache.set(cache_key, value, 60)
            retrieved = cache.get(cache_key)

            if retrieved == value:
                self.stdout.write(f"  ✅ {key}: PASS")
            else:
                self.stdout.write(
                    f"  ❌ {key}: FAIL (expected {value}, got {retrieved})"
                )

        basic_time = time.time() - start_time
        self.stdout.write(f"  ⏱️ Basic operations completed in {basic_time:.4f}s")

        # Test 2: Cache key generation
        self.stdout.write("\n🔑 Test 2: Cache Key Generation")
        start_time = time.time()

        test_keys = [
            generate_cache_key("test", "user", 123, role="admin"),
            generate_cache_key("api", "programs", user_id=456, status="active"),
            generate_cache_key("analytics", "dashboard", date="2025-01-01"),
        ]

        for i, key in enumerate(test_keys):
            cache.set(key, f"test_value_{i}", 60)
            retrieved = cache.get(key)
            if retrieved == f"test_value_{i}":
                self.stdout.write(f"  ✅ Key {i+1}: PASS")
            else:
                self.stdout.write(f"  ❌ Key {i+1}: FAIL")

        key_time = time.time() - start_time
        self.stdout.write(f"  ⏱️ Key generation completed in {key_time:.4f}s")

        # Test 3: Bulk operations
        self.stdout.write("\n📦 Test 3: Bulk Operations")
        start_time = time.time()

        bulk_data = {}
        for i in range(100):
            bulk_data[f"bulk_key_{i}"] = f"bulk_value_{i}"

        # Set multiple keys
        cache.set_many(bulk_data, 60)

        # Get multiple keys
        retrieved_bulk = cache.get_many(bulk_data.keys())

        success_count = sum(
            1 for k, v in bulk_data.items() if retrieved_bulk.get(k) == v
        )
        self.stdout.write(f"  ✅ Bulk operations: {success_count}/100 keys successful")

        bulk_time = time.time() - start_time
        self.stdout.write(f"  ⏱️ Bulk operations completed in {bulk_time:.4f}s")

        # Test 4: Cache invalidation
        self.stdout.write("\n🗑️ Test 4: Cache Invalidation")
        start_time = time.time()

        # Set some test data
        for i in range(10):
            cache.set(f"invalidate_test_{i}", f"value_{i}", 300)

        # Verify data exists
        pre_invalidate = sum(
            1 for i in range(10) if cache.get(f"invalidate_test_{i}") is not None
        )
        self.stdout.write(f"  📊 Before invalidation: {pre_invalidate}/10 keys exist")

        # Invalidate pattern
        from core.cache import invalidate_cache_pattern

        invalidate_cache_pattern("invalidate_test")

        # Verify data is gone
        post_invalidate = sum(
            1 for i in range(10) if cache.get(f"invalidate_test_{i}") is not None
        )
        self.stdout.write(f"  📊 After invalidation: {post_invalidate}/10 keys exist")

        if post_invalidate == 0:
            self.stdout.write("  ✅ Invalidation: PASS")
        else:
            self.stdout.write("  ❌ Invalidation: FAIL")

        invalidate_time = time.time() - start_time
        self.stdout.write(f"  ⏱️ Invalidation completed in {invalidate_time:.4f}s")

        # Summary
        total_time = basic_time + key_time + bulk_time + invalidate_time
        self.stdout.write("\n📊 Test Summary:")
        self.stdout.write(f"  Total time: {total_time:.4f}s")
        self.stdout.write("Cache test completed")
        self.stdout.write(f"  Average operation time: {total_time/4:.4f}s")

    def clear_cache(self):
        """Clear all cache."""
        self.stdout.write("🧹 Clearing All Cache")
        self.stdout.write("=" * 30)

        try:
            cache.clear()
            self.stdout.write("✅ All cache cleared successfully")
        except Exception as e:
            self.stdout.write(f"❌ Error clearing cache: {e}")

    def show_cache_stats(self):
        """Show cache statistics."""
        self.stdout.write("📊 Cache Statistics")
        self.stdout.write("=" * 30)

        # Check if using django-redis
        backend = settings.CACHES["default"]["BACKEND"]
        if "django_redis" in backend:
            try:
                import django_redis
                from django_redis import get_redis_connection

                r = get_redis_connection("default")
                info = r.info()
                self.stdout.write("ℹ️ Redis INFO:")
                self.stdout.write(f"  Redis Version: {info.get('redis_version')}")
                self.stdout.write(
                    f"  Used Memory: {info.get('used_memory_human')} ({info.get('used_memory')} bytes)"
                )
                self.stdout.write(f"  Max Memory: {info.get('maxmemory_human', 'N/A')}")
                self.stdout.write(
                    f"  Connected Clients: {info.get('connected_clients')}"
                )
                self.stdout.write(f"  Uptime: {info.get('uptime_in_days')} days")
                self.stdout.write(
                    f"  Total Keys: {info.get('db0', {}).get('keys', 'N/A') if 'db0' in info else 'N/A'}"
                )
                self.stdout.write(f"  Hits: {info.get('keyspace_hits')}")
                self.stdout.write(f"  Misses: {info.get('keyspace_misses')}")
                total = info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)
                hit_rate = (
                    (info.get("keyspace_hits", 0) / total * 100) if total > 0 else 0
                )
                self.stdout.write(f"  Hit Rate: {hit_rate:.2f}%")
                self.stdout.write(f"  Evicted Keys: {info.get('evicted_keys')}")
                self.stdout.write(f"  Expired Keys: {info.get('expired_keys')}")
            except ImportError:
                self.stdout.write("  ❌ django-redis not installed")
            except Exception as e:
                self.stdout.write(f"  ❌ Error retrieving Redis stats: {e}")
        else:
            self.stdout.write("ℹ️ Basic cache statistics:")
            self.stdout.write("  Note: Detailed statistics require Redis INFO command")
            self.stdout.write("  or custom monitoring implementation")
            # Test cache connectivity
            try:
                cache.set("stats_test", "test_value", 10)
                retrieved = cache.get("stats_test")
                if retrieved == "test_value":
                    self.stdout.write("  ✅ Cache connectivity: OK")
                else:
                    self.stdout.write("  ❌ Cache connectivity: FAILED")
            except Exception as e:
                self.stdout.write(f"  ❌ Cache connectivity error: {e}")
