from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.permissions import SAFE_METHODS, IsAdminUser
from rest_framework.test import APIRequestFactory

from core.permissions import IsOwnerOrAdmin


class TestIsOwnerOrAdminPermission(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )
        self.other_user = self.User.objects.create_user(
            username='otheruser', email='otheruser@example.com', password='TestPass123!'
        )
        self.permission = IsOwnerOrAdmin()

    def test_is_owner_permission_owner(self):
        """Test permission for object owner"""
        request = self.factory.get('/test/')
        request.user = self.user
        # Mock object with student field (per IsOwnerOrAdmin)
        obj = type('MockObject', (), {'student': self.user})()
        has_permission = self.permission.has_object_permission(request, None, obj)
        self.assertTrue(has_permission)

    def test_is_owner_permission_not_owner(self):
        """Test permission for non-owner"""
        request = self.factory.get('/test/')
        request.user = self.other_user
        obj = type('MockObject', (), {'student': self.user})()
        has_permission = self.permission.has_object_permission(request, None, obj)
        self.assertFalse(has_permission)

    def test_is_owner_permission_admin(self):
        """Test permission for admin user"""
        request = self.factory.get('/test/')
        request.user = self.user
        request.user.is_staff = True
        obj = type('MockObject', (), {'student': self.other_user})()
        has_permission = self.permission.has_object_permission(request, None, obj)
        self.assertTrue(has_permission)

    def test_is_owner_permission_safe_methods(self):
        """Test permission for safe methods"""
        for method in SAFE_METHODS:
            request = self.factory.request(method=method)
            request.user = self.user

            has_permission = self.permission.has_permission(request, None)
            self.assertTrue(has_permission)

class TestIsAdminUserPermission(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )
        self.admin_user = self.User.objects.create_user(
            username='adminuser', email='adminuser@example.com', password='TestPass123!',
            is_staff=True, is_superuser=True
        )
        self.permission = IsAdminUser()

    def test_is_admin_user_permission_admin(self):
        """Test permission for admin user"""
        request = self.factory.get('/test/')
        request.user = self.admin_user

        has_permission = self.permission.has_permission(request, None)
        self.assertTrue(has_permission)

    def test_is_admin_user_permission_regular_user(self):
        """Test permission for regular user"""
        request = self.factory.get('/test/')
        request.user = self.user

        has_permission = self.permission.has_permission(request, None)
        self.assertFalse(has_permission)

    def test_is_admin_user_permission_anonymous(self):
        """Test permission for anonymous user"""
        request = self.factory.get('/test/')
        request.user = None

        has_permission = self.permission.has_permission(request, None)
        self.assertFalse(has_permission)
