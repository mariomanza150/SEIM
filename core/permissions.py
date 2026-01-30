from rest_framework import permissions


# ============================================================================
# UNIFIED PERMISSION REGISTRY
# ============================================================================
# All permissions defined in one place. Source of truth for entire system.
# Format: 'permission_name': [list of roles that have this permission]
# ============================================================================

PERMISSION_REGISTRY = {
    # Application Permissions
    'view_own_applications': ['student', 'coordinator', 'admin'],
    'view_all_applications': ['coordinator', 'admin'],
    'create_application': ['student', 'coordinator', 'admin'],
    'edit_own_application': ['student', 'coordinator', 'admin'],
    'edit_any_application': ['coordinator', 'admin'],
    'delete_application': ['admin'],
    'review_application': ['coordinator', 'admin'],
    'change_application_status': ['coordinator', 'admin'],
    
    # Document Permissions
    'view_own_documents': ['student', 'coordinator', 'admin'],
    'view_all_documents': ['coordinator', 'admin'],
    'upload_document': ['student', 'coordinator', 'admin'],
    'edit_own_document': ['student', 'coordinator', 'admin'],
    'delete_own_document': ['student', 'coordinator', 'admin'],
    'validate_document': ['coordinator', 'admin'],
    'request_document_resubmission': ['coordinator', 'admin'],
    'delete_any_document': ['admin'],
    
    # Program Permissions
    'view_programs': ['student', 'coordinator', 'admin'],
    'create_program': ['admin'],
    'edit_program': ['admin'],
    'delete_program': ['admin'],
    'manage_program_availability': ['admin'],
    
    # User Management
    'view_own_profile': ['student', 'coordinator', 'admin'],
    'view_all_profiles': ['coordinator', 'admin'],
    'edit_own_profile': ['student', 'coordinator', 'admin'],
    'edit_any_profile': ['admin'],
    'manage_roles': ['admin'],
    'view_user_sessions': ['coordinator', 'admin'],
    'view_all_user_sessions': ['admin'],
    'view_login_times': ['coordinator', 'admin'],
    'revoke_user_session': ['admin'],
    'delete_user': ['admin'],
    
    # Analytics & Reporting
    'view_basic_analytics': ['coordinator', 'admin'],
    'view_full_analytics': ['admin'],
    'view_reports': ['coordinator', 'admin'],
    'export_data': ['coordinator', 'admin'],
    
    # System Administration
    'access_django_admin': ['admin'],
    'manage_cache': ['admin'],
    'manage_forms': ['admin'],
    'view_system_logs': ['admin'],
    'manage_settings': ['admin'],
    
    # Notifications
    'send_notification': ['coordinator', 'admin'],
    'send_bulk_notification': ['admin'],
    
    # Comments & Communication
    'add_comment': ['student', 'coordinator', 'admin'],
    'view_own_comments': ['student', 'coordinator', 'admin'],
    'view_all_comments': ['coordinator', 'admin'],
    'edit_own_comment': ['student', 'coordinator', 'admin'],
    'delete_own_comment': ['student', 'coordinator', 'admin'],
    'delete_any_comment': ['coordinator', 'admin'],
}


# ============================================================================
# PERMISSION MANAGER
# ============================================================================
# Central manager for all permission checks across the application
# ============================================================================

