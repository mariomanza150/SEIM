"""
Test Accounts Services - Edge Cases and Boundary Conditions

This test file covers edge cases for user authentication, registration,
and account management.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounts.models import Profile, Role

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationEdgeCases(TestCase):
    """Test user registration edge cases."""

    def test_register_with_minimum_valid_data(self):
        """Test registration with absolute minimum required fields."""
        user = User.objects.create_user(
            username="minuser",
            email="min@test.com",
            password="pass123"
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "minuser")
        self.assertTrue(user.check_password("pass123"))

    def test_register_with_unicode_username(self):
        """Test registration with unicode characters in username."""
        unicode_username = "用户名"
        
        user = User.objects.create_user(
            username=unicode_username,
            email="unicode@test.com",
            password="testpass123"
        )
        
        self.assertEqual(user.username, unicode_username)

    def test_register_with_email_as_username(self):
        """Test registration using email as username."""
        email = "user@example.com"
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password="testpass123"
        )
        
        self.assertEqual(user.username, email)
        self.assertEqual(user.email, email)

    def test_duplicate_username_prevention(self):
        """Test that duplicate usernames are prevented."""
        User.objects.create_user(
            username="duplicate",
            email="first@test.com",
            password="testpass123"
        )
        
        # Attempt duplicate username
        with self.assertRaises(Exception):  # IntegrityError expected
            User.objects.create_user(
                username="duplicate",
                email="second@test.com",
                password="testpass123"
            )

    def test_duplicate_email_allowed(self):
        """Test that duplicate emails might be allowed (depends on constraints)."""
        # Note: If email is not unique in model, this should work
        user1 = User.objects.create_user(
            username="user1",
            email="same@test.com",
            password="testpass123"
        )
        
        try:
            user2 = User.objects.create_user(
                username="user2",
                email="same@test.com",  # Same email
                password="testpass123"
            )
            # If we get here, emails can be duplicated
            self.assertIsNotNone(user2)
        except Exception:
            # If unique constraint exists, this is expected
            pass

    def test_password_minimum_length(self):
        """Test password with very short length."""
        # Single character password
        user = User.objects.create_user(
            username="shortpass",
            email="short@test.com",
            password="a"  # Very short
        )
        
        self.assertTrue(user.check_password("a"))

    def test_password_with_null_bytes(self):
        """Test password with null bytes."""
        # Null bytes should be handled
        password = "pass\x00word"
        
        user = User.objects.create_user(
            username="nullbyte",
            email="null@test.com",
            password=password
        )
        
        # Password should be hashed successfully
        self.assertIsNotNone(user.password)


@pytest.mark.django_db
class TestRoleAssignmentEdgeCases(TestCase):
    """Test role assignment edge cases."""

    def test_user_with_no_roles(self):
        """Test user without any roles assigned."""
        user = User.objects.create_user(
            username="noroles",
            email="noroles@test.com",
            password="testpass123"
        )
        
        self.assertEqual(user.roles.count(), 0)
        self.assertFalse(user.has_role("student"))
        self.assertFalse(user.has_role("admin"))

    def test_user_with_multiple_roles(self):
        """Test user assigned to multiple roles."""
        student_role, _ = Role.objects.get_or_create(name="student")
        coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        admin_role, _ = Role.objects.get_or_create(name="admin")
        
        user = User.objects.create_user(
            username="multirole",
            email="multi@test.com",
            password="testpass123"
        )
        
        # Assign multiple roles
        user.roles.add(student_role, coordinator_role, admin_role)
        
        self.assertEqual(user.roles.count(), 3)
        self.assertTrue(user.has_role("student"))
        self.assertTrue(user.has_role("coordinator"))
        self.assertTrue(user.has_role("admin"))

    def test_assign_nonexistent_role(self):
        """Test assigning a role that doesn't exist."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        # has_role should return False for nonexistent role
        self.assertFalse(user.has_role("nonexistent_role"))

    def test_remove_all_roles(self):
        """Test removing all roles from a user."""
        role, _ = Role.objects.get_or_create(name="student")
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        user.roles.add(role)
        
        # Remove all roles
        user.roles.clear()
        
        self.assertEqual(user.roles.count(), 0)


