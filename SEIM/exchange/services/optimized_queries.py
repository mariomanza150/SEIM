"""
Optimized database queries for SGII.
Provides efficient query patterns and prefetch strategies.
"""
from django.db.models import Prefetch, Count, Q, F
from django.utils import timezone
from django.db import transaction
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
    def get_active_exchanges():
        """Get currently active exchanges."""
        today = timezone.now().date()
        return Exchange.objects.filter(
            status='in_progress',
            start_date__lte=today,
            end_date__gte=today
        ).select_related(
            'student',
            'destination_university'
        ).prefetch_related('courses')
    
    @staticmethod
    def get_exchanges_by_destination(country=None, university=None):
        """Get exchanges filtered by destination."""
        qs = Exchange.objects.select_related(
            'student',
            'destination_university'
        )
        
        if country:
            qs = qs.filter(destination_country=country)
        if university:
            qs = qs.filter(destination_university=university)
            
        return qs.annotate(
            duration_days=F('end_date') - F('start_date')
        ).order_by('-created_at')
    
    @staticmethod
    def get_document_verification_queue():
        """Get documents pending verification."""
        return Document.objects.filter(
            status='pending_verification'
        ).select_related(
            'exchange',
            'exchange__student',
            'document_type'
        ).order_by('created_at')
    
    @staticmethod
    def bulk_update_status(exchange_ids, new_status, user):
        """Bulk update exchange status with timeline tracking."""
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
    
    @staticmethod
    def get_exchange_timeline(exchange_id):
        """Get complete timeline for an exchange."""
        return Timeline.objects.filter(
            exchange_id=exchange_id
        ).select_related('user').order_by('-created_at')
    
    @staticmethod
    def get_recent_comments(limit=10):
        """Get recent comments across all exchanges."""
        return Comment.objects.select_related(
            'user',
            'exchange',
            'exchange__student'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def search_exchanges(query):
        """Search exchanges by multiple fields."""
        return Exchange.objects.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__email__icontains=query) |
            Q(destination_university__name__icontains=query) |
            Q(destination_country__icontains=query) |
            Q(exchange_program__icontains=query)
        ).select_related(
            'student',
            'destination_university'
        ).distinct()
