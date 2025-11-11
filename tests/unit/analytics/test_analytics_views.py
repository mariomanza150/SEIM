from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class TestAnalyticsViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )
        # Create JWT token for API authentication
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_dashboard_view_get(self):
        """Test dashboard view GET request - should redirect to login"""
        url = reverse('analytics:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_view_authenticated(self):
        """Test dashboard view with authenticated user"""
        self.client.force_login(self.user)
        url = reverse('analytics:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reports_view_get(self):
        """Test reports view GET request - should require authentication"""
        url = reverse('analytics:reports')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_reports_view_authenticated(self):
        """Test reports view with authenticated user"""
        self.api_client.force_authenticate(user=self.user)
        url = reverse('analytics:reports')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_metrics_api_view_get(self):
        """Test metrics API view GET request - requires authentication"""
        url = reverse('analytics:metrics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_metrics_api_view_authenticated(self):
        """Test metrics API view with authenticated user"""
        self.api_client.force_authenticate(user=self.user)
        url = reverse('analytics:metrics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_metrics_api_view_jwt_authenticated(self):
        """Test metrics API view with JWT authentication"""
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        url = reverse('analytics:metrics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_application_analytics_view_get(self):
        """Test application analytics view GET request - requires authentication"""
        url = reverse('analytics:application-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 401)  # Requires authentication

    def test_application_analytics_view_authenticated(self):
        """Test application analytics view with authenticated user"""
        self.api_client.force_authenticate(user=self.user)
        url = reverse('analytics:application-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_analytics_view_get(self):
        """Test user analytics view GET request - requires authentication"""
        url = reverse('analytics:user-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 401)  # Requires authentication

    def test_user_analytics_view_authenticated(self):
        """Test user analytics view with authenticated user"""
        self.api_client.force_authenticate(user=self.user)
        url = reverse('analytics:user-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_program_analytics_view_get(self):
        """Test program analytics view GET request - requires authentication"""
        url = reverse('analytics:program-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 401)  # Requires authentication

    def test_program_analytics_view_authenticated(self):
        """Test program analytics view with authenticated user"""
        self.api_client.force_authenticate(user=self.user)
        url = reverse('analytics:program-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_document_analytics_view_get(self):
        """Test document analytics view GET request - requires authentication"""
        url = reverse('analytics:document-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 401)  # Requires authentication

    def test_document_analytics_view_authenticated(self):
        """Test document analytics view with authenticated user"""
        self.api_client.force_authenticate(user=self.user)
        url = reverse('analytics:document-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_notification_analytics_view_get(self):
        """Test notification analytics view GET request - requires authentication"""
        url = reverse('analytics:notification-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 401)  # Requires authentication

    def test_notification_analytics_view_authenticated(self):
        """Test notification analytics view with authenticated user"""
        self.api_client.force_authenticate(user=self.user)
        url = reverse('analytics:notification-analytics')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 200)
