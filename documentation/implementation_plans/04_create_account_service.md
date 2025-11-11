# Implementation Plan: Create AccountService and Move Business Logic

**Priority:** 🟠 High Priority - Architecture  
**Effort:** 8 hours  
**Risk:** Medium - Requires refactoring existing code  
**Dependencies:** None  

---

## Problem Statement

Business logic for account management is currently scattered across:
- User model methods (`increment_failed_login_attempts`, `is_locked_out`, etc.)
- LoginSerializer validation
- RegistrationSerializer creation

This violates the Single Responsibility Principle and makes code harder to test and maintain.

### Current Issues

1. **Business Logic in Model** (`accounts/models.py`, lines 52-91)
   - Account lockout logic
   - Email verification logic
   - Password reset logic

2. **Business Logic in Serializer** (`accounts/serializers.py`, lines 164-206)
   - Authentication logic
   - Failed login attempt handling

---

## Proposed Solution

Create a dedicated `AccountService` class to handle all account-related business logic.

### Step 1: Create AccountService

**Create File:** `accounts/services.py`

```python
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
from typing import Optional

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from notifications.services import NotificationService

from .models import Profile, User


class AccountService:
    """Service for account-related business logic."""
    
    # Configuration (should eventually move to settings)
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
    def initiate_password_reset(email: str) -> Optional[User]:
        """
        Initiate password reset process.
        
        Args:
            email: User's email address
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists (security)
            return None
        
        # Generate reset token
        token = get_random_string(AccountService.PASSWORD_RESET_TOKEN_LENGTH)
        user.email_verification_token = token  # Reuse field
        user.save()
        
        # Send reset email
        NotificationService.send_notification(
            recipient=user,
            title="Password Reset Request",
            message=f"Your password reset token: {token}\n\n"
                   f"This token will expire in 1 hour.",
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
            raise ValueError("User not found")
        
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
            message="Your password has been successfully changed.",
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
            password: Password
            first_name: First name (optional)
            last_name: Last name (optional)
            
        Returns:
            Created user instance
            
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
            message=f"Please verify your email using this token: {token}",
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
            ValueError: If authentication fails
        """
        # Determine if login is email or username
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
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
            raise ValueError("Email not verified")
        
        # Check if account locked
        if AccountService.is_account_locked(user):
            raise ValueError("Account is locked. Try again later.")
        
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
        
        return user
```

---

### Step 2: Refactor User Model

**File:** `accounts/models.py`

**Remove these methods:**

```python
# ❌ DELETE these methods from User model

    def is_locked_out(self):  # DELETE
        from django.utils import timezone
        return self.lockout_until is not None and self.lockout_until > timezone.now()

    def unlock_account(self):  # DELETE
        self.failed_login_attempts = 0
        self.lockout_until = None
        self.save()

    def generate_email_verification_token(self):  # DELETE
        from django.utils.crypto import get_random_string
        token = get_random_string(64)
        self.email_verification_token = token
        self.save()
        return token

    def increment_failed_login_attempts(self):  # DELETE
        from django.utils import timezone
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lockout_until = timezone.now() + timezone.timedelta(minutes=30)
            self.failed_login_attempts = 0
        self.save()
```

