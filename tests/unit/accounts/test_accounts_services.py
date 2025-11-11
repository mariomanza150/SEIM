"""
Test Accounts Services

Comprehensive tests for account management business logic.
"""

import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone
from unittest.mock import patch, MagicMock

from accounts.models import Role
from accounts.services import AccountService

User = get_user_model()


@pytest.mark.django_db
class TestAccountLockout(TestCase):
    """Test account lockout functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    def test_is_account_locked_no_lockout(self):
        """Test account not locked when lockout_until is None."""
        self.user.lockout_until = None
        self.user.save()
        
        result = AccountService.is_account_locked(self.user)
        
        self.assertFalse(result)

    def test_is_account_locked_future_lockout(self):
        """Test account locked when lockout_until is in future."""
        self.user.lockout_until = timezone.now() + timedelta(minutes=10)
        self.user.save()
        
        result = AccountService.is_account_locked(self.user)
        
        self.assertTrue(result)

    def test_is_account_locked_past_lockout(self):
        """Test account not locked when lockout_until is in past."""
        self.user.lockout_until = timezone.now() - timedelta(minutes=10)
        self.user.save()
        
        result = AccountService.is_account_locked(self.user)
        
        self.assertFalse(result)

    @patch('accounts.services.NotificationService.send_notification')
    def test_increment_failed_login_attempts_below_threshold(self, mock_notification):
        """Test incrementing attempts below threshold."""
        self.user.failed_login_attempts = 2
        self.user.save()
        
        updated_user = AccountService.increment_failed_login_attempts(self.user)
        
        self.assertEqual(updated_user.failed_login_attempts, 3)
        self.assertIsNone(updated_user.lockout_until)
        mock_notification.assert_not_called()

    @patch('accounts.services.NotificationService.send_notification')
    @override_settings(MAX_LOGIN_ATTEMPTS=5)
    def test_increment_failed_login_attempts_reaches_threshold(self, mock_notification):
        """Test incrementing attempts to threshold locks account."""
        self.user.failed_login_attempts = 4
        self.user.save()
        
        updated_user = AccountService.increment_failed_login_attempts(self.user)
        
        # Should be locked
        self.assertEqual(updated_user.failed_login_attempts, 0)  # Reset to 0
        self.assertIsNotNone(updated_user.lockout_until)
        self.assertGreater(updated_user.lockout_until, timezone.now())
        
        # Should send notification
        mock_notification.assert_called_once()

    def test_reset_failed_login_attempts(self):
        """Test resetting failed login attempts."""
        self.user.failed_login_attempts = 3
        self.user.lockout_until = timezone.now() + timedelta(minutes=10)
        self.user.save()
        
        updated_user = AccountService.reset_failed_login_attempts(self.user)
        
        self.assertEqual(updated_user.failed_login_attempts, 0)
        self.assertIsNone(updated_user.lockout_until)

    def test_unlock_account(self):
        """Test manually unlocking account."""
        self.user.failed_login_attempts = 5
        self.user.lockout_until = timezone.now() + timedelta(minutes=20)
        self.user.save()
        
        updated_user = AccountService.unlock_account(self.user)
        
        self.assertEqual(updated_user.failed_login_attempts, 0)
        self.assertIsNone(updated_user.lockout_until)


@pytest.mark.django_db
class TestEmailVerification(TestCase):
    """Test email verification functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            is_email_verified=False
        )

    def test_generate_email_verification_token(self):
        """Test generating verification token."""
        token = AccountService.generate_email_verification_token(self.user)
        
        self.assertIsNotNone(token)
        self.assertEqual(len(token), 64)
        
        # Verify token saved
        self.user.refresh_from_db()
        self.assertEqual(self.user.email_verification_token, token)

    def test_generate_email_verification_token_length(self):
        """Test token has correct length."""
        token = AccountService.generate_email_verification_token(self.user)
        
        self.assertEqual(len(token), AccountService.EMAIL_VERIFICATION_TOKEN_LENGTH)

    @patch('accounts.services.NotificationService.send_notification')
    def test_verify_email_success(self, mock_notification):
        """Test successful email verification."""
        token = AccountService.generate_email_verification_token(self.user)
        
        updated_user = AccountService.verify_email(self.user, token)
        
        self.assertTrue(updated_user.is_email_verified)
        self.assertTrue(updated_user.is_active)
        self.assertIsNone(updated_user.email_verification_token)
        
        # Should send welcome notification
        mock_notification.assert_called_once()

    def test_verify_email_invalid_token(self):
        """Test verification with invalid token."""
        AccountService.generate_email_verification_token(self.user)
        
        with self.assertRaises(ValueError) as context:
            AccountService.verify_email(self.user, "wrong_token")
        
        self.assertIn('Invalid verification token', str(context.exception))

    def test_verify_email_already_verified(self):
        """Test verification when email already verified."""
        self.user.is_email_verified = True
        self.user.save()
        
        with self.assertRaises(ValueError) as context:
            AccountService.verify_email(self.user, "any_token")
        
        self.assertIn('already verified', str(context.exception))


