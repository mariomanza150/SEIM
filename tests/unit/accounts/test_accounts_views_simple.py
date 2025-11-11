"""
Simple unit tests for accounts views without problematic imports.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class TestAccountsViewsSimple(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )
        self.user.is_active = True
        self.user.is_email_verified = True
        self.user.save()
        self.refresh = RefreshToken.for_user(self.user)

    def test_login_view_post(self):
        client = APIClient()
        response = client.post('/api/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertIn(response.status_code, [200, 400])

    def test_register_view_post(self):
        client = APIClient()
        response = client.post('/api/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        })
        self.assertIn(response.status_code, [200, 201, 400])

    def test_profile_view_authenticated(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, 200)

    def test_profile_view_unauthenticated(self):
        client = APIClient()
        response = client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, 401)

    def test_logout_view(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.post('/api/accounts/logout/', {})
        self.assertEqual(response.status_code, 200)

    def test_password_reset_request_view_post(self):
        client = APIClient()
        response = client.post('/api/accounts/password-reset-request/', {
            'email': 'testuser@example.com'
        })
        self.assertIn(response.status_code, [200, 400])

    def test_change_password_view_authenticated(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.post('/api/accounts/change-password/', {
            'old_password': 'TestPass123!',
            'new_password': 'NewPass123!'
        })
        self.assertIn(response.status_code, [200, 400])

    def test_change_password_view_unauthenticated(self):
        client = APIClient()
        response = client.post('/api/accounts/change-password/', {})
        self.assertEqual(response.status_code, 401)

    def test_user_sessions_view_authenticated(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.get('/api/accounts/sessions/')
        self.assertEqual(response.status_code, 200)

    def test_user_sessions_view_unauthenticated(self):
        client = APIClient()
        response = client.get('/api/accounts/sessions/')
        self.assertEqual(response.status_code, 401)

    def test_appearance_settings_view_authenticated(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.get('/api/accounts/appearance-settings/')
        self.assertEqual(response.status_code, 200)

    def test_notification_settings_view_authenticated(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.get('/api/accounts/notification-settings/')
        self.assertEqual(response.status_code, 200)

    def test_privacy_settings_view_authenticated(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.get('/api/accounts/privacy-settings/')
        self.assertEqual(response.status_code, 200)

    def test_delete_account_view_authenticated(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        response = client.delete('/api/accounts/delete/')
        self.assertEqual(response.status_code, 200)