class PermissionManager:
    """
    Central manager for permission checks.
    
    This class provides static methods for checking user permissions
    based on the PERMISSION_REGISTRY. Use this instead of manual role checks.
    
    Examples:
        # In views
        if PermissionManager.user_has_permission(request.user, 'edit_application'):
            # Allow edit
        
        # Get all user permissions
        permissions = PermissionManager.get_user_permissions(request.user)
        
        # Get permissions for a role
        admin_perms = PermissionManager.get_role_permissions('admin')
    """
    
    @staticmethod
    def user_has_permission(user, permission_name):
        """
        Check if user has specific permission.
        
        Args:
            user: User instance
            permission_name: Name of permission to check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        if not user or not user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Get permission from registry
        allowed_roles = PERMISSION_REGISTRY.get(permission_name, [])
        if not allowed_roles:
            # Permission doesn't exist in registry
            return False
        
        # Get user's roles
        user_roles = user.get_all_roles()
        
        # Check if any user role has the permission
        return any(role in allowed_roles for role in user_roles)
    
    @staticmethod
    def get_user_permissions(user):
        """
        Get all permissions for a user based on their roles.
        
        Args:
            user: User instance
            
        Returns:
            list: Sorted list of permission names
        """
        if not user or not user.is_authenticated:
            return []
        
        if user.is_superuser:
            return sorted(PERMISSION_REGISTRY.keys())
        
        user_roles = user.get_all_roles()
        permissions = set()
        
        for perm_name, allowed_roles in PERMISSION_REGISTRY.items():
            if any(role in allowed_roles for role in user_roles):
                permissions.add(perm_name)
        
        return sorted(permissions)
    
    @staticmethod
    def get_role_permissions(role_name):
        """
        Get all permissions for a specific role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            list: Sorted list of permission names for this role
        """
        permissions = []
        for perm_name, allowed_roles in PERMISSION_REGISTRY.items():
            if role_name in allowed_roles:
                permissions.append(perm_name)
        return sorted(permissions)
    
    @staticmethod
    def validate_permission(permission_name):
        """
        Check if a permission exists in the registry.
        
        Args:
            permission_name: Name of permission to validate
            
        Returns:
            bool: True if permission exists, False otherwise
        """
        return permission_name in PERMISSION_REGISTRY
    
    @staticmethod
    def get_all_permissions():
        """
        Get all available permissions.
        
        Returns:
            list: Sorted list of all permission names
        """
        return sorted(PERMISSION_REGISTRY.keys())


# ============================================================================
# UNIFIED PERMISSION CLASSES
# ============================================================================
# DRF permission classes that use the unified permission system
# ============================================================================

class HasPermission(permissions.BasePermission):
    """
    Generic permission class that checks permission via PermissionManager.
    
    Usage in views:
        permission_classes = [HasPermission('edit_application')]
        
    Or create specific permission classes:
        class CanEditApplication(HasPermission):
            permission_name = 'edit_application'
    """
    
    permission_name = None  # Override in subclasses or pass to __init__
    
    def __init__(self, permission_name=None):
        """
        Initialize with permission name.
        
        Args:
            permission_name: Name of permission to check
        """
        if permission_name:
            self.permission_name = permission_name
        super().__init__()
    
    def has_permission(self, request, view):
        """Check if user has the permission."""
        if not self.permission_name:
            raise ValueError("permission_name must be set")
        
        return PermissionManager.user_has_permission(
            request.user,
            self.permission_name
        )
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.
        
        For "own" permissions, checks ownership first,
        then checks for "any" version of permission.
        """
        if not self.permission_name:
            raise ValueError("permission_name must be set")
        
        # Check if permission has "own" in the name
        if 'own' in self.permission_name:
            # Check ownership
            owner = getattr(obj, 'student', None) or getattr(obj, 'user', None)
            if owner == request.user:
                return True
            
            # Check if user has "any" version of permission
            any_permission = self.permission_name.replace('own', 'any')
            return PermissionManager.user_has_permission(
                request.user,
                any_permission
            )
        
        # For other permissions, just check if user has it
        return PermissionManager.user_has_permission(
            request.user,
            self.permission_name
        )


# ============================================================================
# BACKWARD COMPATIBLE PERMISSION CLASSES
# ============================================================================
# These maintain backward compatibility while using the new system
# ============================================================================

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access if user is admin/staff or is the object's owner (student).
    
    BACKWARD COMPATIBLE: Maintained for existing code.
    For new code, use HasPermission with appropriate permission names.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Check if admin or staff
        if user.is_staff or (hasattr(user, 'is_admin') and user.is_admin):
            return True
        
        # Check ownership
        owner = getattr(obj, "student", None) or getattr(obj, "user", None)
        return owner == user


class IsCoordinatorOrAdmin(permissions.BasePermission):
    """
    Allow access if user is admin/staff or has role 'coordinator' or 'admin'.
    
    BACKWARD COMPATIBLE: Maintained for existing code.
    Now uses multi-role aware checking via has_any_role().
    """

    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Check staff or superuser
        if user.is_staff or user.is_superuser:
            return True
        
        # Check for coordinator or admin role (multi-role aware)
        if hasattr(user, 'has_any_role'):
            return user.has_any_role(['coordinator', 'admin'])
        
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow admins to create/update/delete, but allow all authenticated users to read.

    Use for resources that only admins should modify (e.g., Programs).
    
    BACKWARD COMPATIBLE: Maintained for existing code.
    Now uses multi-role aware checking via is_admin property.
    """

    def has_permission(self, request, view):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions only for admins
        if not request.user or not request.user.is_authenticated:
            return False

        # Check using is_admin property (includes superuser)
        return (
            request.user.is_staff or
            (hasattr(request.user, 'is_admin') and request.user.is_admin)
        )


class IsStudentOrReadOnly(permissions.BasePermission):
    """
    Allow students to create, coordinators/admins to update, and all authenticated users to read.

    Use for resources that students create (e.g., Applications).
    
    BACKWARD COMPATIBLE: Maintained for existing code.
    Now uses multi-role aware checking via has_any_role().
    """

    def has_permission(self, request, view):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        if not request.user or not request.user.is_authenticated:
            return False

        # Only students can create (POST)
        if request.method == 'POST':
            return hasattr(request.user, 'has_any_role') and request.user.has_any_role(['student', 'coordinator', 'admin'])

        # Students, coordinators, and admins can update (PUT, PATCH, DELETE)
        return (
            hasattr(request.user, 'has_any_role') and 
            request.user.has_any_role(['student', 'coordinator', 'admin'])
        )

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Coordinators and admins can modify any application
        if hasattr(request.user, 'has_any_role') and request.user.has_any_role(['coordinator', 'admin']):
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