**Keep these (they're simple property methods):**

```python
# ✅ KEEP these helper methods

    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()

    @property
    def primary_role(self):
        """Get the primary role name for the user."""
        first_role = self.roles.first()
        return first_role.name if first_role else "student"

    @property
    def role(self):
        """Get the primary role name for the user (alias for primary_role)."""
        return self.primary_role
```

---

### Step 3: Refactor LoginSerializer

**File:** `accounts/serializers.py`

**Replace lines 164-206:**

```python
class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate credentials using AccountService.
        
        Delegates all authentication logic to the service layer.
        """
        from .services import AccountService
        
        login = data.get("login")
        password = data.get("password")

        try:
            # Use AccountService for authentication
            auth_user = AccountService.authenticate_user(login, password)
            data["user"] = auth_user
            return data
        except ValueError as e:
            # Re-raise as serializer validation error
            raise serializers.ValidationError({"detail": str(e)})
```

---

### Step 4: Refactor RegistrationSerializer

**File:** `accounts/serializers.py`

**Replace create method (lines 110-137):**

```python
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password2",
            "first_name",
            "last_name",
        )

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        """
        Create user using AccountService.
        
        Delegates registration logic to the service layer.
        """
        from .services import AccountService
        
        password = validated_data.pop("password")
        validated_data.pop("password2", None)
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        username = validated_data["username"]
        email = validated_data["email"]
        
        try:
            user = AccountService.register_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            return user
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})
```

---

### Step 5: Update Other Serializers

**File:** `accounts/serializers.py`

**EmailVerificationSerializer:**

```python
class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=64)

    def validate(self, data):
        if not data.get("token"):
            raise serializers.ValidationError({"token": "This field is required."})
        try:
            user = User.objects.get(email_verification_token=data["token"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid verification token."})
        
        data["user"] = user
        return data

    def save(self, **kwargs):
        """Verify email using AccountService."""
        from .services import AccountService
        
        user = self.validated_data["user"]
        token = self.validated_data["token"]
        
        try:
            user = AccountService.verify_email(user, token)
            return user
        except ValueError as e:
            raise serializers.ValidationError({"token": str(e)})
```

**PasswordResetRequestSerializer:**

```python
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self, **kwargs):
        """Initiate password reset using AccountService."""
        from .services import AccountService
        
        email = self.validated_data["email"]
        AccountService.initiate_password_reset(email)
        # Always return success (don't reveal if email exists)
        return {"detail": "Password reset email sent if account exists"}
```

**PasswordResetConfirmSerializer:**

```python
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=64)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        """Reset password using AccountService."""
        from .services import AccountService
        
        try:
            user = AccountService.reset_password(
                email=self.validated_data["email"],
                token=self.validated_data["token"],
                new_password=self.validated_data["new_password"]
            )
            return user
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})
```

**ChangePasswordSerializer:**

```python
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "New passwords do not match."}
            )
        return data

    def save(self, **kwargs):
        """Change password using AccountService."""
        from .services import AccountService
        
        user = self.context["request"].user
        
        try:
            user = AccountService.change_password(
                user=user,
                old_password=self.validated_data["old_password"],
                new_password=self.validated_data["new_password"]
            )
            return user
        except ValueError as e:
            raise serializers.ValidationError({"old_password": str(e)})
```

---

## Implementation Steps

### Phase 1: Create Service (2 hours)

1. Create `accounts/services.py`
2. Implement all AccountService methods
3. Add docstrings and type hints
4. Add configuration constants

### Phase 2: Refactor Model (30 minutes)

1. Remove business logic methods from User model
2. Keep simple helper methods
3. Update any code that calls removed methods

### Phase 3: Refactor Serializers (2 hours)

1. Update LoginSerializer
2. Update RegistrationSerializer
3. Update EmailVerificationSerializer
4. Update PasswordResetRequestSerializer
5. Update PasswordResetConfirmSerializer
6. Update ChangePasswordSerializer

### Phase 4: Testing (3 hours)

1. Write unit tests for AccountService
2. Update serializer tests
3. Integration testing
4. Manual testing

### Phase 5: Documentation (30 minutes)

1. Add docstrings
2. Update developer guide
3. Add examples

---

## Testing

**Create:** `accounts/tests/test_account_service.py`

```python
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, Role
from accounts.services import AccountService


class AccountServiceTests(TestCase):
    def setUp(self):
        self.student_role = Role.objects.create(name='student')
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_register_user(self):
        """Test user registration."""
        user = AccountService.register_user(
            username='newuser',
            email='new@example.com',
            password='newpass123',
            first_name='New',
            last_name='User'
        )
        
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertFalse(user.is_active)  # Should be inactive until verified
        self.assertFalse(user.is_email_verified)
        self.assertIsNotNone(user.email_verification_token)
        self.assertTrue(user.has_role('student'))
    
    def test_verify_email(self):
        """Test email verification."""
        token = AccountService.generate_email_verification_token(self.test_user)
        
        user = AccountService.verify_email(self.test_user, token)
        
        self.assertTrue(user.is_email_verified)
        self.assertTrue(user.is_active)
        self.assertIsNone(user.email_verification_token)
    
    def test_is_account_locked(self):
        """Test account lockout check."""
        # Not locked initially
        self.assertFalse(AccountService.is_account_locked(self.test_user))
        
        # Lock account
        self.test_user.lockout_until = timezone.now() + timedelta(minutes=30)
        self.test_user.save()
        
        self.assertTrue(AccountService.is_account_locked(self.test_user))
    
    def test_increment_failed_login_attempts(self):
        """Test failed login attempt handling."""
        user = self.test_user
        
        # Increment 4 times (should not lock)
        for _ in range(4):
            AccountService.increment_failed_login_attempts(user)
            user.refresh_from_db()
        
        self.assertEqual(user.failed_login_attempts, 4)
        self.assertFalse(AccountService.is_account_locked(user))
        
        # 5th attempt should lock account
        AccountService.increment_failed_login_attempts(user)
        user.refresh_from_db()
        
        self.assertTrue(AccountService.is_account_locked(user))
        self.assertEqual(user.failed_login_attempts, 0)  # Reset after lock
    
    def test_authenticate_user_success(self):
        """Test successful authentication."""
        self.test_user.is_email_verified = True
        self.test_user.is_active = True
        self.test_user.save()
        
        user = AccountService.authenticate_user('testuser', 'testpass123')
        
        self.assertEqual(user, self.test_user)
        self.assertEqual(user.failed_login_attempts, 0)
    
    def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password."""
        self.test_user.is_email_verified = True
        self.test_user.is_active = True
        self.test_user.save()
        
        with self.assertRaises(ValueError):
            AccountService.authenticate_user('testuser', 'wrongpass')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.failed_login_attempts, 1)
    
    def test_change_password(self):
        """Test password change."""
        self.test_user.set_password('oldpass')
        self.test_user.save()
        
        user = AccountService.change_password(
            user=self.test_user,
            old_password='oldpass',
            new_password='newpass123'
        )
        
        self.assertTrue(user.check_password('newpass123'))
        self.assertFalse(user.check_password('oldpass'))
```

---

## Estimated Time

| Task | Time |
|------|------|
| Create AccountService | 2h |
| Refactor User model | 30m |
| Refactor serializers | 2h |
| Write tests | 2h |
| Integration testing | 1h |
| Documentation | 30m |

**Total:** ~8 hours

---

## Success Criteria

✅ **Business Logic Moved:** All account logic in service layer  
✅ **Models Clean:** User model has no business logic  
✅ **Serializers Thin:** Serializers delegate to service  
✅ **Tests Pass:** All tests pass  
✅ **No Regression:** Existing functionality works  
✅ **Well-Documented:** Comprehensive docstrings  

---

## Next Steps

After this refactor:
1. ✅ Apply same pattern to other areas
2. ✅ Create DocumentService improvements
3. ✅ Create ExchangeService improvements

