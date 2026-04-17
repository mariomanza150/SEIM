from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimeStampedModel, UUIDModel


class User(AbstractUser, UUIDModel, TimeStampedModel):
    """Custom user model for SEIM. Extend as needed."""

    email = models.EmailField(unique=True)
    # Email verification and account lockout fields
    is_email_verified = models.BooleanField(
        default=False, help_text="Has the user verified their email?"
    )
    email_verification_token = models.CharField(
        max_length=64,
        blank=True,
        default="",
        null=True,
        help_text="Token for email verification workflow.",
    )
    failed_login_attempts = models.IntegerField(
        default=0, help_text="Number of failed login attempts for lockout policy."
    )
    lockout_until = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Datetime until which the account is locked out.",
    )
    # Add institutional fields, etc.
    roles = models.ManyToManyField(
        "Role",
        related_name="users",
        blank=True,
        help_text="Roles assigned to this user.",
    )
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="accounts_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="accounts_user_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def has_role(self, role_name):
        """Check if user has specific role."""
        return self.roles.filter(name=role_name).exists()

    def has_any_role(self, role_names):
        """Check if user has any of the specified roles."""
        if isinstance(role_names, str):
            role_names = [role_names]
        return self.roles.filter(name__in=role_names).exists()

    def has_all_roles(self, role_names):
        """Check if user has all of the specified roles."""
        if isinstance(role_names, str):
            role_names = [role_names]
        return all(self.has_role(role) for role in role_names)

    def get_all_roles(self):
        """Get list of all role names."""
        return list(self.roles.values_list('name', flat=True))

    def has_permission(self, permission_name):
        """Check if user has specific permission based on their roles."""
        from core.permissions import PermissionManager
        return PermissionManager.user_has_permission(self, permission_name)

    def get_all_permissions(self):
        """Get all permissions for user based on their roles."""
        from core.permissions import PermissionManager
        return PermissionManager.get_user_permissions(self)

    @property
    def primary_role(self):
        """
        Get the primary role name for the user.
        Priority: admin > coordinator > student
        """
        role_priority = ['admin', 'coordinator', 'student']
        user_roles = self.get_all_roles()

        for role in role_priority:
            if role in user_roles:
                return role

        # Default to first role if no priority match
        first_role = self.roles.first()
        return first_role.name if first_role else "student"

    @property
    def role(self):
        """Alias for primary_role for backward compatibility."""
        return self.primary_role

    @property
    def is_admin(self):
        """SEIM admin: role, Django staff, or superuser (matches SPA admin console access)."""
        return self.has_role('admin') or self.is_superuser or self.is_staff

    @property
    def is_coordinator(self):
        """Check if user has coordinator role."""
        return self.has_role('coordinator')

    @property
    def is_student(self):
        """Check if user has student role."""
        return self.has_role('student')

    def generate_email_verification_token(self):
        """Generate a random token for email verification."""
        import secrets
        token = secrets.token_hex(32)  # 64-character hex string
        self.email_verification_token = token
        self.save()
        return token

    def is_locked_out(self):
        """Check if the user account is currently locked out."""
        if self.lockout_until is None:
            return False
        from django.utils import timezone
        return timezone.now() < self.lockout_until

    def increment_failed_login_attempts(self):
        """Increment failed login attempts and lock account if threshold reached."""
        from datetime import timedelta

        from django.utils import timezone

        self.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lockout_until = timezone.now() + timedelta(minutes=30)
            self.failed_login_attempts = 0  # Reset counter after lockout

        self.save()

    def unlock_account(self):
        """Unlock the account and reset failed login attempts."""
        self.failed_login_attempts = 0
        self.lockout_until = None
        self.save()

    class Meta:
        ordering = ['username']


