from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.permissions import SAFE_METHODS, IsAdminUser
from rest_framework.test import APIRequestFactory

from core.permissions import (
    PERMISSION_REGISTRY,
    CanManageRoles,
    HasPermission,
    IsAdminOrReadOnly,
    IsAdminRole,
    IsCoordinatorOrAdmin,
    IsOwner,
    IsOwnerOrAdmin,
    IsStudentOrReadOnly,
    PermissionManager,
)
from tests.utils import TestUtils


class TestPermissionManager(TestCase):
    def setUp(self):
        self.student = TestUtils.create_test_user(
            username="perm_student", email="perm_student@example.com", role="student"
        )
        self.coordinator = TestUtils.create_test_user(
            username="perm_coord",
            email="perm_coord@example.com",
            role="coordinator",
        )
        self.admin = TestUtils.create_test_user(
            username="perm_admin", email="perm_admin@example.com", role="admin"
        )
        self.staff = TestUtils.create_test_user(
            username="perm_staff", email="perm_staff@example.com", role="student"
        )
        self.staff.is_staff = True
        self.staff.save(update_fields=["is_staff"])
        self.superuser = TestUtils.create_test_user(
            username="perm_super", email="perm_super@example.com", role="student"
        )
        self.superuser.is_superuser = True
        self.superuser.save(update_fields=["is_superuser"])

    def test_anonymous_and_missing_permission(self):
        self.assertFalse(
            PermissionManager.user_has_permission(None, "view_own_applications")
        )
        self.assertFalse(
            PermissionManager.user_has_permission(
                AnonymousUser(), "view_own_applications"
            )
        )
        self.assertFalse(
            PermissionManager.user_has_permission(self.student, "not_a_real_permission")
        )

    def test_role_and_staff_registry_checks(self):
        self.assertTrue(
            PermissionManager.user_has_permission(self.student, "view_own_applications")
        )
        self.assertFalse(
            PermissionManager.user_has_permission(self.student, "view_all_applications")
        )
        self.assertTrue(
            PermissionManager.user_has_permission(
                self.coordinator, "view_all_applications"
            )
        )
        self.assertTrue(
            PermissionManager.user_has_permission(self.admin, "manage_roles")
        )
        # Django staff inherits registry entries that include the admin role
        self.assertTrue(
            PermissionManager.user_has_permission(self.staff, "manage_workflows")
        )
        self.assertTrue(
            PermissionManager.user_has_permission(self.superuser, "delete_user")
        )

    def test_get_user_permissions_variants(self):
        self.assertEqual(PermissionManager.get_user_permissions(None), [])
        self.assertEqual(PermissionManager.get_user_permissions(AnonymousUser()), [])

        student_perms = PermissionManager.get_user_permissions(self.student)
        self.assertIn("view_own_applications", student_perms)
        self.assertNotIn("manage_roles", student_perms)
        self.assertEqual(student_perms, sorted(student_perms))

        super_perms = PermissionManager.get_user_permissions(self.superuser)
        self.assertEqual(super_perms, sorted(PERMISSION_REGISTRY.keys()))

        staff_perms = PermissionManager.get_user_permissions(self.staff)
        self.assertIn("manage_workflows", staff_perms)
        # staff still keeps student-role perms from attached role
        self.assertIn("view_own_applications", staff_perms)

    def test_role_and_registry_helpers(self):
        admin_perms = PermissionManager.get_role_permissions("admin")
        self.assertIn("manage_roles", admin_perms)
        self.assertEqual(admin_perms, sorted(admin_perms))
        self.assertEqual(PermissionManager.get_role_permissions("no_such_role"), [])

        self.assertTrue(PermissionManager.validate_permission("upload_document"))
        self.assertFalse(PermissionManager.validate_permission("nope"))
        self.assertEqual(
            PermissionManager.get_all_permissions(), sorted(PERMISSION_REGISTRY.keys())
        )


