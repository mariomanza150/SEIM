"""
Unit tests for accounts models.
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from accounts.models import Permission, Role, UserSession, UserSettings

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.models
class TestUserModel:
    """Test cases for User model."""

    def test_user_creation(self):
        """Test basic user creation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_email_verified is False
        assert user.failed_login_attempts == 0
        assert user.lockout_until is None

    def test_user_creation_without_username(self):
        """Test user creation with email as username."""
        user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123",
        )

        assert user.username == "test@example.com"
        assert user.email == "test@example.com"

    def test_superuser_creation(self):
        """Test superuser creation."""
        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.is_active is True

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )

        assert str(user) == "testuser"
        assert user.get_full_name() == "Test User"
        assert user.get_short_name() == "Test"

    def test_email_uniqueness(self):
        """Test that email addresses must be unique."""
        User.objects.create_user(
            username="user1", email="test@example.com", password="testpass123"
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="user2", email="test@example.com", password="testpass123"
            )

    def test_email_verification_token_generation(self):
        """Test email verification token generation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Initially no token
        assert user.email_verification_token == ""

        # Generate token
        token = user.generate_email_verification_token()
        assert len(token) == 64
        assert user.email_verification_token == token

    def test_account_lockout(self):
        """Test account lockout functionality."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Initially not locked
        assert user.is_locked_out() is False

        # Increment failed attempts
        for _ in range(5):
            user.increment_failed_login_attempts()

        # After lockout, failed_login_attempts should be 0
        assert user.failed_login_attempts == 0
        assert user.is_locked_out() is True
        assert user.lockout_until is not None

    def test_account_unlock(self):
        """Test account unlock functionality."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Lock account
        user.failed_login_attempts = 5
        user.lockout_until = timezone.now() + timezone.timedelta(minutes=30)
        user.save()

        assert user.is_locked_out() is True

        # Unlock account
        user.unlock_account()
        assert user.failed_login_attempts == 0
        assert user.lockout_until is None
        assert user.is_locked_out() is False

    def test_password_validation(self):
        """Test password validation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Test valid password
        assert user.check_password("testpass123") is True

        # Test invalid password
        assert user.check_password("wrongpassword") is False

    def test_user_permissions(self):
        """Test user permissions."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Initially no special permissions
        assert user.is_staff is False
        assert user.is_superuser is False

        # Grant staff permissions
        user.is_staff = True
        user.save()
        assert user.is_staff is True

    def test_is_locked_out_with_future_lockout(self):
        """Test is_locked_out when lockout_until is in the future."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Set lockout to future time
        user.lockout_until = timezone.now() + timedelta(minutes=30)
        user.save()

        assert user.is_locked_out() is True

    def test_is_locked_out_with_past_lockout(self):
        """Test is_locked_out when lockout_until is in the past."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Set lockout to past time
        user.lockout_until = timezone.now() - timedelta(minutes=30)
        user.save()

        assert user.is_locked_out() is False

    def test_is_locked_out_with_none_lockout(self):
        """Test is_locked_out when lockout_until is None."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        user.lockout_until = None
        user.save()

        assert user.is_locked_out() is False

    def test_increment_failed_login_attempts_below_threshold(self):
        """Test increment_failed_login_attempts when below lockout threshold."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Increment 3 times (below threshold of 5)
        for _ in range(3):
            user.increment_failed_login_attempts()

        assert user.failed_login_attempts == 3
        assert user.lockout_until is None

    def test_increment_failed_login_attempts_at_threshold(self):
        """Test increment_failed_login_attempts when reaching threshold."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Set to 4 attempts, then increment
        user.failed_login_attempts = 4
        user.save()

        user.increment_failed_login_attempts()

        assert user.failed_login_attempts == 0
        assert user.lockout_until is not None

    def test_has_role_with_existing_role(self):
        """Test has_role method when user has the role."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        role = Role.objects.create(name="test_admin_role_1")
        user.roles.add(role)

        assert user.has_role("test_admin_role_1") is True

    def test_has_role_without_role(self):
        """Test has_role method when user doesn't have the role."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        assert user.has_role("admin") is False

    def test_primary_role_with_roles(self):
        """Test primary_role property when user has roles."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        role1 = Role.objects.create(name="test_admin_role_2")
        role2 = Role.objects.create(name="test_coordinator_role_2")
        user.roles.add(role1, role2)

        assert user.primary_role == "test_admin_role_2"  # First role added

    def test_primary_role_without_roles(self):
        """Test primary_role property when user has no roles."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        assert user.primary_role == "student"  # Default value

    def test_role_alias_property(self):
        """Test role property as alias for primary_role."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        role = Role.objects.create(name="test_admin_role_3")
        user.roles.add(role)

        assert user.role == user.primary_role
        assert user.role == "test_admin_role_3"


@pytest.mark.django_db
@pytest.mark.models
class TestProfileModel:
    """Test cases for Profile model."""

    def test_profile_creation(self):
        """Test profile creation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Profile should be automatically created by signal
        profile = user.profile
        profile.secondary_email = "secondary@example.com"
        profile.save()

        assert profile.user == user
        assert profile.secondary_email == "secondary@example.com"

    def test_profile_str_representation(self):
        """Test profile string representation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Profile should be automatically created by signal
        profile = user.profile
        assert str(profile) == f"Profile for {user.username}"

    def test_profile_user_relationship(self):
        """Test one-to-one relationship with user."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Profile should be automatically created by signal
        profile = user.profile
        assert profile.user == user

    def test_profile_fields(self):
        """Test profile field values."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        profile = user.profile
        profile.secondary_email = "secondary@example.com"
        profile.gpa = 3.8
        profile.language = "English"
        profile.save()

        assert profile.secondary_email == "secondary@example.com"
        assert profile.gpa == 3.8
        assert profile.language == "English"

    def test_automatic_profile_creation(self):
        """Test that profile is automatically created when user is created."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Profile should exist
        assert hasattr(user, 'profile')
        assert user.profile is not None


