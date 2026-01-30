# Quick Start: Roles and Permissions

**5-Minute Guide to the New Multi-Role System**

---

## For Developers: Permission Checks

### In Python Views

```python
# ✅ NEW WAY - Use properties
if user.is_admin:
    # Admin-only code

if user.is_coordinator:
    # Coordinator code

if user.is_student:
    # Student code

# Check multiple roles
if user.has_any_role(['coordinator', 'admin']):
    # For coordinators and admins

# Check permissions
if user.has_permission('edit_application'):
    # User can edit
```

### In Templates

```django
{# ✅ Use new properties #}
{% if user.is_admin %}
    <a href="/admin">Admin Panel</a>
{% endif %}

{% if user.is_coordinator %}
    <a href="/reviews">Reviews</a>
{% endif %}

{% if user.is_student %}
    <a href="/applications">My Applications</a>
{% endif %}
```

### In JavaScript

```javascript
// ✅ Check permissions (loaded from backend)
if (Auth.hasPermission('edit_application')) {
    // Show edit button
}

// Check roles
if (Auth.isAdmin()) {
    // Admin features
}

if (Auth.isCoordinator()) {
    // Coordinator features
}
```

---

## For Admins: Assign Roles

### Via Django Admin
1. Go to `/seim/admin/accounts/user/`
2. Click user
3. Scroll to "Roles" section
4. Select role(s): Student, Coordinator, Admin
5. Save

### Via User Management Page
1. Go to `/seim/user-management/`
2. View all users with their roles
3. Filter by role
4. Search for specific users

---

## User Roles Quick Reference

### Student
- Apply to programs
- Upload documents
- Track status

### Coordinator  
- Everything Student can do
- **+ Review applications**
- **+ Validate documents**
- **+ View user login times**

### Admin
- Everything Coordinator can do
- **+ Manage programs**
- **+ Manage users**
- **+ System configuration**

---

## New Features

### Coordinator Dashboard
**URL**: `/seim/coordinator-dashboard/`  
**Access**: Coordinators and Admins  
**Features**: Pending reviews, document validation, activity feed

### Session Management
**URL**: `/seim/sessions/`  
**Access**: All users  
**Features**: View/revoke active sessions, security monitoring

### User Management
**URL**: `/seim/user-management/`  
**Access**: Coordinators and Admins  
**Features**: View login times, search users, filter by role

### Resend Verification
**Endpoint**: `/api/accounts/resend-verification/`  
**Access**: Unauthenticated  
**Rate Limit**: 1 per 5 minutes

---

## API Endpoints

### Get User Permissions
```bash
GET /api/accounts/permissions/
Authorization: Bearer <jwt-token>

Response:
{
  "roles": ["student", "coordinator"],
  "primary_role": "coordinator",
  "permissions": ["view_own_applications", "review_application", ...],
  "is_admin": false,
  "is_coordinator": true,
  "is_student": true
}
```

### Resend Verification
```bash
POST /api/accounts/resend-verification/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

---

## Common Tasks

### Add Coordinator Role to User
```python
from accounts.models import User, Role

user = User.objects.get(email='user@example.com')
coordinator_role = Role.objects.get(name='coordinator')
user.roles.add(coordinator_role)
```

### Check User's All Roles
```python
user = User.objects.get(username='john')
print(user.get_all_roles())
# Output: ['student', 'coordinator']
```

### Check Permission
```python
from core.permissions import PermissionManager

has_perm = PermissionManager.user_has_permission(user, 'edit_application')
```

---

## Multi-Role Example

User has BOTH Student and Coordinator roles:
- ✅ Sees Student navigation (Applications, Calendar)
- ✅ Sees Coordinator navigation (Reviews)
- ✅ Has ALL Student permissions
- ✅ Has ALL Coordinator permissions
- ✅ `primary_role` = "coordinator" (higher priority)
- ✅ `is_student` = True
- ✅ `is_coordinator` = True

---

## Navigation Updates

### Student Nav
- Dashboard
- Programs
- Applications
- Calendar

### + Coordinator Nav
- **Reviews** (Coordinator Dashboard)

### + Admin Nav
- **Admin** (Admin Dashboard)
- **Form Builder**

---

## Troubleshooting

### Permission Denied?
1. Check user has correct role assigned
2. Log out and log back in
3. Clear browser cache
4. Verify at `/api/accounts/permissions/`

### Role Not Showing?
1. Check Django admin: User has role assigned?
2. Refresh page
3. Check `user.get_all_roles()` in shell

### JS Permissions Not Working?
1. Check network tab: `/api/accounts/permissions/` call
2. Check console for errors
3. Verify JWT token is valid

---

## More Information

- **Full Guide**: `docs/roles-and-permissions-guide.md`
- **Architecture**: `docs/role-permission-architecture.md`
- **Implementation**: `docs/MULTI_ROLE_IMPLEMENTATION.md`

---

**Quick Start Complete!** 🎉

For detailed information, see the full documentation.

