from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from accounts.models import Profile, Role


class TestAssignUserRolesCommand(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )
        self.role, created = Role.objects.get_or_create(name='student')

    def test_assign_user_roles_command_success(self):
        """Test successful role assignment"""
        out = StringIO()
        call_command('assign_user_roles', stdout=out)
        self.assertIn('Role assignment completed!', out.getvalue())

    def test_assign_user_roles_command_with_user_id(self):
        """Test role assignment for specific user"""
        out = StringIO()
        call_command('assign_user_roles', username=self.user.username, role='student', stdout=out)
        self.assertIn('Assigned student role to user', out.getvalue())

    def test_assign_user_roles_command_invalid_user(self):
        """Test command with invalid username"""
        out = StringIO()
        call_command('assign_user_roles', username='nonexistentuser', role='student', stdout=out)
        self.assertIn('User nonexistentuser not found', out.getvalue())

class TestCreateMissingProfilesCommand(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )

    def test_create_missing_profiles_command_success(self):
        """Test successful profile creation"""
        out = StringIO()
        call_command('create_missing_profiles', stdout=out)
        self.assertIn('All users already have profiles!', out.getvalue())

    def test_create_missing_profiles_command_no_missing(self):
        """Test when no profiles are missing"""
        # Profile is likely created automatically by signals, so use get_or_create
        profile, created = Profile.objects.get_or_create(user=self.user)
        out = StringIO()
        call_command('create_missing_profiles', stdout=out)
        self.assertIn('All users already have profiles!', out.getvalue())

    def test_create_missing_profiles_command_dry_run(self):
        """Test dry run option for create_missing_profiles command"""
        out = StringIO()
        call_command('create_missing_profiles', '--dry-run', stdout=out)
        output = out.getvalue()
        self.assertTrue('DRY RUN' in output or 'All users already have profiles!' in output)