class TestHasPermission(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.student = TestUtils.create_test_user(
            username="has_student", email="has_student@example.com", role="student"
        )
        self.other = TestUtils.create_test_user(
            username="has_other", email="has_other@example.com", role="student"
        )
        self.coordinator = TestUtils.create_test_user(
            username="has_coord", email="has_coord@example.com", role="coordinator"
        )

    def test_requires_permission_name(self):
        bare = HasPermission()
        request = self.factory.get("/test/")
        request.user = self.student
        with self.assertRaises(ValueError):
            bare.has_permission(request, None)
        with self.assertRaises(ValueError):
            bare.has_object_permission(request, None, object())

    def test_view_level_permission(self):
        perm = HasPermission("view_all_applications")
        request = self.factory.get("/test/")
        request.user = self.student
        self.assertFalse(perm.has_permission(request, None))
        request.user = self.coordinator
        self.assertTrue(perm.has_permission(request, None))

    def test_own_object_permission_owner_and_any_fallback(self):
        perm = HasPermission("edit_own_application")
        request = self.factory.patch("/test/")
        request.user = self.student
        own = type("App", (), {"student": self.student, "user": None})()
        other = type("App", (), {"student": self.other, "user": None})()
        self.assertTrue(perm.has_object_permission(request, None, own))
        self.assertFalse(perm.has_object_permission(request, None, other))

        # coordinators have edit_any_application via registry replacement
        request.user = self.coordinator
        self.assertTrue(perm.has_object_permission(request, None, other))

    def test_non_own_permission_uses_registry(self):
        perm = HasPermission("review_application")
        request = self.factory.post("/test/")
        request.user = self.student
        obj = type("App", (), {"student": self.student})()
        self.assertFalse(perm.has_object_permission(request, None, obj))
        request.user = self.coordinator
        self.assertTrue(perm.has_object_permission(request, None, obj))

    def test_can_manage_roles_subclass(self):
        perm = CanManageRoles()
        request = self.factory.get("/test/")
        request.user = self.student
        self.assertFalse(perm.has_permission(request, None))
        admin = TestUtils.create_test_user(
            username="has_admin", email="has_admin@example.com", role="admin"
        )
        request.user = admin
        self.assertTrue(perm.has_permission(request, None))


class TestIsOwnerOrAdminPermission(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="testuser@example.com", password="TestPass123!"
        )
        self.other_user = self.User.objects.create_user(
            username="otheruser", email="otheruser@example.com", password="TestPass123!"
        )
        self.permission = IsOwnerOrAdmin()

    def test_is_owner_permission_owner(self):
        """Test permission for object owner"""
        request = self.factory.get("/test/")
        request.user = self.user
        # Mock object with student field (per IsOwnerOrAdmin)
        obj = type("MockObject", (), {"student": self.user})()
        has_permission = self.permission.has_object_permission(request, None, obj)
        self.assertTrue(has_permission)

    def test_is_owner_permission_not_owner(self):
        """Test permission for non-owner"""
        request = self.factory.get("/test/")
        request.user = self.other_user
        obj = type("MockObject", (), {"student": self.user})()
        has_permission = self.permission.has_object_permission(request, None, obj)
        self.assertFalse(has_permission)

    def test_is_owner_permission_admin(self):
        """Test permission for admin user on non-document objects"""
        request = self.factory.get("/test/")
        request.user = self.user
        request.user.is_staff = True
        obj = type("MockObject", (), {"student": self.other_user})()
        has_permission = self.permission.has_object_permission(request, None, obj)
        self.assertTrue(has_permission)

    def test_document_staff_can_read_but_not_write(self):
        request_get = self.factory.get("/test/")
        request_get.user = self.user
        request_get.user.is_staff = True
        request_patch = self.factory.patch("/test/")
        request_patch.user = self.user
        request_patch.user.is_staff = True

        app = type("App", (), {"student_id": self.other_user.id})()
        obj = type(
            "MockDocument",
            (),
            {
                "_meta": type("Meta", (), {"model_name": "document"})(),
                "application": app,
                "uploaded_by_id": self.other_user.id,
            },
        )()
        self.assertTrue(self.permission.has_object_permission(request_get, None, obj))
        self.assertFalse(
            self.permission.has_object_permission(request_patch, None, obj)
        )

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
            username="testuser", email="testuser@example.com", password="TestPass123!"
        )
        self.admin_user = self.User.objects.create_user(
            username="adminuser",
            email="adminuser@example.com",
            password="TestPass123!",
            is_staff=True,
            is_superuser=True,
        )
        self.permission = IsAdminUser()

    def test_is_admin_user_permission_admin(self):
        """Test permission for admin user"""
        request = self.factory.get("/test/")
        request.user = self.admin_user

        has_permission = self.permission.has_permission(request, None)
        self.assertTrue(has_permission)

    def test_is_admin_user_permission_regular_user(self):
        """Test permission for regular user"""
        request = self.factory.get("/test/")
        request.user = self.user

        has_permission = self.permission.has_permission(request, None)
        self.assertFalse(has_permission)

    def test_is_admin_user_permission_anonymous(self):
        """Test permission for anonymous user"""
        request = self.factory.get("/test/")
        request.user = None

        has_permission = self.permission.has_permission(request, None)
        self.assertFalse(has_permission)


