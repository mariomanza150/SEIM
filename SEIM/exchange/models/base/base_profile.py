from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from .timestamped import Timestamped

class BaseProfile(AbstractUser, Timestamped):
    groups = models.ManyToManyField(
        Group,
        related_name="userprofile_groups",  # Unique related_name for UserProfile.groups
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="userprofile_permissions",  # Unique related_name for UserProfile.user_permissions
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def ensure_default_groups():
        """
        Ensure the default groups exist in the database.
        """
        roles = ["CASE_MANAGER", "SUPERVISOR", "SYSTEM"]
        for role in roles:
            Group.objects.get_or_create(name=role)

    @staticmethod
    def get_system_user():
        """
        Returns the special 'System' user, creating it if necessary.
        Use this func for system-initiated changes.
        """
        user, _ = BaseProfile.objects.get_or_create(
            username="system", defaults={"is_staff": False, "is_superuser": False}
        )
        system_group, _ = Group.objects.get_or_create(name="SYSTEM")
        user.groups.add(system_group)
        return user
