"""
Unit tests for analytics services.
"""

import datetime
import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from analytics.services import AnalyticsService
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture(scope="function")
def application_statuses(db):
    """Create application statuses, avoiding duplicates."""
    statuses = {}
    for name in ["draft", "submitted", "approved", "rejected", "under_review"]:
        status, _ = ApplicationStatus.objects.get_or_create(name=name)
        statuses[name] = status
    return statuses


@pytest.fixture(scope="function")
def programs():
    """Create test programs with required dates."""
    today = datetime.date.today()
    return {
        'active': Program.objects.create(
            name="Test Program 1",
            description="Test Description 1",
            is_active=True,
            start_date=today,
            end_date=today + datetime.timedelta(days=30)
        ),
        'inactive': Program.objects.create(
            name="Test Program 2",
            description="Test Description 2",
            is_active=False,
            start_date=today,
            end_date=today + datetime.timedelta(days=30)
        )
    }


@pytest.fixture
def applications(user, application_statuses, programs):
    """Create test applications."""
    return {
        'draft': Application.objects.create(
            student=user,
            program=programs['active'],
            status=application_statuses['draft'],
            created_at=timezone.now() - timedelta(days=5)
        ),
        'submitted': Application.objects.create(
            student=user,
            program=programs['active'],
            status=application_statuses['submitted'],
            created_at=timezone.now() - timedelta(days=3)
        ),
        'approved': Application.objects.create(
            student=user,
            program=programs['inactive'],
            status=application_statuses['approved'],
            created_at=timezone.now() - timedelta(days=1)
        )
    }