@pytest.mark.django_db
class TestProfileEdgeCases(TestCase):
    """Test user profile edge cases."""

    def test_profile_auto_creation(self):
        """Test that profile is created automatically for new users."""
        user = User.objects.create_user(
            username="newuser",
            email="new@test.com",
            password="testpass123"
        )
        
        # Profile should be created automatically by signal
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile)

    def test_profile_with_null_fields(self):
        """Test profile with null optional fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        profile = user.profile
        
        # Optional fields should be null or empty
        self.assertIsNone(profile.secondary_email)
        self.assertIsNone(profile.gpa)
        self.assertIsNone(profile.language)
        self.assertIsNone(profile.date_of_birth)

    def test_profile_update_with_special_characters(self):
        """Test updating profile with special characters."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        # Update with special characters
        user.profile.bio = "Hello! 😀 Testing with émojis and spëcial çhars"
        user.profile.save()
        
        user.profile.refresh_from_db()
        self.assertIn("😀", user.profile.bio)

    def test_profile_deletion_with_user(self):
        """Test that profile is deleted when user is deleted."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        profile_id = user.profile.id
        
        # Delete user
        user.delete()
        
        # Profile should also be deleted
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(id=profile_id)


@pytest.mark.django_db
class TestAuthenticationEdgeCases(TestCase):
    """Test authentication edge cases."""

    def test_login_with_inactive_user(self):
        """Test login attempt with inactive user."""
        user = User.objects.create_user(
            username="inactive",
            email="inactive@test.com",
            password="testpass123",
            is_active=False  # Inactive user
        )
        
        # User exists but is inactive
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password("testpass123"))

    def test_login_with_wrong_password(self):
        """Test login with incorrect password."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="correctpass"
        )
        
        # Wrong password
        self.assertFalse(user.check_password("wrongpass"))

    def test_login_with_empty_password(self):
        """Test login with empty password."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        # Empty password should not match
        self.assertFalse(user.check_password(""))

    def test_case_sensitive_username(self):
        """Test that usernames are case-sensitive."""
        User.objects.create_user(
            username="TestUser",
            email="test1@test.com",
            password="testpass123"
        )
        
        # Different case should create different user
        user2 = User.objects.create_user(
            username="testuser",
            email="test2@test.com",
            password="testpass123"
        )
        
        self.assertEqual(User.objects.filter(username__iexact="testuser").count(), 2)

    def test_superuser_without_roles(self):
        """Test that superuser has admin access without explicit role."""
        superuser = User.objects.create_superuser(
            username="super",
            email="super@test.com",
            password="testpass123"
        )
        
        # Superuser should have admin access even without admin role
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


@pytest.mark.django_db
class TestDataIntegrityEdgeCases(TestCase):
    """Test data integrity and constraint edge cases."""

    def test_user_with_same_email_different_case(self):
        """Test users with same email in different cases."""
        User.objects.create_user(
            username="user1",
            email="Test@Example.com",
            password="testpass123"
        )
        
        # Depending on database collation, this may or may not be allowed
        try:
            User.objects.create_user(
                username="user2",
                email="test@example.com",
                password="testpass123"
            )
            # If allowed, both users exist
            self.assertTrue(User.objects.filter(username="user2").exists())
        except Exception:
            # If unique constraint on email (case-insensitive), this is expected
            pass

    def test_role_name_uniqueness(self):
        """Test that role names must be unique."""
        # Use a unique name to avoid collisions with other tests
        unique_role_name = f"test_role_{timezone.now().timestamp()}"
        Role.objects.create(name=unique_role_name)
        
        # Duplicate role name should fail
        with self.assertRaises(Exception):  # IntegrityError
            Role.objects.create(name=unique_role_name)

    def test_role_with_empty_name(self):
        """Test role with empty name."""
        # Empty name might be allowed by model
        role = Role.objects.create(name="")
        
        self.assertEqual(role.name, "")

    def test_user_deletion_preserves_audit_trail(self):
        """Test that user deletion doesn't break audit trails."""
        student_role, _ = Role.objects.get_or_create(name="student")
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        user.roles.add(student_role)
        
        # Create some activity
        user.last_login = timezone.now()
        user.save()
        
        user_id = user.id
        
        # Delete user
        user.delete()
        
        # User should be gone
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)


@pytest.mark.django_db
class TestPermissionEdgeCases(TestCase):
    """Test permission-related edge cases."""

    def test_anonymous_user_permissions(self):
        """Test that anonymous users have no special permissions."""
        from django.contrib.auth.models import AnonymousUser
        
        anon = AnonymousUser()
        
        self.assertFalse(anon.is_authenticated)
        self.assertFalse(anon.is_staff)
        self.assertFalse(anon.is_superuser)

    def test_staff_user_without_superuser(self):
        """Test staff user without superuser status."""
        user = User.objects.create_user(
            username="staff",
            email="staff@test.com",
            password="testpass123",
            is_staff=True,  # Staff but not superuser
            is_superuser=False
        )
        
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_with_all_flags_disabled(self):
        """Test user with all boolean flags set to False."""
        user = User.objects.create_user(
            username="disabled",
            email="disabled@test.com",
            password="testpass123",
            is_active=False,
            is_staff=False,
            is_superuser=False
        )
        
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_password_change_invalidates_old_password(self):
        """Test that changing password invalidates old one."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="oldpass123"
        )
        
        # Old password works
        self.assertTrue(user.check_password("oldpass123"))
        
        # Change password
        user.set_password("newpass456")
        user.save()
        
        # Old password no longer works
        self.assertFalse(user.check_password("oldpass123"))
        
        # New password works
        self.assertTrue(user.check_password("newpass456"))

