"""
Unit tests for accounts serializers.
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import (
    AllowedEmailDomain,
    HomeAcademicProgram,
    Permission,
    Role,
    SchoolFaculty,
    UserSession,
    UserSettings,
)
from accounts.serializers import (
    AppearanceSettingsSerializer,
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    NotificationSettingsSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PermissionSerializer,
    PrivacySettingsSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    RoleSerializer,
    UserSerializer,
    UserSessionSerializer,
    UserSettingsSerializer,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.serializers
class TestUserSerializer:
    """Test cases for UserSerializer."""

    def test_user_serializer_fields(self):
        """Test UserSerializer includes correct fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        serializer = UserSerializer(user)
        data = serializer.data

        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "is_active" in data
        assert "is_staff" in data
        assert "is_superuser" in data
        assert "role" in data
        assert "roles" in data
        assert data["roles"] == []

    def test_user_serializer_role_field(self):
        """Test UserSerializer role field uses primary_role."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        role = Role.objects.create(name="test_role_serializer_field")
        user.roles.add(role)

        serializer = UserSerializer(user)
        assert serializer.data["role"] == "test_role_serializer_field"

    def test_user_serializer_role_field_no_roles(self):
        """Test UserSerializer role field when user has no roles."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        serializer = UserSerializer(user)
        assert serializer.data["role"] == "student"


