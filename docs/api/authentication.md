# Authentication API

The SEIM system uses JWT (JSON Web Tokens) for authentication. This document describes the authentication endpoints and usage.

## Endpoints

### Login

Authenticate a user and receive a JWT token.

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "role": "student",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Account disabled

### Logout

Invalidate the current JWT token.

**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### Refresh Token

Get a new JWT token using a refresh token (if implemented).

**Endpoint:** `POST /api/auth/refresh/`

**Request:**
```json
{
  "refresh": "refresh-token-here"
}
```

**Response:**
```json
{
  "access": "new-jwt-token-here"
}
```

### Verify Token

Check if a JWT token is valid.

**Endpoint:** `POST /api/auth/verify/`

**Request:**
```json
{
  "token": "jwt-token-to-verify"
}
```

**Response:**
```json
{
  "valid": true,
  "user_id": 1,
  "expires_at": "2025-01-15T12:00:00Z"
}
```

## Using Authentication

### 1. Initial Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "student@example.com", "password": "password123"}'
```

### 2. Store the Token

Save the returned token securely in your application:

```javascript
// JavaScript example
localStorage.setItem('jwt_token', response.token);
```

### 3. Include Token in Requests

Include the token in the Authorization header for all subsequent requests:

```bash
curl -X GET http://localhost:8000/api/exchanges/ \
     -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 4. Handle Token Expiration

Tokens expire after a configured time (default: 60 minutes). Handle 401 responses by:

1. Attempting to refresh the token
2. Redirecting to login if refresh fails

```javascript
// JavaScript example
fetch('/api/exchanges/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(response => {
  if (response.status === 401) {
    // Token expired, redirect to login
    window.location.href = '/login';
  }
  return response.json();
});
```

## User Roles

The system supports two main roles:

### Student Role
- Can create and manage their own exchange applications
- Can upload documents for their applications
- Can view their application status
- Cannot access other students' data

### Manager Role
- Can view all exchange applications
- Can transition applications through workflow states
- Can generate official documents
- Can manage system configuration

## Security Considerations

1. **Store tokens securely**: Never store tokens in plain text
2. **Use HTTPS**: Always use secure connections in production
3. **Token expiration**: Tokens should have reasonable expiration times
4. **Refresh mechanism**: Implement token refresh for better UX
5. **Logout properly**: Clear tokens on logout

## Error Codes

| Code | Description |
|------|-------------|
| `AUTH001` | Invalid credentials |
| `AUTH002` | Token expired |
| `AUTH003` | Invalid token format |
| `AUTH004` | User account disabled |
| `AUTH005` | Insufficient permissions |

## Examples

### Python Example

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login/', json={
    'username': 'student@example.com',
    'password': 'password123'
})
token = response.json()['token']

# Use token in subsequent requests
headers = {'Authorization': f'Bearer {token}'}
exchanges = requests.get('http://localhost:8000/api/exchanges/', headers=headers)
```

### JavaScript Example

```javascript
// Login
async function login(username, password) {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password})
  });
  const data = await response.json();
  localStorage.setItem('jwt_token', data.token);
  return data;
}

// Make authenticated request
async function getExchanges() {
  const token = localStorage.getItem('jwt_token');
  const response = await fetch('/api/exchanges/', {
    headers: {'Authorization': `Bearer ${token}`}
  });
  return response.json();
}
```