class TestIsCoordinatorOrAdmin(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsCoordinatorOrAdmin()
        self.student = TestUtils.create_test_user(
            username="coa_student", email="coa_student@example.com", role="student"
        )
        self.coordinator = TestUtils.create_test_user(
            username="coa_coord", email="coa_coord@example.com", role="coordinator"
        )

    def test_anonymous_denied(self):
        request = self.factory.get("/test/")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))
        request.user = None
        self.assertFalse(self.permission.has_permission(request, None))

    def test_roles_and_staff(self):
        request = self.factory.get("/test/")
        request.user = self.student
        self.assertFalse(self.permission.has_permission(request, None))

        request.user = self.coordinator
        self.assertTrue(self.permission.has_permission(request, None))
        self.assertTrue(
            self.permission.has_object_permission(request, None, object())
        )

        staff = TestUtils.create_test_user(
            username="coa_staff", email="coa_staff@example.com", role="student"
        )
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])
        request.user = staff
        self.assertTrue(self.permission.has_permission(request, None))

    def test_user_without_has_any_role_denied(self):
        request = self.factory.get("/test/")
        bare = type("BareUser", (), {"is_authenticated": True, "is_staff": False, "is_superuser": False})()
        request.user = bare
        self.assertFalse(self.permission.has_permission(request, None))


class TestIsAdminRole(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsAdminRole()
        self.coordinator = TestUtils.create_test_user(
            username="iar_coord", email="iar_coord@example.com", role="coordinator"
        )
        self.admin = TestUtils.create_test_user(
            username="iar_admin", email="iar_admin@example.com", role="admin"
        )

    def test_coordinator_denied_admin_allowed(self):
        request = self.factory.get("/test/")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))

        request.user = self.coordinator
        self.assertFalse(self.permission.has_permission(request, None))

        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))
        self.assertTrue(
            self.permission.has_object_permission(request, None, object())
        )

    def test_staff_and_is_admin_property(self):
        request = self.factory.get("/test/")
        staff = TestUtils.create_test_user(
            username="iar_staff", email="iar_staff@example.com", role="student"
        )
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])
        request.user = staff
        self.assertTrue(self.permission.has_permission(request, None))


class TestIsAdminOrReadOnly(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsAdminOrReadOnly()
        self.student = TestUtils.create_test_user(
            username="aor_student", email="aor_student@example.com", role="student"
        )
        self.admin = TestUtils.create_test_user(
            username="aor_admin", email="aor_admin@example.com", role="admin"
        )

    def test_authenticated_reads_allowed(self):
        request = self.factory.get("/test/")
        request.user = self.student
        self.assertTrue(self.permission.has_permission(request, None))
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))

    def test_writes_require_admin(self):
        request = self.factory.post("/test/")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))
        request.user = self.student
        self.assertFalse(self.permission.has_permission(request, None))
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))


class TestIsStudentOrReadOnly(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsStudentOrReadOnly()
        self.student = TestUtils.create_test_user(
            username="sor_student", email="sor_student@example.com", role="student"
        )
        self.other = TestUtils.create_test_user(
            username="sor_other", email="sor_other@example.com", role="student"
        )
        self.coordinator = TestUtils.create_test_user(
            username="sor_coord", email="sor_coord@example.com", role="coordinator"
        )

    def test_view_level_create_and_update(self):
        get_req = self.factory.get("/test/")
        get_req.user = self.student
        self.assertTrue(self.permission.has_permission(get_req, None))

        post = self.factory.post("/test/")
        post.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(post, None))
        post.user = self.student
        self.assertTrue(self.permission.has_permission(post, None))

        patch = self.factory.patch("/test/")
        patch.user = self.student
        self.assertTrue(self.permission.has_permission(patch, None))

    def test_object_isolation_for_students(self):
        own = type("App", (), {"student": self.student})()
        other = type("App", (), {"student": self.other})()

        get_req = self.factory.get("/test/")
        get_req.user = self.student
        self.assertTrue(self.permission.has_object_permission(get_req, None, other))

        patch = self.factory.patch("/test/")
        patch.user = self.student
        self.assertTrue(self.permission.has_object_permission(patch, None, own))
        self.assertFalse(self.permission.has_object_permission(patch, None, other))

        patch.user = self.coordinator
        self.assertTrue(self.permission.has_object_permission(patch, None, other))

    def test_non_role_user_denied_on_write(self):
        patch = self.factory.patch("/test/")
        bare = type(
            "BareUser",
            (),
            {"is_authenticated": True, "has_any_role": lambda self, roles: False},
        )()
        patch.user = bare
        obj = type("App", (), {"student": self.student})()
        self.assertFalse(self.permission.has_object_permission(patch, None, obj))


class TestIsOwner(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsOwner()
        self.owner = TestUtils.create_test_user(
            username="own_owner", email="own_owner@example.com", role="student"
        )
        self.other = TestUtils.create_test_user(
            username="own_other", email="own_other@example.com", role="student"
        )

    def test_student_or_user_attribute(self):
        request = self.factory.get("/test/")
        request.user = self.owner
        via_student = type("Obj", (), {"student": self.owner, "user": None})()
        via_user = type("Obj", (), {"student": None, "user": self.owner})()
        other = type("Obj", (), {"student": self.other, "user": None})()
        self.assertTrue(self.permission.has_object_permission(request, None, via_student))
        self.assertTrue(self.permission.has_object_permission(request, None, via_user))
        self.assertFalse(self.permission.has_object_permission(request, None, other))
