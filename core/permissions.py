from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access if user is admin/staff or is the object's owner (student)."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or getattr(obj, "student", None) == request.user


class IsCoordinatorOrAdmin(permissions.BasePermission):
    """Allow access if user is admin/staff or has role 'coordinator' or 'admin'."""

    def has_permission(self, request, view):
        user = request.user
        return user.is_staff or getattr(user, "role", None) in ["coordinator", "admin"]

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or getattr(user, "role", None) in ["coordinator", "admin"]


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow admins to create/update/delete, but allow all authenticated users to read.

    Use for resources that only admins should modify (e.g., Programs).
    """

    def has_permission(self, request, view):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions only for admins
        if not request.user or not request.user.is_authenticated:
            return False

        return (
            request.user.is_staff or
            (hasattr(request.user, 'has_role') and request.user.has_role('admin'))
        )


class IsStudentOrReadOnly(permissions.BasePermission):
    """
    Allow students to create, coordinators/admins to update, and all authenticated users to read.

    Use for resources that students create (e.g., Applications).
    """

    def has_permission(self, request, view):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        if not request.user or not request.user.is_authenticated:
            return False

        # Only students can create (POST)
        if request.method == 'POST':
            return hasattr(request.user, 'has_role') and request.user.has_role('student')

        # Students, coordinators, and admins can update (PUT, PATCH, DELETE)
        return (
            hasattr(request.user, 'has_role') and 
            (request.user.has_role('student') or 
             request.user.has_role('coordinator') or 
             request.user.has_role('admin'))
        )

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Coordinators and admins can modify any application
        if hasattr(request.user, 'has_role') and (request.user.has_role('coordinator') or request.user.has_role('admin')):
            return True

        # Students can only modify their own applications
        # Status transition validation happens in the serializer/service layer
        if hasattr(request.user, 'has_role') and request.user.has_role('student'):
            is_owner = getattr(obj, 'student', None) == request.user
            return is_owner

        return False


class IsOwner(permissions.BasePermission):
    """
    Allow access only to the owner of the object.

    Object must have either 'student' or 'user' attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Check both 'student' and 'user' attributes
        owner = getattr(obj, 'student', None) or getattr(obj, 'user', None)
        return owner == request.user
