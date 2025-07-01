"""
Database optimization scripts for SGII.
Creates indexes and optimizes queries for better performance.
"""

# Create a migration file for performance indexes
MIGRATION_CONTENT = '''# Generated migration for performance optimization

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', 'LATEST_MIGRATION'),  # Replace with actual latest migration
    ]

    operations = [
        # Indexes for Exchange model
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['status', 'created_at'], name='exchange_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['student', 'status'], name='exchange_student_status_idx'),
        ),
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['destination_university', 'status'], name='exchange_uni_status_idx'),
        ),
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['start_date', 'end_date'], name='exchange_date_range_idx'),
        ),
        
        # Indexes for Document model
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['exchange', 'document_type'], name='document_exchange_type_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['status', 'created_at'], name='document_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['file_hash'], name='document_hash_idx'),
        ),
        
        # Indexes for Timeline model
        migrations.AddIndex(
            model_name='timeline',
            index=models.Index(fields=['exchange', 'status'], name='timeline_exchange_status_idx'),
        ),
        migrations.AddIndex(
            model_name='timeline',
            index=models.Index(fields=['created_at'], name='timeline_created_idx'),
        ),
        
        # Indexes for Comment model
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['exchange', 'created_at'], name='comment_exchange_created_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['user', 'created_at'], name='comment_user_created_idx'),
        ),
        
        # Indexes for Course model
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['exchange', 'status'], name='course_exchange_status_idx'),
        ),
        
        # Composite indexes for common queries
        migrations.AddIndex(
            model_name='exchange',
            index=models.Index(fields=['status', 'destination_country', 'created_at'], 
                              name='exchange_status_country_idx'),
        ),
    ]
'''

# Query optimization helpers
QUERY_OPTIMIZATIONS = '''
# Common query optimizations for SGII

from django.db.models import Prefetch, Count, Q, F
from exchange.models import Exchange, Document, Timeline, Comment, Course

class OptimizedQueries:
    """Optimized database queries for common operations."""
    
    @staticmethod
    def get_exchanges_with_related():
        """Get exchanges with all related data prefetched."""
        return Exchange.objects.select_related(
            'student',
            'student__profile',
            'home_university',
            'destination_university',
        ).prefetch_related(
            'documents',
            'timeline_set',
            'comments',
            'courses',
            Prefetch('documents', 
                    queryset=Document.objects.select_related('document_type'))
        )
    
    @staticmethod
    def get_pending_exchanges():
        """Get exchanges pending approval with optimized queries."""
        return Exchange.objects.filter(
            status__in=['submitted', 'under_review']
        ).select_related(
            'student',
            'destination_university'
        ).prefetch_related(
            'documents'
        ).annotate(
            document_count=Count('documents'),
            pending_documents=Count('documents', filter=Q(documents__status='pending'))
        )
    
    @staticmethod
    def get_exchange_statistics():
        """Get exchange statistics with single query."""
        return Exchange.objects.aggregate(
            total=Count('id'),
            approved=Count('id', filter=Q(status='approved')),
            pending=Count('id', filter=Q(status__in=['submitted', 'under_review'])),
            completed=Count('id', filter=Q(status='completed')),
            by_country=Count('destination_country', distinct=True),
            by_university=Count('destination_university', distinct=True)
        )
    
    @staticmethod
    def get_user_exchanges(user):
        """Get all exchanges for a user with related data."""
        return Exchange.objects.filter(
            student=user
        ).select_related(
            'destination_university',
            'home_university'
        ).prefetch_related(
            'documents',
            'timeline_set'
        ).annotate(
            last_update=F('timeline__created_at')
        ).order_by('-last_update')
    
    @staticmethod
    def bulk_update_status(exchange_ids, new_status, user):
        """Bulk update exchange status with timeline tracking."""
        from django.db import transaction
        
        with transaction.atomic():
            # Update exchanges
            updated = Exchange.objects.filter(
                id__in=exchange_ids
            ).update(
                status=new_status,
                updated_at=timezone.now()
            )
            
            # Create timeline entries
            timeline_entries = [
                Timeline(
                    exchange_id=exchange_id,
                    status=new_status,
                    user=user,
                    notes=f"Bulk status update to {new_status}"
                )
                for exchange_id in exchange_ids
            ]
            Timeline.objects.bulk_create(timeline_entries)
            
            return updated
'''

# Cache configuration
CACHE_CONFIG = '''
# Cache configuration for SGII

from django.core.cache import cache
from django.conf import settings
import hashlib
import json

class CacheManager:
    """Centralized cache management for SGII."""
    
    # Cache timeouts
    TIMEOUTS = {
        'university_list': 86400,  # 24 hours
        'country_list': 86400,     # 24 hours
        'exchange_stats': 3600,    # 1 hour
        'user_permissions': 1800,  # 30 minutes
        'document_types': 86400,   # 24 hours
        'exchange_detail': 300,    # 5 minutes
    }
    
    @classmethod
    def get_or_set(cls, key, callable_func, timeout=None):
        """Get from cache or set if not exists."""
        if timeout is None:
            timeout = cls.TIMEOUTS.get(key.split(':')[0], 300)
            
        value = cache.get(key)
        if value is None:
            value = callable_func()
            cache.set(key, value, timeout)
        return value
    
    @classmethod
    def invalidate_pattern(cls, pattern):
        """Invalidate all cache keys matching pattern."""
        if hasattr(cache, '_cache'):
            # For Redis backend
            cache.delete_pattern(f"*{pattern}*")
        else:
            # For other backends, need to track keys
            pass
    
    @classmethod
    def invalidate_exchange(cls, exchange_id):
        """Invalidate all caches related to an exchange."""
        keys = [
            f'exchange_detail:{exchange_id}',
            f'exchange_documents:{exchange_id}',
            f'exchange_timeline:{exchange_id}',
            'exchange_stats',
        ]
        cache.delete_many(keys)
    
    @classmethod
    def make_key(cls, prefix, params):
        """Generate cache key from prefix and parameters."""
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}:{param_hash}"

# Example usage in views
def get_universities():
    """Get list of universities with caching."""
    return CacheManager.get_or_set(
        'university_list',
        lambda: list(University.objects.values('id', 'name', 'country'))
    )

def get_exchange_stats():
    """Get exchange statistics with caching."""
    return CacheManager.get_or_set(
        'exchange_stats',
        lambda: OptimizedQueries.get_exchange_statistics()
    )
'''

print("Database optimization configurations created.")
print("\nTo apply:")
print("1. Create a new migration with the index definitions")
print("2. Update queries in views/services to use OptimizedQueries")
print("3. Implement CacheManager in frequently accessed data")
print("4. Run 'python manage.py makemigrations --name add_performance_indexes'")
print("5. Run 'python manage.py migrate'")
