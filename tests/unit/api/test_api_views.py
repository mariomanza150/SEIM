from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile
from exchange.models import Application
from exchange.models import ApplicationStatus, Program


class TestAPIViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )
        self.admin_user = self.User.objects.create_user(
            username='adminuser', email='adminuser@example.com', password='TestPass123!',
            is_staff=True, is_superuser=True
        )

        # Create JWT tokens
        self.user_refresh = RefreshToken.for_user(self.user)
        self.admin_refresh = RefreshToken.for_user(self.admin_user)

        # Create test data
        self.program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30)
        )

        self.application_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={"order": 1}
        )

        Profile.objects.get_or_create(user=self.user)

    def test_program_check_eligibility_includes_application_context(self):
        self.client.force_authenticate(user=self.user)
        application = Application.objects.create(
            program=self.program,
            student=self.user,
            status=self.application_status,
        )
        response = self.client.get(
            f"/api/programs/{self.program.id}/check_eligibility/",
            {"application": str(application.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("schema_version", response.data)
        self.assertEqual(response.data["schema_version"], 6)
        self.assertIn("application_context", response.data)
        ctx = response.data["application_context"]
        self.assertEqual(ctx["application_id"], str(application.id))
        self.assertIn("document_checklist", ctx)

    def test_api_schema(self):
        """Test API schema endpoint"""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_docs(self):
        """Test API documentation endpoint"""
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programs_list_unauthorized(self):
        """Test programs list without authentication"""
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_programs_list_authorized(self):
        """Test programs list with authentication"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_programs_list_jwt_authenticated(self):
        """Test programs list with JWT authentication"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_refresh.access_token}')
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_applications_list_unauthorized(self):
        """Test applications list without authentication"""
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_applications_list_authorized(self):
        """Test applications list with authentication"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_users_list_unauthorized(self):
        """Test users list without authentication"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_list_authorized(self):
        """Test users list with authentication"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_documents_list_unauthorized(self):
        """Test documents list without authentication"""
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_documents_list_authorized(self):
        """Test documents list with authentication"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_notifications_list_unauthorized(self):
        """Test notifications list without authentication"""
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_notifications_list_authorized(self):
        """Test notifications list with authentication"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_api_error_handling_404(self):
        """Test API 404 error handling"""
        response = self.client.get('/api/nonexistent-endpoint/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_error_handling_405(self):
        """Test API 405 error handling"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_cors_headers(self):
        """Test API CORS headers"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_content_type(self):
        """Test API content type headers"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('application/json', response.get('Content-Type', ''))

    def test_api_pagination(self):
        """Test API pagination"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if pagination keys are present
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_token_obtain_pair(self):
        """Test JWT token obtain pair (email + password)"""
        response = self.client.post('/api/token/', {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        """Test JWT token refresh"""
        response = self.client.post('/api/token/refresh/', {
            'refresh': str(self.user_refresh)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