@pytest.mark.django_db
class TestPasswordReset(TestCase):
    """Test password reset functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    @patch('accounts.services.NotificationService.send_notification')
    def test_initiate_password_reset_success(self, mock_notification):
        """Test initiating password reset."""
        user = AccountService.initiate_password_reset("test@test.com")
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@test.com")
        
        # Should generate token
        user.refresh_from_db()
        self.assertIsNotNone(user.email_verification_token)
        
        # Should send notification
        mock_notification.assert_called_once()

    def test_initiate_password_reset_nonexistent_email(self):
        """Test password reset with non-existent email."""
        user = AccountService.initiate_password_reset("nonexistent@test.com")
        
        # Should return None for security (don't reveal if email exists)
        self.assertIsNone(user)

    def test_initiate_password_reset_inactive_user(self):
        """Test password reset still works for inactive users."""
        self.user.is_active = False
        self.user.save()
        
        user = AccountService.initiate_password_reset("test@test.com")
        
        # Should still work for inactive users
        self.assertIsNotNone(user)

    @patch('accounts.services.NotificationService.send_notification')
    def test_reset_password_success(self, mock_notification):
        """Test successful password reset."""
        # Initiate reset to get token
        token = get_random_string(64)
        self.user.email_verification_token = token
        self.user.save()
        
        old_password = self.user.password
        
        updated_user = AccountService.reset_password(
            email="test@test.com",
            token=token,
            new_password="newpass123"
        )
        
        # Password should be changed
        self.assertNotEqual(updated_user.password, old_password)
        
        # Token should be cleared
        self.assertIsNone(updated_user.email_verification_token)
        
        # Notification should be sent
        mock_notification.assert_called_once()

    def test_reset_password_invalid_email(self):
        """Test password reset with invalid email."""
        with self.assertRaises(ValueError) as context:
            AccountService.reset_password(
                email="wrong@test.com",
                token="any_token",
                new_password="newpass123"
            )
        
        self.assertIn('Invalid reset token', str(context.exception))

    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token."""
        token = get_random_string(64)
        self.user.email_verification_token = token
        self.user.save()
        
        with self.assertRaises(ValueError) as context:
            AccountService.reset_password(
                email="test@test.com",
                token="wrong_token",
                new_password="newpass123"
            )
        
        self.assertIn('Invalid reset token', str(context.exception))