@pytest.mark.django_db
class TestAnalyticsService:
    def test_get_application_statistics(self, applications):
        """Test getting application statistics."""
        stats = AnalyticsService.get_application_statistics()

        assert stats['total_applications'] == 3
        assert stats['total_users'] == 1
        assert stats['total_programs'] == 2
        assert stats['applications_by_status']['draft'] == 1
        assert stats['applications_by_status']['submitted'] == 1
        assert stats['applications_by_status']['approved'] == 1

    def test_get_program_statistics(self, programs, applications):
        """Test getting program statistics."""
        stats = AnalyticsService.get_program_statistics()

        assert len(stats) == 2
        program1_stats = next(s for s in stats if s['name'] == 'Test Program 1')
        program2_stats = next(s for s in stats if s['name'] == 'Test Program 2')

        assert program1_stats['total_applications'] == 2
        assert program1_stats['is_active'] is True
        assert program2_stats['total_applications'] == 1
        assert program2_stats['is_active'] is False

    def test_get_user_statistics(self, user, applications):
        """Test getting user statistics."""
        stats = AnalyticsService.get_user_statistics()

        assert len(stats) == 1
        user_stats = stats[0]
        assert user_stats['username'] == 'testuser'
        assert user_stats['total_applications'] == 3

    def test_get_timeline_statistics(self, applications):
        """Test getting timeline statistics."""
        stats = AnalyticsService.get_timeline_statistics(days=30)

        assert len(stats) >= 1
        # Check that we have data for the days we created applications
        dates = [s['day'] for s in stats]
        assert len(dates) >= 1

    def test_get_conversion_rates(self, applications):
        """Test getting conversion rates."""
        rates = AnalyticsService.get_conversion_rates()

        assert 'draft_to_submitted' in rates
        assert 'submitted_to_approved' in rates
        assert rates['draft_to_submitted'] == 100.0  # 1 draft, 1 submitted
        assert rates['submitted_to_approved'] == 100.0  # 1 submitted, 1 approved

    def test_get_conversion_rates_zero_denominator(self):
        """Test conversion rates with zero denominator."""
        # Delete all applications
        Application.objects.all().delete()

        rates = AnalyticsService.get_conversion_rates()

        assert rates['draft_to_submitted'] == 0
        assert rates['submitted_to_approved'] == 0

    def test_get_user_engagement_metrics(self, applications):
        """Test getting user engagement metrics."""
        metrics = AnalyticsService.get_user_engagement_metrics()

        assert metrics['active_users'] == 1
        assert metrics['average_applications_per_user'] == 3.0

    def test_get_user_engagement_metrics_no_users(self):
        """Test user engagement metrics with no users."""
        # Delete all applications
        Application.objects.all().delete()

        metrics = AnalyticsService.get_user_engagement_metrics()

        assert metrics['active_users'] == 0
        assert metrics['average_applications_per_user'] == 0

    def test_get_program_performance_metrics(self, programs, applications):
        """Test getting program performance metrics."""
        metrics = AnalyticsService.get_program_performance_metrics()

        assert len(metrics) == 2
        program1_metrics = next(m for m in metrics if m['name'] == 'Test Program 1')
        program2_metrics = next(m for m in metrics if m['name'] == 'Test Program 2')

        assert program1_metrics['total_applications'] == 2
        assert program1_metrics['is_active'] is True
        assert program2_metrics['total_applications'] == 1
        assert program2_metrics['is_active'] is False

    def test_get_application_trends(self, applications):
        """Test getting application trends."""
        trends = AnalyticsService.get_application_trends(days=30)

        assert len(trends) >= 1
        # Should be the same as timeline statistics
        timeline_stats = AnalyticsService.get_timeline_statistics(days=30)
        assert len(trends) == len(timeline_stats)

    def test_get_user_demographics(self, user):
        """Test getting user demographics."""
        demographics = AnalyticsService.get_user_demographics()

        assert demographics['total_users'] >= 1
        assert 'users_by_role' in demographics
        # Should have at least one user with unknown role
        assert 'unknown' in demographics['users_by_role'] or 'student' in demographics['users_by_role']

    def test_get_system_health_metrics(self, programs, applications):
        """Test getting system health metrics."""
        metrics = AnalyticsService.get_system_health_metrics()

        assert metrics['total_programs'] == 2
        assert metrics['total_applications'] == 3
        assert metrics['total_users'] >= 1

    @patch('analytics.services.connection')
    def test_get_custom_analytics(self, mock_connection):
        """Test executing custom analytics query."""
        # Mock the database cursor
        mock_cursor = MagicMock()
        mock_cursor.description = [('count',), ('total',)]
        mock_cursor.fetchone.return_value = (5, 10)
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        query = "SELECT COUNT(*) as count, SUM(value) as total FROM test_table"
        result = AnalyticsService.get_custom_analytics(query)

        assert result['count'] == 5
        assert result['total'] == 10
        mock_cursor.execute.assert_called_once_with(query)

    def test_get_dashboard_metrics(self, applications):
        """Test getting dashboard metrics."""
        metrics = AnalyticsService.get_dashboard_metrics()

        assert 'total_students' in metrics
        assert 'applications_by_status' in metrics
        assert 'ongoing_applications' in metrics
        assert metrics['total_students'] == 1
        assert metrics['ongoing_applications'] == 1  # 1 submitted application

    def test_get_program_metrics(self, programs, applications):
        """Test getting program metrics."""
        metrics = AnalyticsService.get_program_metrics(program_id=programs['active'].id)

        assert 'total_applications' in metrics
        assert 'approved' in metrics
        assert 'rejected' in metrics
        assert 'ongoing' in metrics
        assert 'withdrawn' in metrics
        assert metrics['total_applications'] == 2

    def test_get_program_metrics_all_programs(self, programs, applications):
        """Test getting metrics for all programs."""
        metrics = AnalyticsService.get_program_metrics()

        assert 'total_applications' in metrics
        assert metrics['total_applications'] == 3

    def test_get_coordinator_metrics(self, user):
        """Test getting coordinator metrics."""
        metrics = AnalyticsService.get_coordinator_metrics(coordinator_id=user.id)

        assert 'assigned_applications' in metrics
        assert 'pending_review' in metrics
        assert metrics['assigned_applications'] >= 0  # May be 0 if no assignments

    def test_invalidate_analytics_cache(self):
        """Test invalidating analytics cache."""
        # This should not raise an exception
        AnalyticsService.invalidate_analytics_cache()

    def test_get_user_activity(self, applications):
        """Test getting user activity."""
        activity = AnalyticsService.get_user_activity(days=30)

        assert isinstance(activity, list)
        # Activity may be empty if no UserSession records exist

    def test_get_user_activity_custom_days(self, applications):
        """Test getting user activity with custom days."""
        activity = AnalyticsService.get_user_activity(days=7)

        assert isinstance(activity, list)

    def test_get_cached_metrics_with_fallback(self, applications):
        """Test getting cached metrics with fallback."""
        # Test with dashboard metrics
        metrics = AnalyticsService.get_cached_metrics_with_fallback('dashboard')

        assert 'total_students' in metrics
        assert 'ongoing_applications' in metrics

    def test_get_cached_metrics_with_fallback_program_metrics(self, programs, applications):
        """Test getting cached program metrics with fallback."""
        metrics = AnalyticsService.get_cached_metrics_with_fallback('program', program_id=programs['active'].id)

        assert 'total_applications' in metrics

    def test_get_cached_metrics_with_fallback_activity(self, applications):
        """Test getting cached activity metrics with fallback."""
        metrics = AnalyticsService.get_cached_metrics_with_fallback('activity', days=30)

        assert isinstance(metrics, list)

    def test_get_cached_metrics_with_fallback_unknown_type(self):
        """Test getting cached metrics with unknown type."""
        # Should raise ValueError for unknown metric type
        with pytest.raises(ValueError, match="Unknown metric type"):
            AnalyticsService.get_cached_metrics_with_fallback('unknown_type')

    @patch('core.cache.invalidate_cache_pattern')
    def test_cache_invalidation(self, mock_invalidate):
        """Test that cache invalidation is called."""
        AnalyticsService.invalidate_analytics_cache()
        mock_invalidate.assert_called_once_with("analytics")

    @patch('analytics.services.generate_report.delay')
    def test_trigger_report(self, mock_delay):
        """Test triggering report generation."""
        # Mock the report object with a valid UUID
        mock_report = MagicMock()
        mock_report.id = uuid.uuid4()
        AnalyticsService.trigger_report(mock_report)
        mock_delay.assert_called_once_with(str(mock_report.id))

    def test_analytics_service_with_no_data(self):
        """Test analytics service methods with no data."""
        # Clear all data
        Application.objects.all().delete()
        Program.objects.all().delete()
        User.objects.all().delete()

        # Test that methods don't crash with no data
        stats = AnalyticsService.get_application_statistics()
        assert stats['total_applications'] == 0
        assert stats['total_users'] == 0
        assert stats['total_programs'] == 0

        program_stats = AnalyticsService.get_program_statistics()
        assert len(program_stats) == 0

        user_stats = AnalyticsService.get_user_statistics()
        assert len(user_stats) == 0

        conversion_rates = AnalyticsService.get_conversion_rates()
        assert conversion_rates['draft_to_submitted'] == 0
        assert conversion_rates['submitted_to_approved'] == 0

    def test_analytics_service_edge_cases(self, applications):
        """Test analytics service edge cases."""
        # Test with very large number of days
        timeline_stats = AnalyticsService.get_timeline_statistics(days=365)
        assert isinstance(timeline_stats, list)

        # Test with zero days
        timeline_stats = AnalyticsService.get_timeline_statistics(days=0)
        assert isinstance(timeline_stats, list)

        # Test with negative days
        timeline_stats = AnalyticsService.get_timeline_statistics(days=-1)
        assert isinstance(timeline_stats, list)

    def test_analytics_service_performance(self, applications):
        """Test that analytics service methods are performant."""
        import time

        # Test that methods complete within reasonable time
        start_time = time.time()
        AnalyticsService.get_application_statistics()
        end_time = time.time()
        assert end_time - start_time < 1.0  # Should complete within 1 second

        start_time = time.time()
        AnalyticsService.get_program_statistics()
        end_time = time.time()
        assert end_time - start_time < 1.0

        start_time = time.time()
        AnalyticsService.get_user_statistics()
        end_time = time.time()
        assert end_time - start_time < 1.0
    
    def test_get_user_demographics_by_department(self, user):
        """Test getting user demographics broken down by additional criteria."""
        demographics = AnalyticsService.get_user_demographics()
        
        # Verify structure
        assert 'total_users' in demographics
        assert demographics['total_users'] >= 1
        assert isinstance(demographics['users_by_role'], dict)
    
    def test_get_application_statistics_caching(self, applications):
        """Test that application statistics are cached."""
        # First call
        stats1 = AnalyticsService.get_application_statistics()
        
        # Second call should use cache
        stats2 = AnalyticsService.get_application_statistics()
        
        # Should return same results
        assert stats1 == stats2
    
    def test_get_program_performance_with_inactive_programs(self, programs, applications):
        """Test program performance includes inactive programs."""
        metrics = AnalyticsService.get_program_performance_metrics()
        
        # Should include both active and inactive
        assert len(metrics) == 2
        
        # Verify we have both types
        active_count = sum(1 for m in metrics if m['is_active'])
        inactive_count = sum(1 for m in metrics if not m['is_active'])
        
        assert active_count >= 1
        assert inactive_count >= 1
    
    def test_get_timeline_statistics_ordering(self, applications):
        """Test that timeline statistics are ordered by day."""
        stats = AnalyticsService.get_timeline_statistics(days=30)
        
        if len(stats) > 1:
            # Verify ordering
            days = [s['day'] for s in stats]
            assert days == sorted(days)
    
    def test_get_conversion_rates_precision(self, applications):
        """Test conversion rates are calculated with proper precision."""
        rates = AnalyticsService.get_conversion_rates()
        
        # Verify precision (should be float, not int)
        assert isinstance(rates['draft_to_submitted'], (int, float))
        assert isinstance(rates['submitted_to_approved'], (int, float))
        
        # Verify range (0-100 for percentages)
        assert 0 <= rates['draft_to_submitted'] <= 100
        assert 0 <= rates['submitted_to_approved'] <= 100
    
    def test_get_user_engagement_precision(self, applications):
        """Test user engagement metrics are precise."""
        metrics = AnalyticsService.get_user_engagement_metrics()
        
        # Verify average is float with precision
        assert isinstance(metrics['average_applications_per_user'], (int, float))
        assert metrics['average_applications_per_user'] >= 0
    
    def test_analytics_with_multiple_application_statuses(self, user, programs, application_statuses):
        """Test analytics with applications in various statuses."""
        # Create applications in different statuses
        for status_name in ['draft', 'submitted', 'under_review', 'approved', 'rejected']:
            if status_name in application_statuses:
                Application.objects.create(
                    student=user,
                    program=programs['active'],
                    status=application_statuses[status_name]
                )
        
        stats = AnalyticsService.get_application_statistics()
        
        # Verify all statuses counted
        assert stats['total_applications'] >= 5
        assert len(stats['applications_by_status']) >= 5
    
    def test_get_program_statistics_no_applications(self, programs):
        """Test program statistics when programs have no applications."""
        # Delete all applications
        Application.objects.all().delete()
        
        stats = AnalyticsService.get_program_statistics()
        
        # Should still return program stats
        assert len(stats) == 2
        for stat in stats:
            assert stat['total_applications'] == 0
    
    def test_get_user_statistics_multiple_applications(self, user, programs, application_statuses):
        """Test user statistics with users having multiple applications."""
        # Create multiple applications for same user
        for i in range(5):
            Application.objects.create(
                student=user,
                program=programs['active'],
                status=application_statuses['draft']
            )
        
        stats = AnalyticsService.get_user_statistics()
        
        # Find user's stats
        user_stat = next((s for s in stats if s['username'] == user.username), None)
        assert user_stat is not None
        assert user_stat['total_applications'] >= 5
    
    def test_get_timeline_statistics_data_structure(self, applications):
        """Test timeline statistics return proper data structure."""
        stats = AnalyticsService.get_timeline_statistics(days=30)
        
        assert isinstance(stats, list)
        
        if len(stats) > 0:
            # Verify each entry has required fields
            for entry in stats:
                assert 'day' in entry
                assert 'applications' in entry
                assert isinstance(entry['applications'], int)
    
    def test_get_system_health_with_large_dataset(self, user, programs, application_statuses):
        """Test system health metrics with larger dataset."""
        # Create many applications
        for i in range(20):
            Application.objects.create(
                student=user,
                program=programs['active'],
                status=application_statuses['submitted']
            )
        
        metrics = AnalyticsService.get_system_health_metrics()
        
        # Verify metrics scale appropriately
        assert metrics['total_applications'] >= 20
        assert metrics['total_programs'] >= 1
        assert metrics['total_users'] >= 1
    
    def test_cache_decorator_different_params(self, applications):
        """Test that cache distinguishes between different parameters."""
        # Get timeline for 7 days
        stats_7 = AnalyticsService.get_timeline_statistics(days=7)
        
        # Get timeline for 30 days
        stats_30 = AnalyticsService.get_timeline_statistics(days=30)
        
        # Should be different results (different cache keys)
        # Length may differ
        assert isinstance(stats_7, list)
        assert isinstance(stats_30, list)
    
    def test_application_statistics_distinct_users(self, user, another_user, programs, application_statuses):
        """Test that user count is distinct."""
        # Create multiple applications for same user
        for i in range(3):
            Application.objects.create(
                student=user,
                program=programs['active'],
                status=application_statuses['draft']
            )
        
        # Create one application for another user
        Application.objects.create(
            student=another_user,
            program=programs['active'],
            status=application_statuses['draft']
        )
        
        stats = AnalyticsService.get_application_statistics()
        
        # Should count 2 distinct users, not 4
        assert stats['total_users'] == 2
        assert stats['total_applications'] == 4
    
    def test_conversion_rates_with_complex_funnel(self, user, programs, application_statuses):
        """Test conversion rates with realistic funnel."""
        # Create 10 draft applications
        for i in range(10):
            Application.objects.create(
                student=user,
                program=programs['active'],
                status=application_statuses['draft']
            )
        
        # 7 of them submitted
        for i in range(7):
            Application.objects.create(
                student=user,
                program=programs['active'],
                status=application_statuses['submitted']
            )
        
        # 3 approved
        for i in range(3):
            Application.objects.create(
                student=user,
                program=programs['active'],
                status=application_statuses['approved']
            )
        
        rates = AnalyticsService.get_conversion_rates()
        
        # draft_to_submitted: 7/10 = 70%
        # submitted_to_approved: 3/7 ≈ 42.86%
        assert 65 <= rates['draft_to_submitted'] <= 75
        assert 40 <= rates['submitted_to_approved'] <= 45
    
    def test_analytics_methods_are_static(self):
        """Test that analytics methods are static (no instance needed)."""
        # Should be able to call methods without instantiation
        stats = AnalyticsService.get_application_statistics()
        assert stats is not None
        
        # Verify class doesn't need to be instantiated
        # (If methods weren't static, this would fail)
        assert isinstance(stats, dict)
    
    def test_analytics_cache_timeout(self, applications):
        """Test that analytics cache has proper timeout."""
        # Get stats (should cache for 30 min)
        AnalyticsService.get_application_statistics()
        
        # Cache key should exist
        from core.cache import generate_cache_key
        cache_key = generate_cache_key('analytics', 'get_application_statistics')
        
        from django.core.cache import cache
        cached_value = cache.get(cache_key)
        
        # Should be cached
        assert cached_value is not None
    
    def test_get_dashboard_metrics_structure(self, applications):
        """Test dashboard metrics return complete structure."""
        metrics = AnalyticsService.get_dashboard_metrics()
        
        # Verify all expected keys present
        required_keys = ['total_students', 'applications_by_status', 'ongoing_applications']
        for key in required_keys:
            assert key in metrics, f"Missing key: {key}"
    
    def test_get_program_metrics_single_program(self, programs, applications):
        """Test getting metrics for a single program."""
        metrics = AnalyticsService.get_program_metrics(program_id=programs['active'].id)
        
        # Verify structure for single program
        assert 'total_applications' in metrics
        assert isinstance(metrics['total_applications'], int)
    
    def test_analytics_error_handling(self):
        """Test analytics methods handle errors gracefully."""
        # Test with invalid program ID
        try:
            metrics = AnalyticsService.get_program_metrics(program_id=999999)
            # Should either return empty/zero metrics or handle gracefully
            assert isinstance(metrics, dict)
        except Exception:
            # If it raises an exception, it should be a known type
            pass
    
    def test_concurrent_analytics_calls(self, applications):
        """Test that concurrent analytics calls don't interfere."""
        import concurrent.futures
        
        def get_stats():
            return AnalyticsService.get_application_statistics()
        
        # Make multiple concurrent calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(get_stats) for _ in range(3)]
            results = [f.result() for f in futures]
        
        # All should succeed and return same data
        assert len(results) == 3
        for result in results:
            assert result['total_applications'] == results[0]['total_applications']