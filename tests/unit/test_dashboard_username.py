"""
Unit tests for dashboard username display functionality.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile, Role

User = get_user_model()


class DashboardUsernameDisplayTest(TestCase):
    """Test that dashboard displays full name instead of username."""

    def setUp(self):
        """Set up test data."""
        # Create test user with full name
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

        # Create role and assign to user
        self.role, _ = Role.objects.get_or_create(name="student")
        self.user.roles.add(self.role)

        # Ensure profile exists
        self.profile = Profile.objects.get_or_create(user=self.user)[0]

        # Create API client
        self.client = APIClient()

        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_profile_api_returns_full_name(self):
        """Test that the profile API returns full_name field."""
        url = reverse('accounts:profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('full_name', response.data)
        self.assertEqual(response.data['full_name'], 'John Doe')
        self.assertEqual(response.data['username'], 'testuser')

    def test_profile_api_full_name_fallback(self):
        """Test that full_name returns empty string when no first/last name."""
        # Update user to have no first/last name
        self.user.first_name = ''
        self.user.last_name = ''
        self.user.save()

        url = reverse('accounts:profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('full_name', response.data)
        self.assertEqual(response.data['full_name'], '')  # Django returns empty string
        self.assertEqual(response.data['username'], 'testuser')

    def test_profile_api_full_name_with_partial_names(self):
        """Test full_name with only first name or only last name."""
        # Test with only first name
        self.user.first_name = 'John'
        self.user.last_name = ''
        self.user.save()

        url = reverse('accounts:profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], 'John')

        # Test with only last name
        self.user.first_name = ''
        self.user.last_name = 'Doe'
        self.user.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], 'Doe')