@pytest.mark.django_db
class TestUserRegistration(TestCase):
    """Test user registration functionality."""

    @patch('accounts.services.AccountService.generate_email_verification_token')
    @patch('accounts.services.NotificationService.send_notification')
    def test_register_user_success(self, mock_notification, mock_token):
        """Test successful user registration."""
        mock_token.return_value = "test_token"
        
        user = AccountService.register_user(
            username="newuser",
            email="newuser@test.com",
            password="testpass123",
            first_name="New",
            last_name="User"
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@test.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")
        self.assertFalse(user.is_email_verified)
        self.assertFalse(user.is_active)  # Inactive until verified
        
        # Should have profile created
        self.assertTrue(hasattr(user, 'profile'))
        
        # Should send notification
        mock_notification.assert_called_once()

    @patch('accounts.services.AccountService.generate_email_verification_token')
    @patch('accounts.services.NotificationService.send_notification')
    def test_register_user_minimal_data(self, mock_notification, mock_token):
        """Test registration with minimal required data."""
        mock_token.return_value = "test_token"
        
        user = AccountService.register_user(
            username="minimal",
            email="minimal@test.com",
            password="testpass123"
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "minimal")

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username."""
        User.objects.create_user(
            username="existing",
            email="existing@test.com",
            password="testpass123"
        )
        
        with self.assertRaises(ValueError):
            AccountService.register_user(
                username="existing",
                email="different@test.com",
                password="testpass123"
            )

    @patch('accounts.services.AccountService.generate_email_verification_token')
    @patch('accounts.services.NotificationService.send_notification')
    def test_register_user_assigns_default_role(self, mock_notification, mock_token):
        """Test registration assigns default student role."""
        mock_token.return_value = "test_token"
        
        student_role, _ = Role.objects.get_or_create(name="student")
        
        user = AccountService.register_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        
        # Should have student role
        self.assertTrue(user.has_role("student"))


@pytest.mark.django_db
class TestUserAuthentication(TestCase):
    """Test user authentication functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            is_email_verified=True,
            is_active=True
        )

    @patch('accounts.services.AccountService.reset_failed_login_attempts')
    def test_authenticate_user_success_with_username(self, mock_reset):
        """Test successful authentication with username."""
        user = AccountService.authenticate_user("testuser", "testpass123")
        
        self.assertEqual(user.id, self.user.id)
        mock_reset.assert_called_once_with(user)

    @patch('accounts.services.AccountService.reset_failed_login_attempts')
    def test_authenticate_user_success_with_email(self, mock_reset):
        """Test successful authentication with email."""
        user = AccountService.authenticate_user("test@test.com", "testpass123")
        
        self.assertEqual(user.id, self.user.id)
        mock_reset.assert_called_once_with(user)

    @patch('accounts.services.AccountService.increment_failed_login_attempts')
    def test_authenticate_user_wrong_password(self, mock_increment):
        """Test authentication with wrong password."""
        with self.assertRaises(ValueError) as context:
            AccountService.authenticate_user("testuser", "wrongpass")
        
        self.assertIn('Invalid credentials', str(context.exception))

    def test_authenticate_user_nonexistent_user(self):
        """Test authentication with non-existent user."""
        with self.assertRaises(ValueError) as context:
            AccountService.authenticate_user("nonexistent", "testpass123")
        
        self.assertIn('Invalid credentials', str(context.exception))

    def test_authenticate_user_unverified_email(self):
        """Test authentication with unverified email."""
        self.user.is_email_verified = False
        self.user.save()
        
        with self.assertRaises(ValueError) as context:
            AccountService.authenticate_user("testuser", "testpass123")
        
        self.assertIn('not verified', str(context.exception).lower())

    def test_authenticate_user_locked_account(self):
        """Test authentication with locked account."""
        self.user.lockout_until = timezone.now() + timedelta(minutes=10)
        self.user.save()
        
        with self.assertRaises(ValueError) as context:
            AccountService.authenticate_user("testuser", "testpass123")
        
        self.assertIn('locked', str(context.exception).lower())

    def test_authenticate_user_inactive_account(self):
        """Test authentication with inactive account."""
        self.user.is_active = False
        self.user.save()
        
        with self.assertRaises(ValueError) as context:
            AccountService.authenticate_user("testuser", "testpass123")
        
        # Django's authenticate returns None for inactive users, 
        # which results in "Invalid credentials" error
        self.assertIn('invalid credentials', str(context.exception).lower())


@pytest.mark.django_db
class TestPasswordChange(TestCase):
    """Test password change functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="oldpass123"
        )

    @patch('accounts.services.NotificationService.send_notification')
    def test_change_password_success(self, mock_notification):
        """Test successful password change."""
        old_password_hash = self.user.password
        
        updated_user = AccountService.change_password(
            self.user,
            old_password="oldpass123",
            new_password="newpass123"
        )
        
        # Password should be changed
        self.assertNotEqual(updated_user.password, old_password_hash)
        
        # Should be able to login with new password
        self.assertTrue(
            updated_user.check_password("newpass123")
        )
        
        # Notification should be sent
        mock_notification.assert_called_once()

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        with self.assertRaises(ValueError) as context:
            AccountService.change_password(
                self.user,
                old_password="wrongpass",
                new_password="newpass123"
            )
        
        self.assertIn('incorrect', str(context.exception).lower())

    def test_change_password_same_as_old(self):
        """Test changing to same password."""
        # Should work - no restriction on reusing password
        updated_user = AccountService.change_password(
            self.user,
            old_password="oldpass123",
            new_password="oldpass123"
        )
        
        self.assertIsNotNone(updated_user)


@pytest.mark.django_db
class TestAccountDeactivation(TestCase):
    """Test account deactivation functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            is_active=True
        )

    @patch('accounts.services.NotificationService.send_notification')
    def test_deactivate_account(self, mock_notification):
        """Test account deactivation."""
        updated_user = AccountService.deactivate_account(self.user)
        
        self.assertFalse(updated_user.is_active)
        
        # Should send notification
        mock_notification.assert_called_once()

    def test_deactivate_already_inactive_account(self):
        """Test deactivating already inactive account."""
        self.user.is_active = False
        self.user.save()
        
        updated_user = AccountService.deactivate_account(self.user)
        
        self.assertFalse(updated_user.is_active)


# Import get_random_string at the module level for tests
from django.utils.crypto import get_random_string

