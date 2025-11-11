"""
Unit tests for accounts views.
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import Permission, Role, UserSession, UserSettings

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.views
class TestUserViewSet(APITestCase):
    """Test cases for UserViewSet."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.regular_user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="userpass123",
        )
        self.client = APIClient()

    def test_list_users_admin_access(self):
        """Test that admin can list users."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("accounts:user-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_list_users_regular_user_denied(self):
        """Test that regular user cannot list users."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("accounts:user-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_user_admin_access(self):
        """Test that admin can retrieve user details."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("accounts:user-detail", args=[self.regular_user.id])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "user"

    def test_create_user_admin_access(self):
        """Test that admin can create users."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("accounts:user-list")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
        }
        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
@pytest.mark.views
class TestProfileViewSet(APITestCase):
    """Test cases for ProfileViewSet."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
        )
        self.client = APIClient()

    def test_list_profiles_admin_access(self):
        """Test that admin can list all profiles."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("accounts:profile-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_list_profiles_regular_user_own_only(self):
        """Test that regular user can only see their own profile."""
        self.client.force_authenticate(user=self.user)
        url = reverse("accounts:profile-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]["username"] == "testuser"

    def test_retrieve_profile(self):
        """Test retrieving profile details."""
        self.client.force_authenticate(user=self.user)
        url = reverse("accounts:profile-detail", args=[self.user.profile.id])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"


@pytest.mark.django_db
@pytest.mark.views
class TestRegistrationView(APITestCase):
    """Test cases for RegistrationView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.url = reverse("accounts:register")

    def test_registration_success(self):
        """Test successful user registration."""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpass123",
            "password2": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "Registration successful" in response.data["detail"]
        assert User.objects.filter(username="newuser").exists()

    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpass123",
            "password2": "differentpass",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data


@pytest.mark.django_db
@pytest.mark.views
class TestEmailVerificationView(APITestCase):
    """Test cases for EmailVerificationView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.url = reverse("accounts:verify-email")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_active=False,
            is_email_verified=False,
        )
        self.user.email_verification_token = "test_token_123"
        self.user.save()

    def test_email_verification_success(self):
        """Test successful email verification."""
        data = {"token": "test_token_123"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "Email verified successfully" in response.data["detail"]

        self.user.refresh_from_db()
        assert self.user.is_email_verified is True
        assert self.user.is_active is True

    def test_email_verification_invalid_token(self):
        """Test email verification with invalid token."""
        data = {"token": "invalid_token"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.views
class TestLoginView(APITestCase):
    """Test cases for LoginView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.url = reverse("accounts:login")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_email_verified=True,
        )

    def test_login_success(self):
        """Test successful login."""
        data = {"login": "testuser", "password": "testpass123"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "refresh" in response.data
        assert "access" in response.data
        assert "user" in response.data

    def test_login_with_email(self):
        """Test login with email."""
        data = {"login": "test@example.com", "password": "testpass123"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "refresh" in response.data

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {"login": "testuser", "password": "wrongpass"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unverified_email(self):
        """Test login with unverified email."""
        self.user.is_email_verified = False
        self.user.save()

        data = {"login": "testuser", "password": "testpass123"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_locked_account(self):
        """Test login with locked account."""
        self.user.lockout_until = timezone.now() + timedelta(minutes=30)
        self.user.save()

        data = {"login": "testuser", "password": "testpass123"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_device_info_mobile(self):
        """Test device info extraction for mobile."""
        from accounts.views import LoginView
        view = LoginView()
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        device = view._get_device_info(user_agent)
        assert device == "Mobile"

    def test_get_device_info_desktop(self):
        """Test device info extraction for desktop."""
        from accounts.views import LoginView
        view = LoginView()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        device = view._get_device_info(user_agent)
        assert device == "Desktop"

    def test_get_location_info_local(self):
        """Test location info extraction for local IP."""
        from accounts.views import LoginView
        view = LoginView()
        location = view._get_location_info("127.0.0.1")
        assert location == "Local"

    def test_get_location_info_remote(self):
        """Test location info extraction for remote IP."""
        from accounts.views import LoginView
        view = LoginView()
        location = view._get_location_info("192.168.1.1")
        assert location == "Remote"


@pytest.mark.django_db
@pytest.mark.views
class TestPasswordResetRequestView(APITestCase):
    """Test cases for PasswordResetRequestView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.url = reverse("accounts:password_reset_request")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_password_reset_request_success(self):
        """Test successful password reset request."""
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "Password reset email sent" in response.data["message"]

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email."""
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(self.url, data)

        # Should still return 200 for security reasons
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.views
class TestPasswordResetConfirmView(APITestCase):
    """Test cases for PasswordResetConfirmView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.url = reverse("accounts:password_reset_confirm")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.user.email_verification_token = "reset_token_123"
        self.user.save()

    def test_password_reset_confirm_success(self):
        """Test successful password reset confirmation."""
        data = {
            "email": "test@example.com",
            "token": "reset_token_123",
            "new_password": "newpass123",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "Password has been reset successfully" in response.data["detail"]


@pytest.mark.django_db
@pytest.mark.views
class TestProfileView(APITestCase):
    """Test cases for ProfileView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Test getting user profile."""
        url = reverse("accounts:profile")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"

    def test_update_profile(self):
        """Test updating user profile."""
        url = reverse("accounts:profile")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "gpa": 3.8,
        }
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"


@pytest.mark.django_db
@pytest.mark.views
class TestLogoutView(APITestCase):
    """Test cases for LogoutView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("accounts:logout")

    def test_logout_success(self):
        """Test successful logout."""
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "Successfully logged out" in response.data["message"]


@pytest.mark.django_db
@pytest.mark.views
class TestChangePasswordView(APITestCase):
    """Test cases for ChangePasswordView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("accounts:change_password")

    def test_change_password_success(self):
        """Test successful password change."""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password2": "newpass123",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "Password changed successfully" in response.data["detail"]

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        data = {
            "old_password": "wrongpass",
            "new_password": "newpass123",
            "new_password2": "newpass123",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.views
class TestAppearanceSettingsView(APITestCase):
    """Test cases for AppearanceSettingsView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.settings = UserSettings.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_appearance_settings(self):
        """Test getting appearance settings."""
        url = reverse("accounts:appearance_settings")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "theme" in response.data
        assert "font_size" in response.data

    def test_update_appearance_settings(self):
        """Test updating appearance settings."""
        url = reverse("accounts:appearance_settings")
        data = {"theme": "dark", "font_size": "large"}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "dark"


@pytest.mark.django_db
@pytest.mark.views
class TestNotificationSettingsView(APITestCase):
    """Test cases for NotificationSettingsView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.settings = UserSettings.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_notification_settings(self):
        """Test getting notification settings."""
        url = reverse("accounts:notification_settings")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "email_applications" in response.data

    def test_update_notification_settings(self):
        """Test updating notification settings."""
        url = reverse("accounts:notification_settings")
        data = {"email_applications": False, "inapp_comments": True}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email_applications"] is False


@pytest.mark.django_db
@pytest.mark.views
class TestPrivacySettingsView(APITestCase):
    """Test cases for PrivacySettingsView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.settings = UserSettings.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_privacy_settings(self):
        """Test getting privacy settings."""
        url = reverse("accounts:privacy_settings")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "profile_public" in response.data

    def test_update_privacy_settings(self):
        """Test updating privacy settings."""
        url = reverse("accounts:privacy_settings")
        data = {"profile_public": True, "share_analytics": False}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile_public"] is True


@pytest.mark.django_db
@pytest.mark.views
class TestUserSettingsView(APITestCase):
    """Test cases for UserSettingsView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.settings = UserSettings.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_user_settings(self):
        """Test getting user settings."""
        url = reverse("accounts:user_settings")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "theme" in response.data
        assert "email_applications" in response.data

    def test_update_user_settings(self):
        """Test updating user settings."""
        url = reverse("accounts:user_settings")
        data = {"theme": "dark", "email_applications": False}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "dark"


@pytest.mark.django_db
@pytest.mark.views
class TestUserSessionsView(APITestCase):
    """Test cases for UserSessionsView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.session = UserSession.objects.create(
            user=self.user,
            session_key="test_session_123",
            device="Desktop",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_user_sessions(self):
        """Test listing user sessions."""
        url = reverse("accounts:sessions")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["device"] == "Desktop"


@pytest.mark.django_db
@pytest.mark.views
class TestRevokeSessionView(APITestCase):
    """Test cases for RevokeSessionView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.session = UserSession.objects.create(
            user=self.user,
            session_key="test_session_123",
            device="Desktop",
        )
        self.client.force_authenticate(user=self.user)

    def test_revoke_session_success(self):
        """Test successful session revocation."""
        url = reverse("accounts:revoke_session", args=[self.session.id])
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert "Session revoked successfully" in response.data["detail"]

        self.session.refresh_from_db()
        assert self.session.is_active is False


@pytest.mark.django_db
@pytest.mark.views
class TestDeleteAccountView(APITestCase):
    """Test cases for DeleteAccountView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_delete_account_success(self):
        """Test successful account deletion."""
        url = reverse("accounts:delete_account")
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert "Account deleted successfully" in response.data["detail"]

        # User should be deactivated, not deleted
        self.user.refresh_from_db()
        assert self.user.is_active is False


@pytest.mark.django_db
@pytest.mark.views
class TestRoleViewSet(APITestCase):
    """Test cases for RoleViewSet."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.role = Role.objects.create(name="test_role_viewset")
        self.client.force_authenticate(user=self.user)

    def test_list_roles(self):
        """Test listing roles."""
        url = reverse("accounts:role-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert any(role["name"] == "test_role_viewset" for role in response.data['results'])

    def test_retrieve_role(self):
        """Test retrieving role details."""
        url = reverse("accounts:role-detail", args=[self.role.id])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "test_role_viewset"


@pytest.mark.django_db
@pytest.mark.views
class TestPermissionViewSet(APITestCase):
    """Test cases for PermissionViewSet."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.permission = Permission.objects.create(name="can_edit_applications")
        self.client.force_authenticate(user=self.user)

    def test_list_permissions(self):
        """Test listing permissions."""
        url = reverse("accounts:permission-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]["name"] == "can_edit_applications"

    def test_retrieve_permission(self):
        """Test retrieving permission details."""
        url = reverse("accounts:permission-detail", args=[self.permission.id])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "can_edit_applications"


@pytest.mark.django_db
@pytest.mark.views
class TestUserSessionViewSet(APITestCase):
    """Test cases for UserSessionViewSet."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.session = UserSession.objects.create(
            user=self.user,
            session_key="test_session_123",
            device="Desktop",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_user_sessions(self):
        """Test listing user sessions."""
        url = reverse("accounts:user-session-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]["device"] == "Desktop"

    def test_delete_user_session(self):
        """Test deleting user session."""
        url = reverse("accounts:user-session-detail", args=[self.session.id])
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Do not refresh_from_db after deletion
