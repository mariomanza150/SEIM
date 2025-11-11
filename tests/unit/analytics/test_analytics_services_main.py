"""
Unit tests for analytics services.
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from analytics.services import AnalyticsService
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


@pytest.mark.django_db
class TestAnalyticsService:
    """Test cases for AnalyticsService."""

    def test_get_application_statistics(self):
        """Test getting application statistics."""
        service = AnalyticsService()

        # Create test data
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )

        # Create programs with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program1 = Program.objects.create(
            name="Program 1",
            description="Test Program 1",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )
        program2 = Program.objects.create(
            name="Program 2",
            description="Test Program 2",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )

        status_draft, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        status_submitted, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={"order": 2})
        status_approved, _ = ApplicationStatus.objects.get_or_create(name="approved", defaults={"order": 3})

        # Create applications using 'student' field
        Application.objects.create(student=user1, program=program1, status=status_draft)
        Application.objects.create(student=user1, program=program2, status=status_submitted)
        Application.objects.create(student=user2, program=program1, status=status_approved)
        Application.objects.create(student=user2, program=program2, status=status_draft)

        stats = service.get_application_statistics()

        assert stats['total_applications'] == 4
        assert stats['total_users'] == 2
        assert stats['total_programs'] == 2
        assert stats['applications_by_status']['draft'] == 2
        assert stats['applications_by_status']['submitted'] == 1
        assert stats['applications_by_status']['approved'] == 1

    def test_get_program_statistics(self):
        """Test getting program statistics."""
        service = AnalyticsService()

        # Create test data with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program1 = Program.objects.create(
            name="Program 1",
            description="Test Program 1",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )
        program2 = Program.objects.create(
            name="Program 2",
            description="Test Program 2",
            is_active=False,
            start_date=start_date,
            end_date=end_date
        )

        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )

        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        # Create applications using 'student' field
        Application.objects.create(student=user1, program=program1, status=status_obj)
        Application.objects.create(student=user2, program=program1, status=status_obj)
        Application.objects.create(student=user1, program=program2, status=status_obj)

        stats = service.get_program_statistics()

        assert len(stats) == 2
        assert stats[0]['name'] == "Program 1"
        assert stats[0]['total_applications'] == 2
        assert stats[1]['name'] == "Program 2"
        assert stats[1]['total_applications'] == 1

    def test_get_user_statistics(self):
        """Test getting user statistics."""
        service = AnalyticsService()

        # Create test data
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )

        # Create programs with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program1 = Program.objects.create(
            name="Program 1",
            description="Test Program 1",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )
        program2 = Program.objects.create(
            name="Program 2",
            description="Test Program 2",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )

        status_draft, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        status_submitted, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={"order": 2})

        # Create applications using 'student' field
        Application.objects.create(student=user1, program=program1, status=status_draft)
        Application.objects.create(student=user1, program=program2, status=status_submitted)
        Application.objects.create(student=user2, program=program1, status=status_draft)

        stats = service.get_user_statistics()

        assert len(stats) == 2

        # Find users by username since order might vary
        user1_stats = next((s for s in stats if s['username'] == "user1"), None)
        user2_stats = next((s for s in stats if s['username'] == "user2"), None)

        assert user1_stats is not None
        assert user2_stats is not None
        assert user1_stats['total_applications'] == 2
        assert user2_stats['total_applications'] == 1

    def test_get_timeline_statistics(self):
        """Test getting timeline statistics."""
        service = AnalyticsService()

        # Create test data
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Create program with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )

        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        # Create applications with different dates
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        app1 = Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        app1.created_at = now
        app1.save()

        app2 = Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        app2.created_at = yesterday
        app2.save()

        app3 = Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        app3.created_at = last_week
        app3.save()

        stats = service.get_timeline_statistics(days=30)

        assert len(stats) > 0
        assert any(day['applications'] > 0 for day in stats)

    def test_get_conversion_rates(self):
        """Test getting conversion rates."""
        service = AnalyticsService()

        # Create test data
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )

        # Create program with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )

        status_draft, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        status_submitted, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={"order": 2})
        status_approved, _ = ApplicationStatus.objects.get_or_create(name="approved", defaults={"order": 3})

        # Create applications using 'student' field
        Application.objects.create(student=user1, program=program, status=status_draft)
        Application.objects.create(student=user1, program=program, status=status_submitted)
        Application.objects.create(student=user2, program=program, status=status_approved)

        rates = service.get_conversion_rates()

        assert 'draft_to_submitted' in rates
        assert 'submitted_to_approved' in rates
        assert rates['draft_to_submitted'] > 0
        assert rates['submitted_to_approved'] > 0

    def test_get_user_engagement_metrics(self):
        """Test getting user engagement metrics."""
        service = AnalyticsService()

        # Create test data
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )

        # Create programs with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program1 = Program.objects.create(
            name="Program 1",
            description="Test Program 1",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )
        program2 = Program.objects.create(
            name="Program 2",
            description="Test Program 2",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )

        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        # Create applications using 'student' field
        Application.objects.create(student=user1, program=program1, status=status_obj)
        Application.objects.create(student=user1, program=program2, status=status_obj)
        Application.objects.create(student=user2, program=program1, status=status_obj)

        metrics = service.get_user_engagement_metrics()

        assert 'active_users' in metrics
        assert 'average_applications_per_user' in metrics
        assert metrics['active_users'] >= 2
        assert metrics['average_applications_per_user'] > 0

    def test_get_program_performance_metrics(self):
        """Test getting program performance metrics."""
        service = AnalyticsService()

        # Create test data with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program1 = Program.objects.create(
            name="Program 1",
            description="Test Program 1",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )
        program2 = Program.objects.create(
            name="Program 2",
            description="Test Program 2",
            is_active=False,
            start_date=start_date,
            end_date=end_date
        )

        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )

        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        # Create applications using 'student' field
        Application.objects.create(student=user1, program=program1, status=status_obj)
        Application.objects.create(student=user2, program=program1, status=status_obj)
        Application.objects.create(student=user1, program=program2, status=status_obj)

        metrics = service.get_program_performance_metrics()

        assert len(metrics) == 2
        assert metrics[0]['name'] == "Program 1"
        assert metrics[0]['total_applications'] == 2
        assert metrics[1]['name'] == "Program 2"
        assert metrics[1]['total_applications'] == 1

    def test_get_application_trends(self):
        """Test getting application trends."""
        service = AnalyticsService()

        # Create test data
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Create program with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )

        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        # Create applications with different dates
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        app1 = Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        app1.created_at = now
        app1.save()

        app2 = Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        app2.created_at = yesterday
        app2.save()

        app3 = Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        app3.created_at = last_week
        app3.save()

        trends = service.get_application_trends(days=30)

        assert len(trends) > 0
        assert any(day['applications'] > 0 for day in trends)

    def test_get_user_demographics(self):
        """Test getting user demographics."""
        service = AnalyticsService()

        # Create test data
        User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe"
        )
        User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith"
        )

        demographics = service.get_user_demographics()

        assert 'total_users' in demographics
        assert 'users_by_role' in demographics
        assert demographics['total_users'] >= 2

    def test_get_system_health_metrics(self):
        """Test getting system health metrics."""
        service = AnalyticsService()

        # Create test data
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Create program with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )

        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        # Create application using 'student' field
        Application.objects.create(student=user, program=program, status=status_obj)

        health = service.get_system_health_metrics()

        assert 'total_programs' in health
        assert 'total_applications' in health
        assert 'total_users' in health
        assert health['total_programs'] >= 1
        assert health['total_applications'] >= 1
        assert health['total_users'] >= 1

    def test_get_custom_analytics(self):
        """Test getting custom analytics."""
        service = AnalyticsService()

        # Create test data
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Create program with required dates
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date=start_date,
            end_date=end_date
        )

        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        # Create application using 'student' field
        Application.objects.create(student=user, program=program, status=status_obj)

        # Test custom query
        result = service.get_custom_analytics("SELECT COUNT(*) as count FROM exchange_application")

        assert 'count' in result
        assert result['count'] >= 1
