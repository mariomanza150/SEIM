<!--
File: docs/AUTHENTICATION_AND_PERMISSIONS.md
Title: Authentication and Permissions Documentation
Purpose: Describe authentication mechanisms and role-based permissions in the SEIM system.
-->

# Authentication and Permissions Documentation

## Purpose
This document details the authentication methods and permission structure used in the SEIM system, including user roles, token usage, and best practices.

## Revision History
| Date       | Author              | Description                                 |
|------------|---------------------|---------------------------------------------|
| 2025-05-31 | Documentation Team  | Added template compliance, title, purpose, and revision history. |

## Overview

The SEIM system implements a comprehensive authentication and role-based permission system to control access to student exchange applications and related data.

## User Roles

The system defines four distinct user roles:

1. **STUDENT**: Can create and manage their own exchange applications
2. **COORDINATOR**: Can view all exchanges and provide initial review
3. **MANAGER**: Can approve/reject applications and manage the workflow
4. **ADMIN**: Has full access to all system features

## Authentication

### Token Authentication

The system uses Django REST Framework's token authentication for API access.

#### Login
```bash
POST /api/auth/login/
{
    "username": "user123",
    "password": "password123"
}

Response:
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": { ... },
    "profile": { ... }
}
```

#### Using the Token
Include the token in the Authorization header for authenticated requests:
```bash
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Registration
Students can self-register:
```bash
POST /api/auth/register/
{
    "username": "newstudent",
    "email": "student@example.com",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "institution": "University Name"
}
```

### Logout
```bash
POST /api/auth/logout/
Authorization: Token YOUR_TOKEN_HERE
```

## Permissions

### Exchange Permissions

| Action | Student | Coordinator | Manager | Admin |
|--------|---------|-------------|---------|-------|
| View own exchanges | ✓ | ✓ | ✓ | ✓ |
| View all exchanges | ✗ | ✓ | ✓ | ✓ |
| Create exchange | ✓ | ✓ | ✓ | ✓ |
| Update own exchange | ✓ | ✓ | ✓ | ✓ |
| Update any exchange | ✗ | ✗ | ✓ | ✓ |
| Delete exchange | ✗ | ✗ | ✓ | ✓ |
| Approve exchange | ✗ | ✗ | ✓ | ✓ |
| Reject exchange | ✗ | ✗ | ✓ | ✓ |

### Document Permissions

| Action | Student | Coordinator | Manager | Admin |
|--------|---------|-------------|---------|-------|
| View own documents | ✓ | ✓ | ✓ | ✓ |
| View all documents | ✗ | ✓ | ✓ | ✓ |
| Upload documents | ✓ | ✓ | ✓ | ✓ |
| Delete own documents | ✓ | ✓ | ✓ | ✓ |
| Delete any documents | ✗ | ✓ | ✓ | ✓ |
| Verify documents | ✗ | ✓ | ✓ | ✓ |

## Management Commands

### Create Staff User
```bash
python manage.py create_staff_user username email --role MANAGER --institution "University Name"
```

Options:
- `--role`: COORDINATOR, MANAGER, or ADMIN
- `--password`: Set password (or will be prompted)
- `--first-name`: User's first name
- `--last-name`: User's last name
- `--institution`: Institution name
- `--department`: Department name

### Setup Permission Groups
```bash
python manage.py setup_permissions
```

This command creates permission groups and assigns appropriate permissions to each group.

## Custom Permission Classes

The system uses custom permission classes to control access:

1. **IsOwnerOrStaff**: Allows owners of an object or staff to access it
2. **IsStudent**: Requires user to have student role
3. **IsCoordinator**: Requires user to have coordinator role
4. **IsManager**: Requires user to have manager role
5. **IsAdmin**: Requires user to have admin role
6. **IsStaffRole**: Requires user to have any staff role
7. **CanApproveExchange**: Requires approve permission
8. **CanRejectExchange**: Requires reject permission
9. **CanViewAllExchanges**: Requires view all permission

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/login/`: User login
- `POST /api/auth/register/`: User registration
- `POST /api/auth/logout/`: User logout
- `GET /api/auth/user/`: Get current user info
- `PUT /api/auth/profile/`: Update user profile
- `POST /api/auth/change-password/`: Change password

### Exchange Endpoints
- `GET /api/exchanges/`: List exchanges (filtered by permissions)
- `POST /api/exchanges/`: Create new exchange
- `GET /api/exchanges/{id}/`: Get exchange details
- `PUT /api/exchanges/{id}/`: Update exchange
- `DELETE /api/exchanges/{id}/`: Delete exchange
- `POST /api/exchanges/{id}/approve/`: Approve exchange
- `POST /api/exchanges/{id}/reject/`: Reject exchange
- `POST /api/exchanges/{id}/upload_document/`: Upload document

### Document Endpoints
- `GET /api/documents/`: List documents
- `POST /api/documents/`: Upload document
- `GET /api/documents/{id}/`: Get document details
- `PUT /api/documents/{id}/`: Update document
- `DELETE /api/documents/{id}/`: Delete document

## Security Considerations

1. **Password Requirements**: Minimum 8 characters
2. **Token Security**: Tokens should be stored securely and transmitted over HTTPS
3. **Rate Limiting**: API endpoints have rate limiting:
   - Anonymous users: 20 requests/hour
   - Authenticated users: 100 requests/hour
4. **File Upload Validation**: Only allowed file types are accepted
5. **Permission Checks**: All views perform appropriate permission checks

## Testing

The authentication and permission system can be tested using the provided test cases:

```bash
python manage.py test exchange.tests.test_authentication
```

## Troubleshooting

1. **"Not authorized" error**: Check that the user has the correct role and permissions
2. **Token invalid**: Ensure the token is correctly formatted in the Authorization header
3. **Permission denied**: Verify the user's role and the specific permission required for the action
4. **Registration fails**: Check that username and email are unique

## Future Enhancements

1. Implement JWT tokens for stateless authentication
2. Add OAuth2 integration for third-party authentication
3. Implement two-factor authentication
4. Add fine-grained permissions per institution
5. Implement audit logging for all permission-based actions