@pytest.mark.django_db
@pytest.mark.models
class TestUserSettingsModel:
    """Test cases for UserSettings model."""

    def test_user_settings_creation(self):
        """Test user settings creation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        settings = UserSettings.objects.create(
            user=user,
            theme='dark',
            font_size='large',
            email_applications=False,
            profile_public=True
        )

        assert settings.user == user
        assert settings.theme == 'dark'
        assert settings.font_size == 'large'
        assert settings.email_applications is False
        assert settings.profile_public is True

    def test_user_settings_defaults(self):
        """Test user settings default values."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        settings = UserSettings.objects.create(user=user)

        assert settings.theme == 'auto'
        assert settings.font_size == 'normal'
        assert settings.email_applications is True
        assert settings.email_documents is True
        assert settings.email_comments is True
        assert settings.email_programs is False
        assert settings.email_system is True
        assert settings.inapp_applications is True
        assert settings.inapp_documents is True
        assert settings.inapp_comments is True
        assert settings.inapp_programs is True
        assert settings.inapp_system is True
        assert settings.profile_public is False
        assert settings.share_analytics is True

    def test_user_settings_str_representation(self):
        """Test user settings string representation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        settings = UserSettings.objects.create(user=user)

        assert str(settings) == f"Settings for {user.username}"

    def test_user_settings_theme_choices(self):
        """Test user settings theme choices."""
        # Test valid theme choices
        for i, theme in enumerate(['light', 'dark', 'auto']):
            user = User.objects.create_user(
                username=f"testuser_theme_{i}",
                email=f"test{i}@example.com",
                password="testpass123"
            )
            settings = UserSettings.objects.create(user=user, theme=theme)
            assert settings.theme == theme

    def test_user_settings_font_size_choices(self):
        """Test user settings font size choices."""
        # Test valid font size choices
        for i, font_size in enumerate(['small', 'medium', 'large']):
            user = User.objects.create_user(
                username=f"testuser_font_{i}",
                email=f"test_font_{i}@example.com",
                password="testpass123"
            )
            settings = UserSettings.objects.create(user=user, font_size=font_size)
            assert settings.font_size == font_size

    def test_user_settings_meta(self):
        """Test user settings meta configuration."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        settings = UserSettings.objects.create(user=user)

        assert settings._meta.verbose_name == "User Settings"
        assert settings._meta.verbose_name_plural == "User Settings"


