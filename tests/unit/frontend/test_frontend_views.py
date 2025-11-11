"""
Test Frontend Views

Comprehensive tests for frontend application views.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import patch

from accounts.models import Role
from exchange.models import Application, ApplicationStatus, Program
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestHomeView(TestCase):
    """Test home page view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_home_view_anonymous_user(self):
        """Test home view for anonymous user displays welcome page."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/home.html')

    def test_home_view_authenticated_user_redirects(self):
        """Test home view redirects authenticated users to dashboard."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)

    def test_home_view_displays_stats(self):
        """Test home view displays program and application stats."""
        # Create some programs and applications
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True
        )
        
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_programs', response.context)
        self.assertIn('total_applications', response.context)

    @patch('frontend.views.Program.objects.filter')
    def test_home_view_handles_stats_error(self, mock_filter):
        """Test home view handles errors when fetching stats."""
        mock_filter.side_effect = Exception("Database error")
        
        response = self.client.get('/')
        
        # Should still render with default values
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_programs'], 0)
        self.assertEqual(response.context['total_applications'], 0)


@pytest.mark.django_db
class TestLoginView(TestCase):
    """Test login view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_login_view_anonymous(self):
        """Test login view displays for anonymous users."""
        response = self.client.get('/login/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/auth/login.html')

    def test_login_view_authenticated_redirects(self):
        """Test login view redirects authenticated users."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/login/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)


@pytest.mark.django_db
class TestRegisterView(TestCase):
    """Test registration view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_register_view_anonymous(self):
        """Test register view displays for anonymous users."""
        response = self.client.get('/register/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/auth/register.html')

    def test_register_view_authenticated_redirects(self):
        """Test register view redirects authenticated users."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/register/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)


@pytest.mark.django_db
class TestLogoutView(TestCase):
    """Test logout view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    def test_logout_view(self):
        """Test logout clears session."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/logout/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        
        # Verify cookie is set to clear JWT
        self.assertIn('clear_jwt_tokens', response.cookies)

    def test_logout_view_anonymous_user(self):
        """Test logout works even when not authenticated."""
        response = self.client.get('/logout/')
        
        self.assertEqual(response.status_code, 302)


@pytest.mark.django_db
class TestDashboardView(TestCase):
    """Test dashboard view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_dashboard_view(self):
        """Test dashboard view renders for all users."""
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dashboard.html')


@pytest.mark.django_db
class TestProgramsView(TestCase):
    """Test programs listing view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    def test_programs_view_requires_login(self):
        """Test programs view requires authentication."""
        response = self.client.get('/programs/')
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_programs_view_authenticated(self):
        """Test programs view displays for authenticated users."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/programs/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/programs/list.html')

    def test_programs_view_displays_active_programs(self):
        """Test programs view only displays active programs."""
        self.client.login(username='testuser', password='testpass123')
        
        active_program = Program.objects.create(
            name="Active Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True
        )
        
        inactive_program = Program.objects.create(
            name="Inactive Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=False
        )
        
        response = self.client.get('/programs/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('programs', response.context)
        
        # Should only include active program
        programs = list(response.context['programs'])
        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0].id, active_program.id)


@pytest.mark.django_db
class TestApplicationsView(TestCase):
    """Test applications listing view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        self.coordinator = User.objects.create_user(
            username="coordinator",
            email="coordinator@test.com",
            password="testpass123"
        )
        self.coordinator.roles.add(self.coordinator_role)

    def test_applications_view_requires_login(self):
        """Test applications view requires authentication."""
        response = self.client.get('/applications/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_applications_view_student_sees_own(self):
        """Test student only sees their own applications."""
        self.client.login(username='student', password='testpass123')
        
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True
        )
        
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        # Create application for student
        student_app = Application.objects.create(
            student=self.student,
            program=program,
            status=status
        )
        
        # Create application for different user
        other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="testpass123"
        )
        other_user.roles.add(self.student_role)
        
        other_app = Application.objects.create(
            student=other_user,
            program=program,
            status=status
        )
        
        response = self.client.get('/applications/')
        
        self.assertEqual(response.status_code, 200)
        applications = list(response.context['applications'])
        
        # Should only see own application
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].id, student_app.id)

    def test_applications_view_coordinator_sees_all(self):
        """Test coordinator sees all applications."""
        self.client.login(username='coordinator', password='testpass123')
        
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True
        )
        
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        # Create multiple applications
        app1 = Application.objects.create(
            student=self.student,
            program=program,
            status=status
        )
        
        other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="testpass123"
        )
        other_user.roles.add(self.student_role)
        
        app2 = Application.objects.create(
            student=other_user,
            program=program,
            status=status
        )
        
        response = self.client.get('/applications/')
        
        self.assertEqual(response.status_code, 200)
        applications = list(response.context['applications'])
        
        # Should see all applications
        self.assertEqual(len(applications), 2)


