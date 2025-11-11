"""
Service layer for account management business logic.

This module encapsulates all account-related operations including:
- Email verification
- Account lockout policy
- Password reset
- User registration
- Authentication

All account business logic should be delegated to this service.
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from notifications.services import NotificationService

from .models import Profile, User


class AccountService:
    """Service for account-related business logic."""

    # Configuration (can be overridden in settings)
    MAX_LOGIN_ATTEMPTS = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
    LOCKOUT_DURATION_MINUTES = getattr(settings, 'LOCKOUT_DURATION_MINUTES', 30)
    EMAIL_VERIFICATION_TOKEN_LENGTH = 64
    PASSWORD_RESET_TOKEN_LENGTH = 64

    # ==========================================
    # Account Lockout Methods
    # ==========================================

    @staticmethod
    def is_account_locked(user: User) -> bool:
        """
        Check if user account is currently locked out.

        Args:
            user: User instance to check

        Returns:
            True if account is locked, False otherwise
        """
        if user.lockout_until is None:
            return False
        return user.lockout_until > timezone.now()

    @staticmethod
    @transaction.atomic
    def increment_failed_login_attempts(user: User) -> User:
        """
        Increment failed login attempts and lock account if threshold reached.

        Args:
            user: User instance

        Returns:
            Updated user instance
        """
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= AccountService.MAX_LOGIN_ATTEMPTS:
            # Lock the account
            lockout_duration = timedelta(minutes=AccountService.LOCKOUT_DURATION_MINUTES)
            user.lockout_until = timezone.now() + lockout_duration
            user.failed_login_attempts = 0

            # Notify user about lockout
            NotificationService.send_notification(
                recipient=user,
                title="Account Locked",
                message=f"Your account has been locked due to too many failed login attempts. "
                       f"It will be unlocked in {AccountService.LOCKOUT_DURATION_MINUTES} minutes.",
                notification_type='email'
            )

        user.save()
        return user

    @staticmethod
    @transaction.atomic
    def reset_failed_login_attempts(user: User) -> User:
        """
        Reset failed login attempts after successful login.

        Args:
            user: User instance

        Returns:
            Updated user instance
        """
        user.failed_login_attempts = 0
        user.lockout_until = None
        user.save()
        return user

    @staticmethod
    @transaction.atomic
    def unlock_account(user: User) -> User:
        """
        Manually unlock a locked account.

        Args:
            user: User instance to unlock

        Returns:
            Updated user instance
        """
        user.failed_login_attempts = 0
        user.lockout_until = None
        user.save()
        return user

    # ==========================================
    # Email Verification Methods
    # ==========================================

    @staticmethod
    @transaction.atomic
    def generate_email_verification_token(user: User) -> str:
        """
        Generate and save email verification token.

        Args:
            user: User instance

        Returns:
            Generated token string
        """
        token = get_random_string(AccountService.EMAIL_VERIFICATION_TOKEN_LENGTH)
        user.email_verification_token = token
        user.save()
        return token

    @staticmethod
    @transaction.atomic
    def verify_email(user: User, token: str) -> User:
        """
        Verify user email with token.

        Args:
            user: User instance
            token: Verification token

        Returns:
            Updated user instance

        Raises:
            ValueError: If token is invalid or email already verified
        """
        if user.is_email_verified:
            raise ValueError("Email already verified")

        if user.email_verification_token != token:
            raise ValueError("Invalid verification token")

        user.is_email_verified = True
        user.is_active = True
        user.email_verification_token = None
        user.save()

        # Send welcome notification
        NotificationService.send_notification(
            recipient=user,
            title="Email Verified",
            message="Your email has been successfully verified. Welcome to SEIM!",
            notification_type='email'
        )

        return user

    # ==========================================
    # Password Reset Methods
    # ==========================================

    @staticmethod
    @transaction.atomic
    def initiate_password_reset(email: str) -> User | None:
        """
        Initiate password reset process.

        Args:
            email: User's email address

        Returns:
            User instance if found, None otherwise (don't reveal if email exists)
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists (security best practice)
            return None

        # Generate reset token
        token = get_random_string(AccountService.PASSWORD_RESET_TOKEN_LENGTH)
        user.email_verification_token = token  # Reuse field for reset
        user.save()

        # Send reset email
        NotificationService.send_notification(
            recipient=user,
            title="Password Reset Request",
            message=f"Your password reset token: {token}\n\n"
                   f"This token will expire in 1 hour. If you didn't request this, please ignore this message.",
            notification_type='email'
        )

        return user

    @staticmethod
    @transaction.atomic
    def reset_password(email: str, token: str, new_password: str) -> User:
        """
        Reset user password with token.

        Args:
            email: User's email
            token: Reset token
            new_password: New password

        Returns:
            Updated user instance

        Raises:
            ValueError: If token is invalid or user not found
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("Invalid reset token")

        if user.email_verification_token != token:
            raise ValueError("Invalid reset token")

        # Set new password
        user.set_password(new_password)
        user.email_verification_token = None
        user.save()

        # Notify user
        NotificationService.send_notification(
            recipient=user,
            title="Password Changed",
            message="Your password has been successfully changed. If you didn't make this change, please contact support immediately.",
            notification_type='email'
        )

        return user

    # ==========================================
    # Registration Methods
    # ==========================================

    @staticmethod
    @transaction.atomic
    def register_user(
        username: str,
        email: str,
        password: str,
        first_name: str = '',
        last_name: str = ''
    ) -> User:
        """
        Register a new user with email verification.

        Args:
            username: Username
            email: Email address
            password: Password (will be hashed)
            first_name: First name (optional)
            last_name: Last name (optional)

        Returns:
            Created user instance (inactive until email verified)

        Raises:
            ValueError: If username or email already exists
        """
        # Check if username exists
        if User.objects.filter(username=username).exists():
            raise ValueError("Username already exists")

        # Check if email exists
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exists")

        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=False,  # Inactive until email verified
            is_email_verified=False
        )
        user.set_password(password)
        user.save()

        # Generate verification token
        token = AccountService.generate_email_verification_token(user)

        # Create profile
        Profile.objects.get_or_create(user=user)

        # Assign default role (student)
        from .models import Role
        student_role, _ = Role.objects.get_or_create(name='student')
        user.roles.add(student_role)

        # Send verification email
        NotificationService.send_notification(
            recipient=user,
            title="Email Verification Required",
            message=f"Welcome to SEIM! Please verify your email using this token: {token}",
            notification_type='email'
        )

        return user

    # ==========================================
    # Authentication Methods
    # ==========================================

    @staticmethod
    def authenticate_user(login: str, password: str) -> User:
        """
        Authenticate user by username or email.

        Args:
            login: Username or email
            password: Password

        Returns:
            Authenticated user instance

        Raises:
            ValueError: If authentication fails (use generic message for security)
        """
        # Determine if login is email or username
        from django.core.exceptions import ValidationError
        from django.core.validators import validate_email

        try:
            validate_email(login)
            # It's an email
            try:
                user = User.objects.get(email=login)
            except User.DoesNotExist:
                raise ValueError("Invalid credentials")
        except ValidationError:
            # It's a username
            try:
                user = User.objects.get(username=login)
            except User.DoesNotExist:
                raise ValueError("Invalid credentials")

        # Check if email verified
        if not user.is_email_verified:
            raise ValueError("Email not verified. Please check your inbox for the verification link.")

        # Check if account locked
        if AccountService.is_account_locked(user):
            minutes_left = (user.lockout_until - timezone.now()).total_seconds() / 60
            raise ValueError(f"Account is locked. Please try again in {int(minutes_left)} minutes.")

        # Authenticate
        auth_user = authenticate(username=user.username, password=password)

        if not auth_user:
            # Increment failed attempts
            AccountService.increment_failed_login_attempts(user)
            raise ValueError("Invalid credentials")

        # Reset failed attempts on successful login
        AccountService.reset_failed_login_attempts(user)

        return auth_user

    # ==========================================
    # Account Management Methods
    # ==========================================

    @staticmethod
    @transaction.atomic
    def change_password(user: User, old_password: str, new_password: str) -> User:
        """
        Change user password.

        Args:
            user: User instance
            old_password: Current password
            new_password: New password

        Returns:
            Updated user instance

        Raises:
            ValueError: If old password is incorrect
        """
        if not user.check_password(old_password):
            raise ValueError("Old password is incorrect")

        user.set_password(new_password)
        user.save()

        # Notify user
        NotificationService.send_notification(
            recipient=user,
            title="Password Changed",
            message="Your password has been successfully changed.",
            notification_type='email'
        )

        return user

    @staticmethod
    @transaction.atomic
    def deactivate_account(user: User) -> User:
        """
        Deactivate user account (soft delete).

        Args:
            user: User instance

        Returns:
            Updated user instance
        """
        user.is_active = False
        user.save()

        # Notify user
        NotificationService.send_notification(
            recipient=user,
            title="Account Deactivated",
            message="Your account has been deactivated. Contact support if this was a mistake.",
            notification_type='email'
        )

        return user