@pytest.mark.django_db
@pytest.mark.models
class TestUserSessionModel:
    """Test cases for UserSession model."""

    def test_user_session_creation(self):
        """Test user session creation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        session = UserSession.objects.create(
            user=user,
            session_key="test_session_key_123",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            ip_address="192.168.1.1",
            device="Desktop",
            location="New York, NY",
            is_active=True
        )

        assert session.user == user
        assert session.session_key == "test_session_key_123"
        assert session.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        assert session.ip_address == "192.168.1.1"
        assert session.device == "Desktop"
        assert session.location == "New York, NY"
        assert session.is_active is True

    def test_user_session_defaults(self):
        """Test user session default values."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        session = UserSession.objects.create(
            user=user,
            session_key="test_session_key_123"
        )

        assert session.is_active is True
        assert session.last_activity is not None

    def test_user_session_str_representation(self):
        """Test user session string representation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        session = UserSession.objects.create(
            user=user,
            session_key="test_session_key_123",
            device="Desktop"
        )

        assert str(session) == f"Session for {user.username} - Desktop"

    def test_user_session_meta(self):
        """Test user session meta configuration."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        session = UserSession.objects.create(
            user=user,
            session_key="test_session_key_123"
        )

        assert session._meta.verbose_name == "User Session"
        assert session._meta.verbose_name_plural == "User Sessions"
        assert session._meta.ordering == ['-last_activity']

    def test_user_session_ordering(self):
        """Test user session ordering by last_activity."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create sessions with different timestamps
        UserSession.objects.create(
            user=user,
            session_key="session1"
        )

        session2 = UserSession.objects.create(
            user=user,
            session_key="session2"
        )

        # Query should return newest first
        sessions = UserSession.objects.filter(user=user)
        assert sessions[0] == session2  # Most recent first


@pytest.mark.django_db
@pytest.mark.models
class TestRoleModel:
    """Test cases for Role model."""

    def test_role_creation(self):
        """Test role creation."""
        role = Role.objects.create(name="test_role_creation")
        assert role.name == "test_role_creation"

    def test_role_uniqueness(self):
        """Test that role names must be unique."""
        Role.objects.create(name="test_role_uniqueness")

        with pytest.raises(IntegrityError):
            Role.objects.create(name="test_role_uniqueness")

    def test_role_str_representation(self):
        """Test role string representation."""
        role = Role.objects.create(name="test_role_str")
        assert str(role) == "test_role_str"


@pytest.mark.django_db
@pytest.mark.models
class TestPermissionModel:
    """Test cases for Permission model."""

    def test_permission_creation(self):
        """Test permission creation."""
        permission = Permission.objects.create(name="can_edit_applications")
        assert permission.name == "can_edit_applications"

    def test_permission_uniqueness(self):
        """Test that permission names must be unique."""
        Permission.objects.create(name="can_edit_applications")

        with pytest.raises(IntegrityError):
            Permission.objects.create(name="can_edit_applications")

    def test_permission_role_relationship(self):
        """Test permission-role relationship."""
        role = Role.objects.create(name="test_role_permission")
        permission = Permission.objects.create(name="test_permission_role")
        permission.roles.add(role)

        assert role in permission.roles.all()
        assert permission in role.permissions.all()

    def test_permission_str_representation(self):
        """Test permission string representation."""
        permission = Permission.objects.create(name="can_view_reports")
        assert str(permission) == "can_view_reports"


@pytest.mark.django_db
@pytest.mark.models
class TestUserRoleIntegration:
    """Test cases for user-role integration."""

    def test_user_role_assignment(self):
        """Test assigning roles to users."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        role = Role.objects.create(name="test_role_assignment")

        user.roles.add(role)
        assert role in user.roles.all()
        assert user in role.users.all()

    def test_user_role_removal(self):
        """Test removing roles from users."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        role = Role.objects.create(name="test_role_removal")

        user.roles.add(role)
        assert role in user.roles.all()

        user.roles.remove(role)
        assert role not in user.roles.all()

    def test_user_has_role_method(self):
        """Test the has_role method."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        role = Role.objects.create(name="test_role_has_role_method")

        assert user.has_role("test_role_has_role_method") is False

        user.roles.add(role)
        assert user.has_role("test_role_has_role_method") is True

    def test_user_role_names(self):
        """Test getting user role names."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        role1 = Role.objects.create(name="test_role_names_1")
        role2 = Role.objects.create(name="test_role_names_2")

        user.roles.add(role1, role2)
        role_names = [role.name for role in user.roles.all()]
        assert "test_role_names_1" in role_names
        assert "test_role_names_2" in role_names


@pytest.mark.django_db
def test_user_str():
    """Test user string representation."""
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    assert str(user) == "testuser"