@pytest.mark.django_db
@pytest.mark.serializers
class TestProfileSerializer:
    """Test cases for ProfileSerializer."""

    def test_profile_serializer_fields(self):
        """Test ProfileSerializer includes correct fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        serializer = ProfileSerializer(user.profile)
        data = serializer.data

        assert "secondary_email" in data
        assert "username" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "full_name" in data
        assert "email" in data
        assert "role" in data
        assert "is_staff" in data
        assert "is_superuser" in data
        assert "gpa" in data
        assert "language" in data
        assert "missing_apply_fields" in data
        assert "grade_scale" in data["missing_apply_fields"]

    def test_profile_serializer_update(self):
        """Test ProfileSerializer update method."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        serializer = ProfileSerializer(
            user.profile,
            data={
                "first_name": "Updated",
                "last_name": "Name",
                "gpa": 3.8,
                "language": "English",
            },
            partial=True,
        )

        assert serializer.is_valid()
        updated_profile = serializer.save()

        assert updated_profile.user.first_name == "Updated"
        assert updated_profile.user.last_name == "Name"
        assert updated_profile.gpa == 3.8
        assert updated_profile.language == "English"

    def test_rejects_program_from_another_school(self):
        user = User.objects.create_user(
            username="program-test",
            email="program@example.com",
            password="testpass123",
        )
        selected_school = SchoolFaculty.objects.create(name="Engineering")
        other_school = SchoolFaculty.objects.create(name="Medicine")
        program = HomeAcademicProgram.objects.create(
            name="Medicine",
            school=other_school,
        )

        serializer = ProfileSerializer(
            user.profile,
            data={"school": selected_school.id, "home_academic_program": program.id},
            partial=True,
        )

        assert not serializer.is_valid()
        assert "home_academic_program" in serializer.errors

    def test_normalizes_blank_matricula_and_validates_clabe(self):
        user = User.objects.create_user(
            username="bank-test",
            email="bank@example.com",
            password="testpass123",
        )
        serializer = ProfileSerializer(
            user.profile,
            data={"matricula": "", "clabe": "123"},
            partial=True,
        )

        assert not serializer.is_valid()
        assert "clabe" in serializer.errors

        valid = ProfileSerializer(
            user.profile,
            data={"matricula": "", "clabe": "123456789012345678"},
            partial=True,
        )
        assert valid.is_valid(), valid.errors
        assert valid.validated_data["matricula"] is None

    def test_profile_serializer_persists_personal_fields(self):
        user = User.objects.create_user(
            username="persist-test",
            email="persist@example.com",
            password="testpass123",
        )
        school = SchoolFaculty.objects.create(name="Engineering")
        program = HomeAcademicProgram.objects.create(
            name="Computer Science", school=school
        )
        serializer = ProfileSerializer(
            user.profile,
            data={
                "first_name": "Ada",
                "secondary_email": "alt@example.net",
                "mobile_phone": "8112345678",
                "birthplace": "Monterrey",
                "school": school.id,
                "home_academic_program": program.id,
                "date_of_birth": "",
            },
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        profile = serializer.save()
        profile.refresh_from_db()
        profile.user.refresh_from_db()
        assert profile.user.first_name == "Ada"
        assert profile.secondary_email == "alt@example.net"
        assert profile.mobile_phone == "8112345678"
        assert profile.birthplace == "Monterrey"
        assert profile.school_id == school.id
        assert profile.home_academic_program_id == program.id
        assert profile.date_of_birth is None

    def test_profile_serializer_persists_eligibility_fields(self):
        from grades.models import GradeScale

        user = User.objects.create_user(
            username="elig-persist",
            email="elig-persist@example.com",
            password="testpass123",
        )
        scale = GradeScale.objects.create(
            name="US GPA 4.0 Scale",
            code="US_GPA_4_TEST",
            min_value=0,
            max_value=4,
            passing_value=2,
            is_active=True,
        )
        serializer = ProfileSerializer(
            user.profile,
            data={
                "gpa": 4.0,
                "grade_scale": str(scale.id),
                "credits_approved_percent": "50.00",
                "ingress_date": "2024-06-24",
                "language": "English",
                "language_level": "C2",
            },
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        profile = serializer.save()
        profile.refresh_from_db()
        data = ProfileSerializer(profile).data
        assert profile.gpa == 4.0
        assert profile.grade_scale_id == scale.id
        assert float(profile.credits_approved_percent) == 50.0
        assert profile.ingress_date == date(2024, 6, 24)
        assert data["credits_approved_percent"] == 50.0
        assert data["grade_scale_name"] == "US GPA 4.0 Scale"
        assert str(data["grade_scale"]) == str(scale.id)

    def test_optional_identity_fields_may_be_blank(self):
        user = User.objects.create_user(
            username="optional-fields",
            email="optional@example.com",
            password="testpass123",
        )
        serializer = ProfileSerializer(
            user.profile,
            data={
                "first_name": "Ada",
                "last_name": "Lovelace",
                "middle_name": "",
                "mothers_last_name": "",
                "passport_number": "",
                "rfc": "",
            },
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        profile = serializer.save()
        profile.refresh_from_db()
        profile.user.refresh_from_db()
        assert profile.user.middle_name == ""
        assert profile.user.mothers_last_name == ""
        assert profile.passport_number == ""
        assert profile.rfc == ""


@pytest.mark.django_db
@pytest.mark.serializers
class TestRoleSerializer:
    """Test cases for RoleSerializer."""

    def test_role_serializer_fields(self):
        """Test RoleSerializer includes all fields."""
        role = Role.objects.create(name="test_role_serializer_fields")

        serializer = RoleSerializer(role)
        data = serializer.data

        assert "id" in data
        assert "name" in data
        assert data["name"] == "test_role_serializer_fields"


@pytest.mark.django_db
@pytest.mark.serializers
class TestPermissionSerializer:
    """Test cases for PermissionSerializer."""

    def test_permission_serializer_fields(self):
        """Test PermissionSerializer includes all fields."""
        permission = Permission.objects.create(name="can_edit_applications")

        serializer = PermissionSerializer(permission)
        data = serializer.data

        assert "id" in data
        assert "name" in data
        assert "roles" in data
        assert data["name"] == "can_edit_applications"


@pytest.mark.django_db
@pytest.mark.serializers
class TestRegistrationSerializer:
    """Test cases for RegistrationSerializer."""

    def setup_method(self):
        AllowedEmailDomain.objects.get_or_create(name="example.com")

    def test_registration_serializer_valid_data(self):
        """Test RegistrationSerializer with valid data."""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "New",
            "middle_name": "Middle",
            "last_name": "User",
            "mothers_last_name": "Family",
        }

        serializer = RegistrationSerializer(data=data)
        assert serializer.is_valid()

    def test_registration_serializer_password_mismatch(self):
        """Test RegistrationSerializer with mismatched passwords."""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpass123",
            "password2": "differentpass",
            "first_name": "New",
            "middle_name": "Middle",
            "last_name": "User",
            "mothers_last_name": "Family",
        }

        serializer = RegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_registration_serializer_create_user(self):
        """Test RegistrationSerializer create method."""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "New",
            "middle_name": "Middle",
            "last_name": "User",
            "mothers_last_name": "Family",
        }

        serializer = RegistrationSerializer(data=data)
        assert serializer.is_valid()

        user = serializer.save()

        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.first_name == "New"
        assert user.middle_name == "Middle"
        assert user.last_name == "User"
        assert user.mothers_last_name == "Family"
        assert user.is_active is False
        assert user.is_email_verified is False
        assert user.email_verification_token is not None
        assert user.check_password("testpass123")

    def test_registration_serializer_requires_all_name_parts(self):
        data = {
            "email": "newuser@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }

        serializer = RegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert {"first_name", "last_name"} <= set(serializer.errors)

    def test_registration_serializer_optional_middle_and_maternal_names(self):
        data = {
            "email": "newuser@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "New",
            "last_name": "User",
        }

        serializer = RegistrationSerializer(data=data)
        assert serializer.is_valid()

        user = serializer.save()
        assert user.username == "newuser"
        assert user.middle_name == ""
        assert user.mothers_last_name == ""

    def test_registration_serializer_derives_username_from_email(self):
        data = {
            "email": "student.name@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "New",
            "last_name": "User",
        }

        serializer = RegistrationSerializer(data=data)
        assert serializer.is_valid()

        user = serializer.save()
        assert user.username == "student.name"

    def test_registration_serializer_rejects_inactive_or_unknown_domain(self):
        AllowedEmailDomain.objects.create(name="inactive.edu.mx", is_active=False)

        unknown = RegistrationSerializer(
            data={
                "email": "student@unknown.edu.mx",
                "username": "unknown",
                "password": "testpass123",
                "password2": "testpass123",
                "first_name": "New",
                "middle_name": "Middle",
                "last_name": "User",
                "mothers_last_name": "Family",
            }
        )
        inactive = RegistrationSerializer(
            data={
                "email": "student@inactive.edu.mx",
                "username": "inactive",
                "password": "testpass123",
                "password2": "testpass123",
                "first_name": "New",
                "middle_name": "Middle",
                "last_name": "User",
                "mothers_last_name": "Family",
            }
        )

        assert not unknown.is_valid()
        assert not inactive.is_valid()
        assert "email" in unknown.errors
        assert "email" in inactive.errors

    def test_registration_serializer_weak_password(self):
        """Test RegistrationSerializer with weak password."""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "123",
            "password2": "123",
            "first_name": "New",
            "middle_name": "Middle",
            "last_name": "User",
            "mothers_last_name": "Family",
        }

        serializer = RegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializers
class TestEmailVerificationSerializer:
    """Test cases for EmailVerificationSerializer."""

    def test_email_verification_serializer_valid_token(self):
        """Test EmailVerificationSerializer with valid token."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        user.is_active = False
        user.is_email_verified = False
        user.email_verification_token = "test_token_123"
        user.save()

        data = {"token": "test_token_123"}
        serializer = EmailVerificationSerializer(data=data)

        assert serializer.is_valid()
        verified_user = serializer.save()

        assert verified_user.is_email_verified is True
        assert verified_user.is_active is True
        assert verified_user.email_verification_token is None

    def test_email_verification_serializer_invalid_token(self):
        """Test EmailVerificationSerializer with invalid token."""
        data = {"token": "invalid_token"}
        serializer = EmailVerificationSerializer(data=data)

        assert not serializer.is_valid()
        assert "token" in serializer.errors

    def test_email_verification_serializer_already_verified(self):
        """Test EmailVerificationSerializer with already verified user."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        user.is_email_verified = True
        user.email_verification_token = "test_token_123"
        user.save()

        data = {"token": "test_token_123"}
        serializer = EmailVerificationSerializer(data=data)

        assert not serializer.is_valid()
        assert "token" in serializer.errors

    def test_email_verification_serializer_missing_token(self):
        """Test EmailVerificationSerializer with missing token."""
        data = {}
        serializer = EmailVerificationSerializer(data=data)

        assert not serializer.is_valid()
        assert "token" in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializers
class TestLoginSerializer:
    """Test cases for LoginSerializer."""

    def test_login_serializer_valid_credentials(self):
        """Test LoginSerializer with valid credentials."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        user.is_email_verified = True
        user.save()

        data = {"login": "testuser", "password": "testpass123"}
        serializer = LoginSerializer(data=data)

        assert serializer.is_valid()
        validated_data = serializer.validated_data
        assert "user" in validated_data

    def test_login_serializer_email_login(self):
        """Test LoginSerializer with email login."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        user.is_email_verified = True
        user.save()

        data = {"login": "test@example.com", "password": "testpass123"}
        serializer = LoginSerializer(data=data)

        assert serializer.is_valid()
        validated_data = serializer.validated_data
        assert "user" in validated_data

    def test_login_serializer_invalid_credentials(self):
        """Test LoginSerializer with invalid credentials."""
        data = {"login": "nonexistent", "password": "wrongpass"}
        serializer = LoginSerializer(data=data)

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid()

    def test_login_serializer_unverified_email(self):
        """Test LoginSerializer with unverified email."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        user.is_email_verified = False
        user.save()

        data = {"login": "testuser", "password": "testpass123"}
        serializer = LoginSerializer(data=data)

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid()

    def test_login_serializer_locked_account(self):
        """Test LoginSerializer with locked account."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        user.is_email_verified = True
        user.lockout_until = timezone.now() + timedelta(minutes=30)
        user.save()

        data = {"login": "testuser", "password": "testpass123"}
        serializer = LoginSerializer(data=data)

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid()

    def test_login_serializer_wrong_password(self):
        """Test LoginSerializer with wrong password."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        user.is_email_verified = True
        user.save()

        data = {"login": "testuser", "password": "wrongpass"}
        serializer = LoginSerializer(data=data)

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid()


@pytest.mark.django_db
@pytest.mark.serializers
class TestPasswordResetRequestSerializer:
    """Test cases for PasswordResetRequestSerializer."""

    def test_password_reset_request_serializer_valid_email(self):
        """Test PasswordResetRequestSerializer with valid email."""
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        data = {"email": "test@example.com"}
        serializer = PasswordResetRequestSerializer(data=data)

        assert serializer.is_valid()
        result = serializer.save()
        assert result is not None

    def test_password_reset_request_serializer_invalid_email(self):
        """Test PasswordResetRequestSerializer with invalid email."""
        data = {"email": "nonexistent@example.com"}
        serializer = PasswordResetRequestSerializer(data=data)

        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializers
class TestPasswordResetConfirmSerializer:
    """Test cases for PasswordResetConfirmSerializer."""

    def test_password_reset_confirm_serializer_valid_data(self):
        """Test PasswordResetConfirmSerializer with valid data."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        user.email_verification_token = "reset_token_123"
        user.save()

        data = {
            "email": "test@example.com",
            "token": "reset_token_123",
            "new_password": "newpass123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        assert serializer.is_valid()
        result = serializer.save()
        assert result is not None

    def test_password_reset_confirm_serializer_invalid_token(self):
        """Test PasswordResetConfirmSerializer with invalid token."""
        data = {
            "email": "test@example.com",
            "token": "invalid_token",
            "new_password": "newpass123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializers
class TestChangePasswordSerializer:
    """Test cases for ChangePasswordSerializer."""

    def test_change_password_serializer_valid_data(self):
        """Test ChangePasswordSerializer with valid data."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpass123",
        )

        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password2": "newpass123",
        }
        # Create a mock request object
        from unittest.mock import Mock

        mock_request = Mock()
        mock_request.user = user
        serializer = ChangePasswordSerializer(
            data=data, context={"request": mock_request}
        )

        assert serializer.is_valid()
        result = serializer.save()
        assert result is not None

    def test_change_password_serializer_wrong_old_password(self):
        """Test ChangePasswordSerializer with wrong old password."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpass123",
        )

        data = {
            "old_password": "wrongpass",
            "new_password": "newpass123",
            "new_password2": "newpass123",
        }
        # Create a mock request object
        from unittest.mock import Mock

        mock_request = Mock()
        mock_request.user = user
        serializer = ChangePasswordSerializer(
            data=data, context={"request": mock_request}
        )

        assert not serializer.is_valid()
        assert "old_password" in serializer.errors

    def test_change_password_serializer_password_mismatch(self):
        """Test ChangePasswordSerializer with password mismatch."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpass123",
        )

        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password2": "differentpass",
        }
        # Create a mock request object
        from unittest.mock import Mock

        mock_request = Mock()
        mock_request.user = user
        serializer = ChangePasswordSerializer(
            data=data, context={"request": mock_request}
        )

        assert not serializer.is_valid()
        assert "new_password" in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializers
class TestUserSettingsSerializer:
    """Test cases for UserSettingsSerializer."""

    def test_user_settings_serializer_fields(self):
        """Test UserSettingsSerializer includes correct fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        settings = UserSettings.objects.create(user=user)

        serializer = UserSettingsSerializer(settings)
        data = serializer.data

        # UserSettingsSerializer doesn't include 'id' field by default
        assert "theme" in data
        assert "font_size" in data
        assert "email_applications" in data
        assert "email_documents" in data
        assert "email_comments" in data
        assert "email_programs" in data
        assert "email_system" in data
        assert "inapp_applications" in data
        assert "inapp_documents" in data
        assert "inapp_comments" in data
        assert "inapp_programs" in data
        assert "inapp_system" in data
        assert "profile_public" in data
        assert "share_analytics" in data

    def test_user_settings_serializer_create(self):
        """Test UserSettingsSerializer create method."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        data = {
            "theme": "dark",
            "font_size": "large",
            "email_applications": False,
        }
        # Create a mock request object
        from unittest.mock import Mock

        mock_request = Mock()
        mock_request.user = user
        serializer = UserSettingsSerializer(
            data=data, context={"request": mock_request}
        )

        assert serializer.is_valid()
        settings = serializer.save()

        assert settings.user == user
        assert settings.theme == "dark"
        assert settings.font_size == "large"
        assert settings.email_applications is False


@pytest.mark.django_db
@pytest.mark.serializers
class TestAppearanceSettingsSerializer:
    """Test cases for AppearanceSettingsSerializer."""

    def test_appearance_settings_serializer_fields(self):
        """Test AppearanceSettingsSerializer includes correct fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        settings = UserSettings.objects.create(user=user)

        serializer = AppearanceSettingsSerializer(settings)
        data = serializer.data

        assert "theme" in data
        assert "font_size" in data

    def test_appearance_settings_serializer_create(self):
        """Test AppearanceSettingsSerializer create method."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        data = {"theme": "dark", "font_size": "large"}
        # Create a mock request object
        from unittest.mock import Mock

        mock_request = Mock()
        mock_request.user = user
        serializer = AppearanceSettingsSerializer(
            data=data, context={"request": mock_request}
        )

        assert serializer.is_valid()
        settings = serializer.save()

        assert settings.user == user
        assert settings.theme == "dark"
        assert settings.font_size == "large"


@pytest.mark.django_db
@pytest.mark.serializers
class TestNotificationSettingsSerializer:
    """Test cases for NotificationSettingsSerializer."""

    def test_notification_settings_serializer_fields(self):
        """Test NotificationSettingsSerializer includes correct fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        settings = UserSettings.objects.create(user=user)

        serializer = NotificationSettingsSerializer(settings)
        data = serializer.data

        assert "email_applications" in data
        assert "email_documents" in data
        assert "email_comments" in data
        assert "email_programs" in data
        assert "email_system" in data
        assert "inapp_applications" in data
        assert "inapp_documents" in data
        assert "inapp_comments" in data
        assert "inapp_programs" in data
        assert "inapp_system" in data

    def test_notification_settings_serializer_create(self):
        """Test NotificationSettingsSerializer create method."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        data = {
            "email_applications": False,
            "email_documents": True,
            "inapp_comments": False,
        }
        # Create a mock request object
        from unittest.mock import Mock

        mock_request = Mock()
        mock_request.user = user
        serializer = NotificationSettingsSerializer(
            data=data, context={"request": mock_request}
        )

        assert serializer.is_valid()
        settings = serializer.save()

        assert settings.user == user
        assert settings.email_applications is False
        assert settings.email_documents is True
        assert settings.inapp_comments is False


@pytest.mark.django_db
@pytest.mark.serializers
class TestPrivacySettingsSerializer:
    """Test cases for PrivacySettingsSerializer."""

    def test_privacy_settings_serializer_fields(self):
        """Test PrivacySettingsSerializer includes correct fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        settings = UserSettings.objects.create(user=user)

        serializer = PrivacySettingsSerializer(settings)
        data = serializer.data

        assert "profile_public" in data
        assert "share_analytics" in data

    def test_privacy_settings_serializer_create(self):
        """Test PrivacySettingsSerializer create method."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        data = {"profile_public": True, "share_analytics": False}
        # Create a mock request object
        from unittest.mock import Mock

        mock_request = Mock()
        mock_request.user = user
        serializer = PrivacySettingsSerializer(
            data=data, context={"request": mock_request}
        )

        assert serializer.is_valid()
        settings = serializer.save()

        assert settings.user == user
        assert settings.profile_public is True
        assert settings.share_analytics is False


@pytest.mark.django_db
@pytest.mark.serializers
class TestUserSessionSerializer:
    """Test cases for UserSessionSerializer."""

    def test_user_session_serializer_fields(self):
        """Test UserSessionSerializer includes correct fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        session = UserSession.objects.create(
            user=user,
            session_key="test_session_123",
            device="Desktop",
            location="New York",
        )

        serializer = UserSessionSerializer(session)
        data = serializer.data

        assert "id" in data
        assert "device" in data
        assert "location" in data
        assert "last_activity" in data
        assert "is_active" in data
        assert data["device"] == "Desktop"
        assert data["location"] == "New York"
