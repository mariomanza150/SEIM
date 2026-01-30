# Roles and Permissions Guide - SEIM

## Table of Contents
1. [Overview](#overview)
2. [User Roles](#user-roles)
3. [Permissions System](#permissions-system)
4. [For Developers](#for-developers)
5. [For Admins](#for-admins)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

---

## Overview

SEIM uses a comprehensive multi-role and permissions system that allows:
- **Multi-Role Support**: Users can have multiple roles simultaneously
- **Granular Permissions**: Fine-grained control over what users can do
- **Hierarchical Access**: Admin > Coordinator > Student
- **Dynamic UI**: Interface adapts based on user permissions
- **Session Management**: View and revoke active login sessions

---

## User Roles

### Student (Base Role)
**Purpose**: Regular users applying to exchange programs

**Capabilities**:
- View and browse exchange programs
- Create and submit applications
- Upload required documents
- Track application status
- View personal profile and settings
- Manage own active sessions

**Dashboard**: Shows my applications, available programs, and deadlines

### Coordinator
**Purpose**: Staff members who review and manage applications

**Capabilities**:
- All Student capabilities, PLUS:
- View all applications (not just own)
- Review and comment on applications
- Validate uploaded documents
- Request document resubmissions
- View limited analytics
- View all user profiles
- See user login times and sessions

**Dashboard**: Coordinator dashboard with pending reviews and documents

### Admin (Highest Role)
**Purpose**: System administrators with full access

**Capabilities**:
- All Coordinator capabilities, PLUS:
- Manage exchange programs (create, edit, delete)
- Manage users and assign roles
- Access Django admin interface
- View full analytics and reports
- Clear system cache
- Manage dynamic forms
- Revoke any user's sessions
- Export data
- System configuration

**Dashboard**: Admin dashboard with system metrics and management tools

---

## Permissions System

### How It Works

1. **Permission Registry**: All permissions defined in `core/permissions.py`
2. **Role-Based**: Permissions granted based on user's roles
3. **Backend Validation**: Server validates all actions
4. **Frontend Adaptation**: UI shows/hides features based on permissions

### Key Permissions

#### Application Permissions
- `view_own_applications` - View your applications
- `view_all_applications` - View all applications
- `create_application` - Create new application
- `edit_own_application` - Edit your applications
- `edit_any_application` - Edit any application
- `delete_application` - Delete applications
- `review_application` - Review and comment
- `change_application_status` - Change status

#### Document Permissions
- `view_own_documents` - View your documents
- `view_all_documents` - View all documents
- `upload_document` - Upload documents
- `validate_document` - Validate documents
- `request_document_resubmission` - Request resubmission

#### Program Permissions
- `view_programs` - View program listings
- `create_program` - Create new programs
- `edit_program` - Edit programs
- `delete_program` - Delete programs

#### User Management
- `view_own_profile` - View your profile
- `view_all_profiles` - View all profiles
- `edit_own_profile` - Edit your profile
- `edit_any_profile` - Edit any profile
- `manage_roles` - Assign/remove roles
- `view_user_sessions` - View user sessions
- `view_login_times` - See last login times

#### System Administration
- `access_django_admin` - Django admin access
- `manage_cache` - Clear system cache
- `manage_forms` - Manage dynamic forms
- `view_system_logs` - View logs
- `manage_settings` - System settings

---

## For Developers

### Checking Permissions in Python

#### In Views

```python
from django.contrib.auth.decorators import login_required

@login_required
def my_view(request):
    user = request.user
    
    # Check single role
    if user.has_role('admin'):
        # Admin-only logic
        pass
    
    # Check multiple roles
    if user.has_any_role(['coordinator', 'admin']):
        # For coordinators and admins
        pass
    
    # Check permission
    if user.has_permission('edit_application'):
        # User can edit applications
        pass
    
    # Using properties
    if user.is_admin:
        # Admin user
        pass
    if user.is_coordinator:
        # Coordinator
        pass
    if user.is_student:
        # Student
        pass
```

#### In DRF ViewSets

```python
from rest_framework import viewsets
from core.permissions import HasPermission

class ApplicationViewSet(viewsets.ModelViewSet):
    # Use unified permission system
    permission_classes = [HasPermission('view_application')]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.has_any_role(['coordinator', 'admin']):
            return Application.objects.all()
        else:
            return Application.objects.filter(student=user)
```

#### Using PermissionManager Directly

```python
from core.permissions import PermissionManager

# Check if user has permission
if PermissionManager.user_has_permission(user, 'delete_application'):
    # Allow deletion
    pass

# Get all user permissions
permissions = PermissionManager.get_user_permissions(user)
# Returns: ['view_own_applications', 'create_application', ...]

# Get all roles
roles = user.get_all_roles()
# Returns: ['student', 'coordinator']
```

### Checking Permissions in Templates

```django
{% load i18n %}

{# Check single role #}
{% if user.is_admin %}
    <a href="{% url 'admin:index' %}">Admin Panel</a>
{% endif %}

{# Check coordinator or admin #}
{% if user.is_coordinator or user.is_admin %}
    <a href="{% url 'frontend:coordinator_dashboard' %}">Reviews</a>
{% endif %}

{# Check student #}
{% if user.is_student %}
    <a href="{% url 'frontend:applications' %}">My Applications</a>
{% endif %}

{# Display all roles #}
<p>Your roles:
{% for role in user.roles.all %}
    <span class="badge">{{ role.name }}</span>
{% endfor %}
</p>
```

### Checking Permissions in JavaScript

```javascript
// After authentication, permissions are available via Auth module

// Check if user has permission
if (Auth.hasPermission('edit_application')) {
    // Show edit button
}

// Check if user has role
if (Auth.hasRole('admin')) {
    // Show admin features
}

// Check if user has any of multiple roles
if (Auth.hasAnyRole(['coordinator', 'admin'])) {
    // Show coordinator/admin features
}

// Get user's permissions
const permissions = Auth.getPermissions();
// Returns: ['view_own_applications', 'create_application', ...]

// Get user's roles
const roles = Auth.getRoles();
// Returns: ['student', 'coordinator']

// Get primary role
const primaryRole = Auth.getPrimaryRole();
// Returns: 'coordinator' (highest priority role)

// Use convenience methods
if (Auth.isAdmin()) {
    // Admin user
}
if (Auth.isCoordinator()) {
    // Coordinator
}
if (Auth.isStudent()) {
    // Student
}
```

### Adding New Permissions

1. **Add to Permission Registry** (`core/permissions.py`):

```python
PERMISSION_REGISTRY = {
    # ... existing permissions ...
    
    # Add new permission
    'approve_budget': ['admin'],  # Only admins can approve budgets
    'submit_report': ['coordinator', 'admin'],  # Coordinators and admins
}
```

2. **Use in Views**:

```python
@login_required
def approve_budget_view(request, budget_id):
    if not request.user.has_permission('approve_budget'):
        return HttpResponseForbidden("You don't have permission")
    
    # Approve budget logic
    ...
```

3. **Use in Templates**:

```django
{% if user.has_permission('approve_budget') %}
    <button>Approve Budget</button>
{% endif %}
```

4. **Update JavaScript** (permissions auto-fetched from API):

```javascript
if (Auth.hasPermission('approve_budget')) {
    // Show approve button
}
```

---

## For Admins

### Managing User Roles

#### Via Django Admin

1. Go to `/seim/admin/accounts/user/`
2. Select user
3. In "Roles" section, select role(s) to assign
4. Save

#### Via User Management Page

1. Go to `/seim/user-management/`
2. Find user
3. View their current roles
4. Use filters to find users by role

### Default Role Assignments

- New users automatically get **Student** role
- Coordinators must be assigned by admins
- Admins must be assigned by superusers

### Multi-Role Users

Users can have multiple roles. Priority order:
1. Admin (highest)
2. Coordinator
3. Student (lowest)

Example: A user with both Student and Coordinator roles:
- Has all Student permissions
- Has all Coordinator permissions
- Primary role shown: "Coordinator"
- Sees both student and coordinator navigation

### Session Management

#### For All Users
- Users can view their own active sessions at `/seim/sessions/`
- Can revoke individual sessions
- Can revoke all other sessions

#### For Admins/Coordinators
- View all users' login times at `/seim/user-management/`
- See active session counts
- Filter by role
- Search users
- Export data

---

## Examples

### Example 1: Adding a New Coordinator

```python
# In Django shell or admin action
from accounts.models import User, Role

user = User.objects.get(email='coordinator@example.com')
coordinator_role = Role.objects.get(name='coordinator')
user.roles.add(coordinator_role)
```

### Example 2: Checking Multi-Role Access

```python
# User has both student and coordinator roles
user = User.objects.get(username='john')

print(user.get_all_roles())
# Output: ['student', 'coordinator']

print(user.primary_role)
# Output: 'coordinator' (higher priority)

print(user.has_role('student'))
# Output: True

print(user.has_role('admin'))
# Output: False

print(user.has_any_role(['coordinator', 'admin']))
# Output: True
```

### Example 3: Custom Permission Check

```python
from core.permissions import PermissionManager

# View requiring coordinator or admin
@login_required
def review_dashboard_view(request):
    if not PermissionManager.user_has_permission(request.user, 'review_application'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('frontend:dashboard')
    
    # Dashboard logic
    ...
```

### Example 4: Dynamic Navigation

```django
<!-- Navigation adapts to user roles -->
<nav>
    {% if user.is_authenticated %}
        <a href="{% url 'frontend:dashboard' %}">Dashboard</a>
        
        {% if user.is_student %}
            <a href="{% url 'frontend:applications' %}">My Applications</a>
        {% endif %}
        
        {% if user.is_coordinator %}
            <a href="{% url 'frontend:coordinator_dashboard' %}">Reviews</a>
        {% endif %}
        
        {% if user.is_admin %}
            <a href="{% url 'frontend:admin_dashboard' %}">Admin</a>
            <a href="{% url 'admin:index' %}">Django Admin</a>
        {% endif %}
    {% endif %}
</nav>
```

---

## Troubleshooting

### Permission Denied Errors

**Problem**: User gets "Permission Denied" when accessing a page

**Solutions**:
1. Check user has correct role assigned
2. Verify permission exists in PERMISSION_REGISTRY
3. Check role is listed for that permission
4. Clear browser cache and re-login
5. Check user account is active and email verified

### Role Not Showing

**Problem**: User has role but it's not reflected in UI

**Solutions**:
1. Log out and log back in
2. Clear browser cache
3. Check permissions API: `/api/accounts/permissions/`
4. Verify role assignment in Django admin

### Multi-Role Conflicts

**Problem**: User has multiple roles and behavior is unexpected

**Solutions**:
1. Check `primary_role` - this determines main behavior
2. Verify permission inheritance is correct
3. Use `has_any_role()` instead of checking `primary_role`
4. Check permission registry for role order

### Session Issues

**Problem**: Can't see/revoke sessions

**Solutions**:
1. Ensure UserSession model is populated
2. Check user has permission: `view_user_sessions`
3. Verify session tracking middleware is active
4. Check database for session records

### JavaScript Permissions Not Loading

**Problem**: Auth.hasPermission() always returns false

**Solutions**:
1. Check network tab for `/api/accounts/permissions/` call
2. Verify JWT token is valid
3. Check browser console for errors
4. Ensure `fetchUserPermissions()` is called after login
5. Verify user is authenticated

---

## API Endpoints

### Get User Permissions
```
GET /api/accounts/permissions/
```

**Response**:
```json
{
  "roles": ["student", "coordinator"],
  "primary_role": "coordinator",
  "permissions": [
    "view_own_applications",
    "view_all_applications",
    "create_application",
    "review_application",
    ...
  ],
  "is_admin": false,
  "is_coordinator": true,
  "is_student": true
}
```

### Resend Verification Email
```
POST /api/accounts/resend-verification/
Body: {"email": "user@example.com"}
```

### View User Sessions
```
GET /api/accounts/sessions/
```

### Revoke Session
```
POST /api/accounts/sessions/{session_id}/revoke/
```

---

## Security Considerations

1. **Always validate on backend**: Frontend checks are for UX only
2. **Use permissions, not just roles**: More granular control
3. **Multi-role awareness**: Check all roles, not just primary
4. **Session monitoring**: Review active sessions regularly
5. **Email verification**: Required before account activation
6. **Account lockout**: 5 failed attempts = 30 min lockout
7. **Token expiry**: JWT tokens expire and must be refreshed

---

## Support

For issues or questions:
1. Check this documentation
2. Review architecture docs: `docs/role-permission-architecture.md`
3. Contact system administrator
4. File issue in project repository

---

**Last Updated**: 2025-11-20  
**Version**: 2.0  
**Author**: SEIM Development Team

