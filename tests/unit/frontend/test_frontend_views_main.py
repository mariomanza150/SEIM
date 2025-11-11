from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.cache import cache
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from accounts.models import Role
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


class FrontendViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        # Create roles first
        self.student_role = Role.objects.get_or_create(name='student')[0]
        self.coordinator_role = Role.objects.get_or_create(name='coordinator')[0]
        self.admin_role = Role.objects.get_or_create(name='admin')[0]

        # Create test users
        self.student_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123'
        )
        self.student_user.roles.add(self.student_role)

        self.coordinator_user = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='testpass123'
        )
        self.coordinator_user.roles.add(self.coordinator_role)

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_user.roles.add(self.admin_role)

        # Create test program
        from datetime import date, timedelta
        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        self.program = Program.objects.create(
            name='Test Program',
            description='Test Description',
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        # Create test application
        self.application = Application.objects.create(
            student=self.student_user,
            program=self.program,
            status=ApplicationStatus.objects.get_or_create(name='draft')[0]
        )

    def tearDown(self):
        cache.clear()

    def _add_messages_to_request(self, request):
        """Helper to add messages framework to request."""
        request.session = {}
        messages = FallbackStorage(request)
        request._messages = messages

    def test_home_view_authenticated_user(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)

    @patch('frontend.views.Program.objects.filter')
    @patch('frontend.views.Application.objects.count')
    def test_home_view_unauthenticated_user(self, mock_app_count, mock_program_filter):
        mock_program_filter.return_value.count.return_value = 5
        mock_app_count.return_value = 10
        response = self.client.get(reverse('frontend:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_programs'], 5)
        self.assertEqual(response.context['total_applications'], 10)

    @patch('frontend.views.Program.objects.filter')
    @patch('frontend.views.Application.objects.count')
    def test_home_view_exception_handling(self, mock_app_count, mock_program_filter):
        mock_program_filter.side_effect = Exception("Database error")
        mock_app_count.side_effect = Exception("Database error")
        response = self.client.get(reverse('frontend:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_programs'], 0)
        self.assertEqual(response.context['total_applications'], 0)

    def test_login_view_authenticated_user(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)

    def test_login_view_unauthenticated_user(self):
        response = self.client.get(reverse('frontend:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_authenticated_user(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:register'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)

    def test_register_view_unauthenticated_user(self):
        response = self.client.get(reverse('frontend:register'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        self.assertEqual(response.cookies['clear_jwt_tokens'].value, 'true')

    def test_dashboard_view(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_programs_view_authenticated(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:programs'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('programs', response.context)

    def test_applications_view_student(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:applications'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('applications', response.context)

    def test_applications_view_coordinator(self):
        self.client.force_login(self.coordinator_user)
        response = self.client.get(reverse('frontend:applications'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('applications', response.context)

    def test_analytics_view_admin_access(self):
        self.client.force_login(self.admin_user)
        with patch('frontend.views.AnalyticsService.get_dashboard_metrics') as mock_metrics:
            mock_metrics.return_value = {'total_applications': 10}
            response = self.client.get(reverse('frontend:analytics'))
            self.assertEqual(response.status_code, 200)
            self.assertIn('metrics', response.context)
            self.assertEqual(response.context['metrics'], {'total_applications': 10})

    def test_analytics_view_exception_handling(self):
        self.client.force_login(self.admin_user)
        with patch('frontend.views.AnalyticsService.get_dashboard_metrics') as mock_metrics:
            mock_metrics.side_effect = Exception("Service error")
            response = self.client.get(reverse('frontend:analytics'))
            self.assertEqual(response.status_code, 200)
            self.assertIn('metrics', response.context)
            self.assertEqual(response.context['metrics'], {})

    def test_admin_dashboard_view_admin_access(self):
        self.client.force_login(self.admin_user)
        with patch('frontend.views.AnalyticsService.get_dashboard_metrics') as mock_metrics, \
             patch('frontend.views.AnalyticsService.get_program_metrics') as mock_program_metrics:
            mock_metrics.return_value = {'total_applications': 10}
            mock_program_metrics.return_value = {'active_programs': 5}
            response = self.client.get(reverse('frontend:admin_dashboard'))
            self.assertEqual(response.status_code, 200)
            self.assertIn('metrics', response.context)
            self.assertIn('program_metrics', response.context)

    def test_admin_dashboard_view_non_admin_redirect(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)

    def test_admin_dashboard_view_unauthenticated_redirect(self):
        response = self.client.get(reverse('frontend:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)

    def test_invalidate_user_cache_authenticated(self):
        self.client.force_login(self.student_user)
        with patch('core.cache.invalidate_cache_pattern') as mock_invalidate:
            response = self.client.get(reverse('frontend:invalidate_cache'))
            self.assertEqual(response.status_code, 200)
            mock_invalidate.assert_called_once()

    def test_invalidate_user_cache_unauthenticated(self):
        response = self.client.get(reverse('frontend:invalidate_cache'))
        self.assertEqual(response.status_code, 401)

    def test_clear_cache_view_admin_post(self):
        self.client.force_login(self.admin_user)
        with patch('frontend.views.cache.clear') as mock_clear:
            response = self.client.post(reverse('frontend:clear_cache'))
            self.assertEqual(response.status_code, 200)
            mock_clear.assert_called_once()

    def test_clear_cache_view_non_admin(self):
        self.client.force_login(self.student_user)
        response = self.client.post(reverse('frontend:clear_cache'))
        self.assertEqual(response.status_code, 403)

    def test_clear_cache_view_unauthenticated(self):
        response = self.client.post(reverse('frontend:clear_cache'))
        self.assertEqual(response.status_code, 403)

    def test_clear_cache_view_exception_handling(self):
        self.client.force_login(self.admin_user)
        with patch('frontend.views.cache.clear') as mock_clear:
            mock_clear.side_effect = Exception("Cache error")
            response = self.client.post(reverse('frontend:clear_cache'))
            self.assertEqual(response.status_code, 500)

    def test_profile_view(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.student_user)

    def test_settings_view(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('frontend:settings'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.student_user)
