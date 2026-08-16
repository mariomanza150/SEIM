# Role and Permission Architecture - SEIM

## Overview
This document describes the comprehensive multi-role and unified permissions architecture for SEIM.

## Current Issues Identified

### 1. Role System Inconsistencies
- **Model**: Uses many-to-many `roles` field (correct for multi-role)
- **Views**: Often use `.role` property which returns only first role
- **Templates**: Check `user.role == 'admin'` (single role assumption)
- **Scattered helpers**: Multiple `is_admin()` functions in different files

### 2. Permission Fragmentation
- **JavaScript**: Hardcoded permission lists in `static/js/auth.js`
- **Python**: Custom DRF permission classes in `core/permissions.py`
- **Database**: Role and Permission models exist but underutilized

### 3. Navigation Issues
- Admin navigation visible only to admin role
- No coordinator-specific navigation
- Templates don't handle multi-role scenarios

---

## New Multi-Role Architecture

### Design Principles

1. **Multi-Role Support**: Users can have multiple roles simultaneously
2. **Hierarchical Permissions**: Admin > Coordinator > Student
3. **Explicit Permissions**: All permissions defined in one place
4. **Backend as Source of Truth**: JS permissions fetched from backend
5. **Consistent API**: Same role-checking methods everywhere

### Role Definitions

#### **Student** (Base Role)
- View own applications and documents
- Create applications
- Upload documents
- View programs
- Edit own profile

#### **Coordinator** (Includes Student Permissions)
- View all applications
- Review and comment on applications
- Request document resubmissions
- View all user profiles
- View analytics dashboard
- View user login times

#### **Admin** (Includes All Permissions)
- All Coordinator permissions
- Manage programs
- Manage users and roles
- Access Django admin
- Clear cache
- Manage forms
- Access full analytics

### Permission Hierarchy

```
Admin
  ├─ All system permissions
  ├─ Coordinator permissions
  │    ├─ Review applications
  │    ├─ Manage documents
  │    ├─ View analytics
  │    └─ Student permissions
  │         ├─ Create applications
  │         ├─ View own data
  │         └─ Upload documents
  └─ System management
```

---

## Unified Permissions Framework

### 1. Permission Registry

All permissions defined in `core/permissions.py`:

```python
PERMISSION_REGISTRY = {
    # Application Permissions
    'view_own_applications': ['student', 'coordinator', 'admin'],
    'view_all_applications': ['coordinator', 'admin'],
    'create_application': ['student', 'coordinator', 'admin'],
    'edit_own_application': ['student', 'coordinator', 'admin'],
    'edit_any_application': ['coordinator', 'admin'],
    'delete_application': ['admin'],
    
    # Document Permissions
    'view_own_documents': ['student', 'coordinator', 'admin'],
    'view_all_documents': ['coordinator', 'admin'],
    'upload_document': ['student', 'coordinator', 'admin'],
    'validate_document': ['coordinator', 'admin'],
    'request_document_resubmission': ['coordinator', 'admin'],
    
    # Program Permissions
    'view_programs': ['student', 'coordinator', 'admin'],
    'create_program': ['admin'],
    'edit_program': ['admin'],
    'delete_program': ['admin'],
    
    # User Management
    'view_own_profile': ['student', 'coordinator', 'admin'],
    'view_all_profiles': ['coordinator', 'admin'],
    'edit_own_profile': ['student', 'coordinator', 'admin'],
    'edit_any_profile': ['admin'],
    'manage_roles': ['admin'],
    'view_user_sessions': ['coordinator', 'admin'],
    'view_login_times': ['coordinator', 'admin'],
    
    # Analytics
    'view_basic_analytics': ['coordinator', 'admin'],
    'view_full_analytics': ['admin'],
    
    # System
    'access_django_admin': ['admin'],
    'manage_cache': ['admin'],
    'manage_forms': ['admin'],
}
```

### 2. Updated User Model Methods

```python
class User(AbstractUser, UUIDModel, TimeStampedModel):
    # ... existing fields ...
    
    def has_role(self, role_name):
        """Check if user has specific role."""
        return self.roles.filter(name=role_name).exists()
    
    def has_any_role(self, role_names):
        """Check if user has any of the specified roles."""
        return self.roles.filter(name__in=role_names).exists()
    
    def has_all_roles(self, role_names):
        """Check if user has all of the specified roles."""
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
        """Check if user has admin role."""
        return self.has_role('admin') or self.is_superuser
    
    @property
    def is_coordinator(self):
        """Check if user has coordinator role."""
        return self.has_role('coordinator')
    
    @property
    def is_student(self):
        """Check if user has student role."""
        return self.has_role('student')
```

### 3. Unified Permission Classes

```python
# core/permissions.py

class HasPermission(permissions.BasePermission):
    """
    Generic permission class that checks permission via PermissionManager.
    Usage: permission_classes = [HasPermission('edit_application')]
    """
    
    def __init__(self, permission_name):
        self.permission_name = permission_name
    
    def has_permission(self, request, view):
        return PermissionManager.user_has_permission(
            request.user, 
            self.permission_name
        )
    
    def has_object_permission(self, request, view, obj):
        # Check ownership for "own" permissions
        if 'own' in self.permission_name:
            owner = getattr(obj, 'student', None) or getattr(obj, 'user', None)
            if owner != request.user:
                # Check if user has "any" version of permission
                any_permission = self.permission_name.replace('own', 'any')
                return PermissionManager.user_has_permission(
                    request.user, 
                    any_permission
                )
        
        return PermissionManager.user_has_permission(
            request.user, 
            self.permission_name
        )
```

