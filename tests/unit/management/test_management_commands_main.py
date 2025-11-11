"""
Tests for management commands to improve coverage.
"""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from accounts.models import Profile, Role, User

User = get_user_model()

class TestAssignUserRolesCommand(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.student_role, _ = Role.objects.get_or_create(name='student')
        self.admin_role, _ = Role.objects.get_or_create(name='admin')

    def test_assign_user_roles_command(self):
        out = StringIO()
        call_command('assign_user_roles', stdout=out)
        self.assertIn('assign', out.getvalue().lower())

class TestCreateMissingProfilesCommand(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        Profile.objects.filter(user=self.user1).delete()

    def test_create_missing_profiles_command(self):
        out = StringIO()
        call_command('create_missing_profiles', stdout=out)
        self.assertIn('profile', out.getvalue().lower())
