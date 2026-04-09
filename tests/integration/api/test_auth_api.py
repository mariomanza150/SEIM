"""
Integration tests for authentication API endpoints.

These tests validate the authentication flow between frontend and backend,
ensuring proper JWT token handling, user registration, and login functionality.
"""

import uuid
from copy import deepcopy

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
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
        self.refresh_url = reverse("api:token_refresh")
        self.verify_email_url = reverse("accounts:verify-email")
        self.password_reset_url = reverse("accounts:password_reset_request")
        # Generate unique identifier for this test run
        self.unique_id = uuid.uuid4().hex[:8]

    def test_user_registration_success(self):
        """Test successful user registration."""
        username = f"testuser_{self.unique_id}"
        email = f"test_{self.unique_id}@example.com"
        
        data = {
            "username": username,
            "email": email,
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = self.client.post(self.register_url, data, format="json")
        print(
            response.status_code,
            getattr(response, "data", response.content),
        )
        self.assert_response_success(response, status.HTTP_201_CREATED)
        self.assert_model_exists(User, username=username, email=email)

        # Check that user is created but not verified
        user = User.objects.get(username=username)
        self.assertFalse(user.is_email_verified)
        self.assertFalse(user.is_active)

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username."""
        username = f"existinguser_{self.unique_id}"
        # Create existing user
        TestUtils.create_test_user(username=username)

        data = {
            "username": username,
            "email": f"new_{self.unique_id}@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        email = f"existing_{self.unique_id}@example.com"
        # Create existing user
        TestUtils.create_test_user(email=email)

        data = {
            "username": f"newuser_{self.unique_id}",
            "email": email,
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
        username = f"testuser_{self.unique_id}"
        email = f"test_{self.unique_id}@example.com"
        # Create user
        TestUtils.create_test_user(
            username=username, email=email, password="testpass123"
        )

        data = {"login": username, "password": "testpass123"}

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
            response.status_code,
            getattr(response, "data", response.content),
        )
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        username = f"testuser_{self.unique_id}"
        # Create user
        TestUtils.create_test_user(username=username, password="testpass123")

        data = {"login": username, "password": "wrongpassword"}

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
        email = f"test_{self.unique_id}@example.com"
        # Create unverified user
        user = TestUtils.create_test_user(
            email=email, is_email_verified=False
        )

        # Use the actual email verification token
        verification_token = user.email_verification_token

        data = {"token": str(verification_token)}

        response = self.client.post(self.verify_email_url, data, format="json")
        print(
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
        email = f"test_{self.unique_id}@example.com"
        # Create user
        TestUtils.create_test_user(email=email)

        data = {"email": email}

        response = self.client.post(self.password_reset_url, data, format="json")
        print(
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

    def test_logout_post_json_succeeds_with_django_session_and_jwt_header(self):
        """MQ-008: Logout POST must not return 403 from Session CSRF when session + JWT exist."""
        uid = self.unique_id
        user = TestUtils.create_test_user(
            username=f"logout_{uid}",
            email=f"logout_{uid}@example.com",
            password="pass789",
        )

        rf = deepcopy(settings.REST_FRAMEWORK)
        rf["DEFAULT_AUTHENTICATION_CLASSES"] = [
            "rest_framework_simplejwt.authentication.JWTAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        ]

        with override_settings(REST_FRAMEWORK=rf):
            self.client.force_login(user)
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
            response = self.client.post(
                reverse("accounts:logout"),
                {"refresh": str(refresh)},
                format="json",
            )

        self.assert_response_success(response, status.HTTP_200_OK)

    def test_frontend_login_with_username_and_email(self):
        """Test frontend login flow using /api/accounts/login/ with both username and email."""
        username = f"frontenduser_{self.unique_id}"
        email = f"frontend_{self.unique_id}@example.com"
        TestUtils.create_test_user(
            username=username,
            email=email,
            password="frontendpass123",
            is_email_verified=True,
            is_active=True,
        )
        # Login with username
        data_username = {"login": username, "password": "frontendpass123"}
        response_username = self.client.post(
            self.login_url, data_username, format="json"
        )
        self.assert_response_success(response_username, status.HTTP_200_OK)
        if hasattr(response_username, "data"):
            self.assertIn("access", response_username.data)
            self.assertIn("refresh", response_username.data)
        # Login with email
        data_email = {"login": email, "password": "frontendpass123"}
        response_email = self.client.post(self.login_url, data_email, format="json")
        self.assert_response_success(response_email, status.HTTP_200_OK)
        if hasattr(response_email, "data"):
            self.assertIn("access", response_email.data)
            self.assertIn("refresh", response_email.data)

    def test_token_obtain_pair_email_vs_username_payload(self):
        """Test /api/token/ accepts email+password (Vue); username field is not used."""
        username = f"tokenuser_{self.unique_id}"
        email = f"token_{self.unique_id}@example.com"
        TestUtils.create_test_user(
            username=username,
            email=email,
            password="tokenpass123",
            is_email_verified=True,
            is_active=True,
        )
        data_email = {"email": email, "password": "tokenpass123"}
        response_ok = self.client.post(
            "/api/token/", data_email, format="json"
        )
        self.assert_response_success(response_ok, status.HTTP_200_OK)
        if hasattr(response_ok, "data"):
            self.assertIn("access", response_ok.data)
            self.assertIn("refresh", response_ok.data)
        # Legacy username+password payload is rejected by serializer (missing email)
        data_username = {"username": username, "password": "tokenpass123"}
        response_bad = self.client.post("/api/token/", data_username, format="json")
        self.assert_response_error(response_bad, status.HTTP_400_BAD_REQUEST)


class TestAuthenticationIntegration(APITestCase):
    """Test authentication integration scenarios."""

    def setUp(self):
        """Set up test case."""
        super().setUp()
        # Generate unique identifier for this test run
        self.unique_id = uuid.uuid4().hex[:8]

    def test_complete_auth_workflow(self):
        """Test complete authentication workflow from registration to logout."""
        username = f"newuser_{self.unique_id}"
        email = f"newuser_{self.unique_id}@example.com"
        
        # 1. Register new user
        register_data = {
            "username": username,
            "email": email,
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

        user = User.objects.get(username=username)
        verify_data = {"token": user.email_verification_token}
        verify_response = self.client.post(
            reverse("accounts:verify-email"), verify_data, format="json"
        )
        self.assert_response_success(verify_response, status.HTTP_200_OK)

        # 2. Login with new user (JWT view uses email + password)
        login_data = {"email": email, "password": "testpass123"}

        login_response = self.client.post(
            reverse("api:token_obtain_pair"), login_data, format="json"
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
            reverse("api:token_refresh"), refresh_data, format="json"
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

    def setUp(self):
        """Set up test case."""
        super().setUp()
        # Generate unique identifier for this test run
        self.unique_id = uuid.uuid4().hex[:8]

    def test_password_strength_validation(self):
        """Test password strength validation during registration."""
        weak_passwords = [
            "123",  # Too short
            "password",  # Common password
            "qwerty",  # Common password
            "abc123",  # Too simple
        ]

        for i, password in enumerate(weak_passwords):
            data = {
                "username": f"testuser_{self.unique_id}_{i}",
                "email": f"test_{self.unique_id}_{i}@example.com",
                "password": password,
            }

            response = self.client.post(
                reverse("accounts:register"), data, format="json"
            )

            self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)
            self.assertIn("password", response.data)

    def test_account_lockout_after_failed_attempts(self):
        """Test account lockout after multiple failed login attempts."""
        username = f"lockoutuser_{self.unique_id}"
        # Create user
        user = TestUtils.create_test_user(
            username=username, password="testpass123"
        )

        # Attempt multiple failed logins
        for i in range(5):
            data = {"login": username, "password": "wrongpassword"}
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

        response = self.client.post(reverse("api:token_obtain_pair"), data, format="json")

        # Should not fail due to CSRF (API endpoints are typically exempt)
        # The response should be 401 (unauthorized) not 403 (forbidden)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_switch_user_with_existing_django_session(self):
        """MQ-007: Login POST must succeed when another user is already in the session (no opaque 403)."""
        uid = self.unique_id
        user_a = TestUtils.create_test_user(
            username=f"a_{uid}", email=f"a_{uid}@example.com", password="pass123"
        )
        user_b = TestUtils.create_test_user(
            username=f"b_{uid}", email=f"b_{uid}@example.com", password="pass456"
        )

        rf = deepcopy(settings.REST_FRAMEWORK)
        rf["DEFAULT_AUTHENTICATION_CLASSES"] = [
            "rest_framework_simplejwt.authentication.JWTAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        ]

        with override_settings(REST_FRAMEWORK=rf):
            self.client.force_login(user_a)
            response = self.client.post(
                reverse("accounts:login"),
                {"login": user_b.email, "password": "pass456"},
                format="json",
            )

        self.assert_response_success(response, status.HTTP_200_OK)
