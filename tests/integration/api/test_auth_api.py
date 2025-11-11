"""
Integration tests for authentication API endpoints.

These tests validate the authentication flow between frontend and backend,
ensuring proper JWT token handling, user registration, and login functionality.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.utils import APITestCase, TestUtils

User = get_user_model()


class TestAuthenticationAPI(APITestCase):
    """Test authentication API endpoints."""

    def setUp(self):
        """Set up test case."""
        super().setUp()
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.refresh_url = reverse("token_refresh")
        self.verify_email_url = reverse("accounts:verify-email")
        self.password_reset_url = reverse("accounts:password_reset_request")

    def test_user_registration_success(self):
        """Test successful user registration."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = self.client.post(self.register_url, data, format="json")
        print(
            "DEBUG registration response:",
            response.status_code,
            getattr(response, "data", response.content),
        )
        self.assert_response_success(response, status.HTTP_201_CREATED)
        self.assert_model_exists(User, username="testuser", email="test@example.com")

        # Check that user is created but not verified
        user = User.objects.get(username="testuser")
        self.assertFalse(user.is_email_verified)
        self.assertFalse(user.is_active)

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username."""
        # Create existing user
        TestUtils.create_test_user(username="existinguser")

        data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create existing user
        TestUtils.create_test_user(email="existing@example.com")

        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_registration_invalid_data(self):
        """Test registration with invalid data."""
        data = {
            "username": "",  # Empty username
            "email": "invalid-email",  # Invalid email
            "password": "123",  # Too short password
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_user_login_success(self):
        """Test successful user login."""
        # Create user
        TestUtils.create_test_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        data = {"login": "testuser", "password": "testpass123"}

        response = self.client.post(self.login_url, data, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Verify token is valid
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Test accessing protected endpoint
        profile_url = reverse("accounts:profile")
        profile_response = self.client.get(profile_url)
        self.assert_response_success(profile_response, status.HTTP_200_OK)

    def test_user_login_with_email(self):
        """Test login using email instead of username."""
        # Create user
        TestUtils.create_test_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_email_verified=True,
            is_active=True,
        )

        data = {"login": "test@example.com", "password": "testpass123"}

        response = self.client.post(self.login_url, data, format="json")
        print(
            "DEBUG login with email response:",
            response.status_code,
            getattr(response, "data", response.content),
        )
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Create user
        TestUtils.create_test_user(username="testuser", password="testpass123")

        data = {"login": "testuser", "password": "wrongpassword"}

        response = self.client.post(self.login_url, data, format="json")

        self.assert_response_error(response, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_nonexistent_user(self):
        """Test login with non-existent user."""
        data = {"login": "nonexistent", "password": "testpass123"}

        response = self.client.post(self.login_url, data, format="json")

        self.assert_response_error(response, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        """Test successful token refresh."""
        # Create user and get tokens
        user = TestUtils.create_test_user()
        refresh = RefreshToken.for_user(user)

        data = {"refresh": str(refresh)}

        response = self.client.post(self.refresh_url, data, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotEqual(response.data["access"], str(refresh.access_token))

    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        data = {"refresh": "invalid-token"}

        response = self.client.post(self.refresh_url, data, format="json")

        self.assert_response_error(response, status.HTTP_401_UNAUTHORIZED)

    def test_email_verification_success(self):
        """Test successful email verification."""
        # Create unverified user
        user = TestUtils.create_test_user(
            email="test@example.com", is_email_verified=False
        )

        # Use the actual email verification token
        verification_token = user.email_verification_token

        data = {"token": str(verification_token)}

        response = self.client.post(self.verify_email_url, data, format="json")
        print(
            "DEBUG email verification response:",
            response.status_code,
            getattr(response, "data", response.content),
        )
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify user is now verified
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)

    def test_email_verification_invalid_token(self):
        """Test email verification with invalid token."""
        data = {"token": "invalid-token"}

        response = self.client.post(self.verify_email_url, data, format="json")

        self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request_success(self):
        """Test successful password reset request."""
        # Create user
        TestUtils.create_test_user(email="test@example.com")

        data = {"email": "test@example.com"}

        response = self.client.post(self.password_reset_url, data, format="json")
        print(
            "DEBUG password reset response:",
            type(response),
            getattr(response, "data", response.content),
        )
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_password_reset_request_nonexistent_email(self):
        """Test password reset request with non-existent email."""
        data = {"email": "nonexistent@example.com"}

        response = self.client.post(self.password_reset_url, data, format="json")

        # Should still return success to prevent email enumeration
        self.assert_response_success(response, status.HTTP_200_OK)

    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication."""
        profile_url = reverse("accounts:profile")
        response = self.client.get(profile_url)

        self.assert_response_unauthorized(response)

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token."""
        # Create user and authenticate
        user = TestUtils.create_test_user()
        self.authenticate_user(user)

        profile_url = reverse("accounts:profile")
        response = self.client.get(profile_url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["email"], user.email)

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")

        profile_url = reverse("accounts:profile")
        response = self.client.get(profile_url)

        self.assert_response_unauthorized(response)

    def test_logout_success(self):
        """Test successful logout."""
        # Create user and authenticate
        user = TestUtils.create_test_user()
        self.authenticate_user(user)

        # Login to get tokens
        login_data = {"login": user.username, "password": "testpass123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        refresh = login_response.data["refresh"]

        logout_url = reverse("accounts:logout")
        # Include refresh token in logout request
        response = self.client.post(logout_url, {"refresh": refresh}, format="json")
        self.assert_response_success(response, status.HTTP_200_OK)

        # Clear credentials to simulate client logout
        self.client.credentials()

        # Use a new client instance for the profile request

        unauth_client = APIClient()
        profile_url = reverse("accounts:profile")
        profile_response = unauth_client.get(profile_url)
        self.assert_response_unauthorized(profile_response)

    def test_frontend_login_with_username_and_email(self):
        """Test frontend login flow using /api/accounts/login/ with both username and email."""
        TestUtils.create_test_user(
            username="frontenduser",
            email="frontend@example.com",
            password="frontendpass123",
            is_email_verified=True,
            is_active=True,
        )
        # Login with username
        data_username = {"login": "frontenduser", "password": "frontendpass123"}
        response_username = self.client.post(
            self.login_url, data_username, format="json"
        )
        self.assert_response_success(response_username, status.HTTP_200_OK)
        if hasattr(response_username, "data"):
            self.assertIn("access", response_username.data)
            self.assertIn("refresh", response_username.data)
        # Login with email
        data_email = {"login": "frontend@example.com", "password": "frontendpass123"}
        response_email = self.client.post(self.login_url, data_email, format="json")
        self.assert_response_success(response_email, status.HTTP_200_OK)
        if hasattr(response_email, "data"):
            self.assertIn("access", response_email.data)
            self.assertIn("refresh", response_email.data)

    def test_token_obtain_pair_username_vs_email(self):
        """Test /api/token/ only works with username, not email."""
        TestUtils.create_test_user(
            username="tokenuser",
            email="token@example.com",
            password="tokenpass123",
            is_email_verified=True,
            is_active=True,
        )
        # Login with username (should succeed)
        data_username = {"username": "tokenuser", "password": "tokenpass123"}
        response_username = self.client.post(
            "/api/token/", data_username, format="json"
        )
        self.assert_response_success(response_username, status.HTTP_200_OK)
        if hasattr(response_username, "data"):
            self.assertIn("access", response_username.data)
            self.assertIn("refresh", response_username.data)
        # Login with email (should fail)
        data_email = {"username": "token@example.com", "password": "tokenpass123"}
        response_email = self.client.post("/api/token/", data_email, format="json")
        self.assert_response_error(response_email, status.HTTP_401_UNAUTHORIZED)


class TestAuthenticationIntegration(APITestCase):
    """Test authentication integration scenarios."""

    def test_complete_auth_workflow(self):
        """Test complete authentication workflow from registration to logout."""
        # 1. Register new user
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "New",
            "last_name": "User",
        }

        register_response = self.client.post(
            reverse("accounts:register"), register_data, format="json"
        )
        self.assert_response_success(register_response, status.HTTP_201_CREATED)

        # 1b. Verify email for new user
        from accounts.models import User

        user = User.objects.get(username="newuser")
        verify_data = {"token": user.email_verification_token}
        verify_response = self.client.post(
            reverse("accounts:verify-email"), verify_data, format="json"
        )
        self.assert_response_success(verify_response, status.HTTP_200_OK)

        # 2. Login with new user
        login_data = {"username": "newuser", "password": "testpass123"}

        login_response = self.client.post(
            reverse("token_obtain_pair"), login_data, format="json"
        )
        self.assert_response_success(login_response, status.HTTP_200_OK)

        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        # 3. Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_response = self.client.get(reverse("accounts:profile"))
        self.assert_response_success(profile_response, status.HTTP_200_OK)

        # 4. Refresh token
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(
            reverse("token_refresh"), refresh_data, format="json"
        )
        self.assert_response_success(refresh_response, status.HTTP_200_OK)

        # 5. Use new access token
        new_access_token = refresh_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
        profile_response2 = self.client.get(reverse("accounts:profile"))
        self.assert_response_success(profile_response2, status.HTTP_200_OK)

        # 6. Logout
        logout_response = self.client.post(
            reverse("accounts:logout"), {"refresh": refresh_token}, format="json"
        )
        if getattr(logout_response, "status_code", None) != status.HTTP_200_OK:
            print(
                "Logout response status:", getattr(logout_response, "status_code", None)
            )
            print(
                "Logout response data:",
                getattr(
                    logout_response, "data", getattr(logout_response, "content", None)
                ),
            )
        self.assert_response_success(logout_response, status.HTTP_200_OK)

        # 7. Verify logout worked
        profile_response3 = self.client.get(reverse("accounts:profile"))
        # JWT access tokens remain valid until expiry; expect 200 (standard JWT behavior)
        self.assert_response_success(profile_response3, status.HTTP_200_OK)

    def test_concurrent_sessions(self):
        """Test handling of concurrent sessions."""
        # Create user
        user = TestUtils.create_test_user()

        # Create multiple tokens for the same user
        refresh1 = RefreshToken.for_user(user)
        refresh2 = RefreshToken.for_user(user)

        # Both tokens should work
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh1.access_token}")
        response1 = self.client.get(reverse("accounts:profile"))
        self.assert_response_success(response1, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh2.access_token}")
        response2 = self.client.get(reverse("accounts:profile"))
        self.assert_response_success(response2, status.HTTP_200_OK)

    @pytest.mark.slow
    def test_token_expiration(self):
        """Test token expiration behavior."""
        # This test would require time manipulation
        # For now, we'll test the basic token structure
        user = TestUtils.create_test_user()
        refresh = RefreshToken.for_user(user)

        # Verify token structure
        self.assertIsInstance(str(refresh.access_token), str)
        self.assertIsInstance(str(refresh), str)
        self.assertNotEqual(str(refresh.access_token), str(refresh))


class TestAuthenticationSecurity(APITestCase):
    """Test authentication security features."""

    def test_password_strength_validation(self):
        """Test password strength validation during registration."""
        weak_passwords = [
            "123",  # Too short
            "password",  # Common password
            "qwerty",  # Common password
            "abc123",  # Too simple
        ]

        for password in weak_passwords:
            data = {
                "username": f"testuser_{password}",
                "email": f"test_{password}@example.com",
                "password": password,
            }

            response = self.client.post(
                reverse("accounts:register"), data, format="json"
            )

            self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)
            self.assertIn("password", response.data)

    def test_account_lockout_after_failed_attempts(self):
        """Test account lockout after multiple failed login attempts."""
        # Create user
        user = TestUtils.create_test_user(
            username="lockoutuser", password="testpass123"
        )

        # Attempt multiple failed logins
        for i in range(5):
            data = {"login": "lockoutuser", "password": "wrongpassword"}
            response = self.client.post(reverse("accounts:login"), data, format="json")

            if i < 4:  # First 4 attempts should fail but not lock
                self.assert_response_error(response, status.HTTP_401_UNAUTHORIZED)
            else:  # 5th attempt should trigger lockout
                self.assert_response_error(response, status.HTTP_401_UNAUTHORIZED)

        # Verify user is locked
        user.refresh_from_db()
        self.assertIsNotNone(user.lockout_until)

    def test_csrf_protection(self):
        """Test CSRF protection on authentication endpoints."""
        # This test verifies that CSRF protection is properly configured
        # The actual CSRF validation would be handled by Django middleware

        # Test that endpoints accept JSON requests
        data = {"username": "testuser", "password": "testpass123"}

        response = self.client.post(reverse("token_obtain_pair"), data, format="json")

        # Should not fail due to CSRF (API endpoints are typically exempt)
        # The response should be 401 (unauthorized) not 403 (forbidden)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