### 4. Permission Manager

Central manager for all permission checks:

```python
class PermissionManager:
    """Central manager for permission checks."""
    
    @staticmethod
    def user_has_permission(user, permission_name):
        """Check if user has specific permission."""
        if not user or not user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Get user's roles
        user_roles = user.get_all_roles()
        
        # Check if any user role has the permission
        allowed_roles = PERMISSION_REGISTRY.get(permission_name, [])
        return any(role in allowed_roles for role in user_roles)
    
    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user."""
        if not user or not user.is_authenticated:
            return []
        
        if user.is_superuser:
            return list(PERMISSION_REGISTRY.keys())
        
        user_roles = user.get_all_roles()
        permissions = set()
        
        for perm_name, allowed_roles in PERMISSION_REGISTRY.items():
            if any(role in allowed_roles for role in user_roles):
                permissions.add(perm_name)
        
        return sorted(permissions)
    
    @staticmethod
    def get_role_permissions(role_name):
        """Get all permissions for a specific role."""
        permissions = []
        for perm_name, allowed_roles in PERMISSION_REGISTRY.items():
            if role_name in allowed_roles:
                permissions.append(perm_name)
        return sorted(permissions)
```

### 5. API Endpoint for JS Permissions

```python
# accounts/views.py

class UserPermissionsView(APIView):
    """
    API endpoint to get current user's permissions.
    Used by frontend JavaScript.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'roles': user.get_all_roles(),
            'primary_role': user.primary_role,
            'permissions': user.get_all_permissions(),
            'is_admin': user.is_admin,
            'is_coordinator': user.is_coordinator,
            'is_student': user.is_student,
        })
```

---

## Dashboard Structure

### 1. Student Dashboard
- My Applications (list view)
- Available Programs
- My Documents
- Application Status
- Upcoming Deadlines

### 2. Coordinator Dashboard (NEW)
- All Applications (with filters)
- Pending Reviews
- Document Validations Required
- User Management (view only)
- Analytics (limited)
- Recent Activity

### 3. Admin Dashboard
- All Coordinator features
- System Statistics
- User Management (full CRUD)
- Program Management
- System Settings
- Full Analytics
- Cache Management

---

## Session Management

### User Session UI
- View all active sessions
- See device, location, IP, last activity
- Revoke individual sessions
- View login history

### Admin/Coordinator Features
- View all user sessions
- See last login times for all users
- Filter by role (student, coordinator, admin)
- Search users
- Export login reports

---

## Email Verification Flow

### Resend Verification
1. Login attempt with unverified email shows message
2. "Resend verification email" button
3. Rate limiting (1 per 5 minutes)
4. Email sent with new token
5. Success message displayed

---

## Navigation Updates

### For Students
- Dashboard
- Programs
- Applications
- Calendar
- Profile/Settings

### For Coordinators (Additional)
- Coordinator Dashboard
- All Applications (review mode)
- User Management (view)
- Analytics

### For Admins (Additional)
- Admin Dashboard
- System Settings
- Django Admin
- Form Builder
- Full User Management

---

## Implementation Plan

1. ✅ Document architecture
2. Update User model with new methods
3. Create PermissionManager and PERMISSION_REGISTRY
4. Update all permission classes
5. Create UserPermissionsView API endpoint
6. Update JavaScript to fetch permissions from API
7. Build coordinator dashboard
8. Create session management UI
9. Add login time tracking for admins/coordinators
10. Implement resend verification flow
11. Update all views to use unified permissions
12. Update all templates for multi-role
13. Update navigation component
14. Write comprehensive tests
15. Document usage and examples

---

## Migration Strategy

### Phase 1: Backend (Non-Breaking)
- Add new User methods (keep old ones)
- Add PermissionManager
- Add API endpoint
- Test thoroughly

### Phase 2: Views & Permissions
- Update views one by one
- Use new permission classes
- Maintain backward compatibility

### Phase 3: Frontend
- Update JS to use API permissions
- Update templates gradually
- Update navigation

### Phase 4: Cleanup
- Remove old permission classes
- Remove `.role` property usage
- Remove hardcoded JS permissions
- Final testing

---

## Testing Strategy

### Unit Tests
- User role methods
- PermissionManager logic
- Individual permission classes
- API endpoint

### Integration Tests
- Multi-role scenarios
- Permission inheritance
- View access control
- Navigation rendering

### End-to-End Tests
- Login flows
- Dashboard access
- Role-based features
- Session management

---

## Documentation Requirements

1. **Developer Guide**
   - How to add new permissions
   - How to check permissions in views
   - How to check permissions in templates
   - How to check permissions in JS

2. **User Guide**
   - Role descriptions
   - Feature access by role
   - Session management
   - Security best practices

3. **API Documentation**
   - Permissions endpoint
   - Session endpoints
   - Role management endpoints

4. **Migration Guide**
   - For existing installations
   - Database updates required
   - Code changes needed