class UserSettings(TimeStampedModel):
    """User settings and preferences."""

    class NotificationDigestFrequency(models.TextChoices):
        OFF = "off", "Off"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')

    # Appearance settings
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='auto',
        help_text="User's preferred theme"
    )
    font_size = models.CharField(
        max_length=20,
        choices=[
            ('normal', 'Normal'),
            ('large', 'Large'),
            ('x-large', 'Extra Large'),
        ],
        default='normal',
        help_text="User's preferred font size"
    )
    
    # Accessibility settings
    high_contrast = models.BooleanField(
        default=False,
        help_text="Enable high contrast mode for improved visibility"
    )
    reduce_motion = models.BooleanField(
        default=False,
        help_text="Reduce animations and transitions for accessibility"
    )

    # Notification settings
    email_applications = models.BooleanField(default=True, help_text="Email notifications for application updates")
    email_documents = models.BooleanField(default=True, help_text="Email notifications for document uploads")
    email_comments = models.BooleanField(
        default=True,
        help_text="Email notifications for comments (application/document threads)",
    )
    email_programs = models.BooleanField(default=False, help_text="Email notifications for new programs")
    email_system = models.BooleanField(default=True, help_text="Email notifications for system messages")
    inapp_programs = models.BooleanField(
        default=True,
        help_text="In-app notifications for new programs and program announcements",
    )
    inapp_applications = models.BooleanField(default=True, help_text="In-app notifications for application updates")
    inapp_documents = models.BooleanField(default=True, help_text="In-app notifications for document uploads")
    inapp_comments = models.BooleanField(default=True, help_text="In-app notifications for comments")
    inapp_system = models.BooleanField(
        default=True,
        help_text="In-app notifications for system messages (e.g. agreement reminders)",
    )
    notification_digest_frequency = models.CharField(
        max_length=16,
        choices=NotificationDigestFrequency.choices,
        default=NotificationDigestFrequency.OFF,
        help_text="Summarize unread in-app notifications on a schedule.",
    )
    email_notification_digest = models.BooleanField(
        default=False,
        help_text="Also email the digest when system email is enabled.",
    )
    notification_digest_last_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        help_text="Last digest sent (managed by the digest task).",
    )

    # Privacy settings
    profile_public = models.BooleanField(default=False, help_text="Make profile visible to other users")
    share_analytics = models.BooleanField(default=True, help_text="Share usage analytics")

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"

    def __str__(self):
        return f"Settings for {self.user.username}"


class UserSession(TimeStampedModel):
    """Track user sessions for security management."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True, help_text="Django session key")
    user_agent = models.TextField(blank=True, help_text="User agent string")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address")
    device = models.CharField(max_length=100, blank=True, help_text="Device identifier")
    location = models.CharField(max_length=100, blank=True, help_text="Location information")
    is_active = models.BooleanField(default=True, help_text="Whether this session is currently active")
    last_activity = models.DateTimeField(auto_now=True, help_text="Last activity timestamp")

    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        ordering = ['-last_activity']

    def __str__(self):
        return f"Session for {self.user.username} - {self.device}"


def _default_additional_languages():
    return []


class Profile(UUIDModel, TimeStampedModel):
    """Profile for additional user info."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secondary_email = models.EmailField(blank=True, null=True)
    gpa = models.FloatField(
        null=True,
        blank=True,
        help_text="Student's GPA/grade in their institutional grading scale"
    )
    grade_scale = models.ForeignKey(
        'grades.GradeScale',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profiles',
        help_text="The grading scale used by the student's institution"
    )
    language = models.CharField(max_length=64, null=True, blank=True)
    language_level = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=[
            ('A1', 'Beginner (A1)'),
            ('A2', 'Elementary (A2)'),
            ('B1', 'Intermediate (B1)'),
            ('B2', 'Upper Intermediate (B2)'),
            ('C1', 'Advanced (C1)'),
            ('C2', 'Proficient (C2)'),
        ],
        help_text="Language proficiency level (CEFR scale)"
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Student's date of birth for age verification"
    )
    additional_languages = models.JSONField(
        default=_default_additional_languages,
        blank=True,
        help_text='Other languages and CEFR levels, e.g. [{"name": "German", "level": "B2"}].',
    )

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"Profile for {self.user.username}"

    def get_gpa_equivalent(self):
        """Get the 4.0 GPA equivalent of the student's grade."""
        if not self.gpa or not self.grade_scale:
            return self.gpa  # Return as-is if no scale specified

        from grades.services import GradeTranslationService
        try:
            # Find the closest grade value in the student's scale
            from grades.models import GradeValue
            grade_value = GradeValue.objects.filter(
                grade_scale=self.grade_scale,
                numeric_value=self.gpa
            ).first()

            if grade_value:
                return grade_value.gpa_equivalent

            # If exact match not found, find closest
            return GradeTranslationService._find_closest_grade(
                self.gpa, self.grade_scale
            ).gpa_equivalent if GradeTranslationService._find_closest_grade(
                self.gpa, self.grade_scale
            ) else self.gpa
        except Exception:
            return self.gpa  # Fallback to original value


class Role(models.Model):
    """User roles (student, coordinator, admin)."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Permission(models.Model):
    """Custom permissions for roles."""

    name = models.CharField(max_length=100, unique=True)
    roles = models.ManyToManyField(Role, related_name="permissions")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