@pytest.mark.django_db
class TestAnalyticsView(TestCase):
    """Test analytics view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.admin_role, _ = Role.objects.get_or_create(name="admin")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123"
        )
        self.admin.roles.add(self.admin_role)
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

    def test_analytics_view_requires_login(self):
        """Test analytics view requires authentication."""
        response = self.client.get('/analytics/')
        
        self.assertEqual(response.status_code, 302)

    def test_analytics_view_admin_access(self):
        """Test admin can access analytics."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get('/analytics/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/admin/analytics.html')

    def test_analytics_view_student_denied(self):
        """Test student cannot access analytics."""
        self.client.login(username='student', password='testpass123')
        
        response = self.client.get('/analytics/')
        
        # Should be denied (403 or redirect)
        self.assertIn(response.status_code, [302, 403])

    @patch('frontend.views.AnalyticsService.get_dashboard_metrics')
    def test_analytics_view_displays_metrics(self, mock_metrics):
        """Test analytics view displays metrics."""
        self.client.login(username='admin', password='testpass123')
        
        mock_metrics.return_value = {
            'total_applications': 10,
            'total_programs': 5
        }
        
        response = self.client.get('/analytics/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('metrics', response.context)

    @patch('frontend.views.AnalyticsService.get_dashboard_metrics')
    def test_analytics_view_handles_error(self, mock_metrics):
        """Test analytics view handles service errors."""
        self.client.login(username='admin', password='testpass123')
        
        mock_metrics.side_effect = Exception("Service error")
        
        response = self.client.get('/analytics/')
        
        # Should still render with empty metrics
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['metrics'], {})


@pytest.mark.django_db
class TestAdminDashboardView(TestCase):
    """Test admin dashboard view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.admin_role, _ = Role.objects.get_or_create(name="admin")
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123"
        )
        self.admin.roles.add(self.admin_role)
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

    def test_admin_dashboard_requires_authentication(self):
        """Test admin dashboard requires authentication."""
        response = self.client.get('/admin-dashboard/')
        
        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_requires_admin_role(self):
        """Test admin dashboard requires admin role."""
        self.client.login(username='student', password='testpass123')
        
        response = self.client.get('/admin-dashboard/')
        
        # Non-admin should be redirected
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)

    def test_admin_dashboard_admin_access(self):
        """Test admin can access admin dashboard."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get('/admin-dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/admin/dashboard.html')

    @patch('frontend.views.AnalyticsService.get_dashboard_metrics')
    @patch('frontend.views.AnalyticsService.get_program_metrics')
    def test_admin_dashboard_displays_metrics(self, mock_program_metrics, mock_dashboard_metrics):
        """Test admin dashboard displays metrics."""
        self.client.login(username='admin', password='testpass123')
        
        mock_dashboard_metrics.return_value = {'stat': 'value'}
        mock_program_metrics.return_value = {'program': 'data'}
        
        response = self.client.get('/admin-dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('metrics', response.context)
        self.assertIn('program_metrics', response.context)

    @patch('frontend.views.AnalyticsService.get_dashboard_metrics')
    def test_admin_dashboard_handles_error(self, mock_metrics):
        """Test admin dashboard handles service errors."""
        self.client.login(username='admin', password='testpass123')
        
        mock_metrics.side_effect = Exception("Service error")
        
        response = self.client.get('/admin-dashboard/')
        
        # Should still render with empty metrics
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['metrics'], {})


@pytest.mark.django_db
class TestInvalidateCacheView(TestCase):
    """Test cache invalidation view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    def test_invalidate_cache_authenticated(self):
        """Test authenticated user can invalidate their cache."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/cache/invalidate/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'Cache invalidated')

    def test_invalidate_cache_anonymous(self):
        """Test anonymous user cannot invalidate cache."""
        response = self.client.get('/cache/invalidate/')
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['status'], 'Not authenticated')


@pytest.mark.django_db
class TestClearCacheView(TestCase):
    """Test clear all cache view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.admin_role, _ = Role.objects.get_or_create(name="admin")
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123"
        )
        self.admin.roles.add(self.admin_role)
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

    def test_clear_cache_requires_authentication(self):
        """Test clear cache requires authentication."""
        response = self.client.post('/cache/clear/')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['error'], 'Unauthorized')

    def test_clear_cache_requires_admin_role(self):
        """Test clear cache requires admin role."""
        self.client.login(username='student', password='testpass123')
        
        response = self.client.post('/cache/clear/')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['error'], 'Unauthorized')

    def test_clear_cache_admin_success(self):
        """Test admin can clear cache."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/cache/clear/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('cache cleared', data['status'].lower())

    def test_clear_cache_requires_post(self):
        """Test clear cache only accepts POST method."""
        self.client.login(username='admin', password='testpass123')
        
        # GET request should fail
        response = self.client.get('/cache/clear/')
        
        self.assertEqual(response.status_code, 405)  # Method not allowed

    @patch('frontend.views.cache.clear')
    def test_clear_cache_handles_error(self, mock_clear):
        """Test clear cache handles errors."""
        self.client.login(username='admin', password='testpass123')
        
        mock_clear.side_effect = Exception("Cache error")
        
        response = self.client.post('/cache/clear/')
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)


@pytest.mark.django_db
class TestProfileView(TestCase):
    """Test profile view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    def test_profile_view_requires_login(self):
        """Test profile view requires authentication."""
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_profile_view_authenticated(self):
        """Test profile view displays for authenticated users."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/profile.html')
        self.assertEqual(response.context['user'], self.user)

