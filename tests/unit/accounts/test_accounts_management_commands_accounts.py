"""
Tests for accounts management commands.
"""
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from accounts.models import Profile, Role

User = get_user_model()


class TestAssignUserRolesCommand(TestCase):
    """Test the assign_user_roles management command."""

    def setUp(self):
        """Set up test data."""
        # Use get_or_create to avoid unique constraint errors
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.admin_role, _ = Role.objects.get_or_create(name="admin")

        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123"
        )

    def test_assign_user_roles_success(self):
        out = StringIO()
        call_command('assign_user_roles', '--user', self.user1.username, '--role', 'student', stdout=out)
        self.assertIn("Assigned student role to user testuser1", out.getvalue())
        self.assertIn("Role assignment completed", out.getvalue())

    def test_assign_user_roles_invalid_role(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command('assign_user_roles', '--user', self.user1.username, '--role', 'notarole', stdout=out)

    def test_create_missing_profiles_no_missing(self):
        out = StringIO()
        call_command('create_missing_profiles', stdout=out)
        self.assertIn("All users already have profiles!", out.getvalue())

    def test_create_missing_profiles_dry_run(self):
        # Create a user without a profile
        user = User.objects.create_user(username="noprofile", email="noprofile@example.com", password="testpass123")
        Profile.objects.filter(user=user).delete()
        out = StringIO()
        call_command('create_missing_profiles', '--dry-run', stdout=out)
        self.assertIn("DRY RUN", out.getvalue())
        self.assertIn("noprofile", out.getvalue())

    def test_create_missing_profiles_creates_profiles(self):
        # Create a user without a profile
        user = User.objects.create_user(username="noprofile2", email="noprofile2@example.com", password="testpass123")
        Profile.objects.filter(user=user).delete()
        out = StringIO()
        call_command('create_missing_profiles', stdout=out)
        self.assertIn("Created profile for noprofile2", out.getvalue())
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_assign_user_roles_default_logic(self):
        # Create users with different flags
        User.objects.create_superuser(username="adminuser", email="admin@example.com", password="testpass123")
        User.objects.create_user(username="staffuser", email="staff@example.com", password="testpass123", is_staff=True)
        User.objects.create_user(username="regularuser", email="regular@example.com", password="testpass123")
        out = StringIO()
        call_command('assign_user_roles', stdout=out)
        self.assertIn("Assigned admin role to superuser: adminuser", out.getvalue())
        self.assertIn("Assigned coordinator role to staff user: staffuser", out.getvalue())
        self.assertIn("Assigned student role to regular user: regularuser", out.getvalue())
        self.assertIn("Role assignment completed", out.getvalue())
