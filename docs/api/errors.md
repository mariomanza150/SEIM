# Error Handling

This document describes the error response format and common error codes used throughout the SEIM API.

## Error Response Format

All API errors follow a consistent format:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "details": {
      // Additional context-specific information
    }
  }
}
```

## HTTP Status Codes

| Status Code | Description | Common Usage |
|-------------|-------------|--------------|
| 400 | Bad Request | Invalid input, validation errors |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method |
| 409 | Conflict | State conflict, duplicate resource |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary outage |

## Error Codes

### Authentication Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTH001` | Invalid credentials | 401 |
| `AUTH002` | Token expired | 401 |
| `AUTH003` | Invalid token format | 401 |
| `AUTH004` | Account disabled | 403 |
| `AUTH005` | Insufficient permissions | 403 |
| `AUTH006` | Two-factor authentication required | 401 |

**Example:**
```json
{
  "status": "error",
  "error": {
    "code": "AUTH002",
    "message": "Authentication token has expired",
    "details": {
      "expired_at": "2025-01-15T12:00:00Z",
      "token_type": "access"
    }
  }
}
```

### Validation Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VAL001` | Required field missing | 400 |
| `VAL002` | Invalid field format | 400 |
| `VAL003` | Field value out of range | 400 |
| `VAL004` | Invalid date format | 400 |
| `VAL005` | Date out of allowed range | 400 |
| `VAL006` | Invalid email format | 400 |
| `VAL007` | Duplicate value | 409 |

**Example:**
```json
{
  "status": "error",
  "error": {
    "code": "VAL001",
    "message": "Validation failed",
    "details": {
      "first_name": ["This field is required"],
      "email": ["Enter a valid email address"],
      "start_date": ["Start date must be in the future"]
    }
  }
}
```

### Resource Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `RES001` | Resource not found | 404 |
| `RES002` | Resource already exists | 409 |
| `RES003` | Resource locked | 423 |
| `RES004` | Resource deleted | 410 |
| `RES005` | Parent resource not found | 404 |

**Example:**
```json
{
  "status": "error",
  "error": {
    "code": "RES001",
    "message": "Exchange application not found",
    "details": {
      "resource_type": "exchange",
      "resource_id": 123
    }
  }
}
```

### Workflow Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `WF001` | Invalid state transition | 400 |
| `WF002` | Missing transition requirements | 400 |
| `WF003` | Transition not allowed for user | 403 |
| `WF004` | Workflow locked | 423 |
| `WF005` | Invalid workflow state | 400 |

**Example:**
```json
{
  "status": "error",
  "error": {
    "code": "WF001",
    "message": "Cannot transition from approved to draft",
    "details": {
      "current_status": "approved",
      "requested_status": "draft",
      "allowed_transitions": ["completed", "cancelled"]
    }
  }
}
```

### File Upload Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `FILE001` | File too large | 413 |
| `FILE002` | Invalid file type | 400 |
| `FILE003` | File corrupted | 400 |
| `FILE004` | Virus detected | 400 |
| `FILE005` | Storage quota exceeded | 507 |
| `FILE006` | Hash mismatch | 409 |

**Example:**
```json
{
  "status": "error",
  "error": {
    "code": "FILE001",
    "message": "File size exceeds maximum allowed",
    "details": {
      "file_size": 15728640,
      "max_size": 10485760,
      "max_size_mb": 10
    }
  }
}
```

### Business Logic Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `BUS001` | Operation not allowed | 403 |
| `BUS002` | Prerequisite not met | 400 |
| `BUS003` | Limit exceeded | 429 |
| `BUS004` | Deadline passed | 400 |
| `BUS005` | Invalid operation | 400 |

**Example:**
```json
{
  "status": "error",
  "error": {
    "code": "BUS004",
    "message": "Application deadline has passed",
    "details": {
      "deadline": "2025-01-01T00:00:00Z",
      "current_time": "2025-01-15T10:00:00Z"
    }
  }
}
```

### System Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `SYS001` | Database error | 500 |
| `SYS002` | External service error | 502 |
| `SYS003` | Configuration error | 500 |
| `SYS004` | Rate limit exceeded | 429 |
| `SYS005` | Service temporarily unavailable | 503 |

**Example:**
```json
{
  "status": "error",
  "error": {
    "code": "SYS004",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "1 hour",
      "retry_after": "2025-01-15T13:00:00Z"
    }
  }
}
```

## Error Handling Best Practices

### 1. Client-Side Error Handling

```javascript
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      
      // Handle specific error codes
      switch (error.error.code) {
        case 'AUTH002':
          // Token expired - refresh or redirect to login
          await refreshToken();
          return apiCall(url, options); // Retry
          
        case 'VAL001':
          // Validation error - show field errors
          showValidationErrors(error.error.details);
          break;
          
        case 'SYS004':
          // Rate limited - wait and retry
          const retryAfter = new Date(error.error.details.retry_after);
          await waitUntil(retryAfter);
          return apiCall(url, options);
          
        default:
          // Generic error handling
          showErrorMessage(error.error.message);
      }
      
      throw error;
    }
    
    return await response.json();
  } catch (error) {
    // Network error
    showErrorMessage('Network error. Please check your connection.');
    throw error;
  }
}
```

### 2. Error Display

```javascript
function showValidationErrors(errors) {
  // Clear previous errors
  document.querySelectorAll('.error-message').forEach(el => el.remove());
  
  // Display field-specific errors
  Object.entries(errors).forEach(([field, messages]) => {
    const fieldElement = document.querySelector(`[name="${field}"]`);
    if (fieldElement) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'error-message';
      errorDiv.textContent = messages.join(', ');
      fieldElement.parentNode.appendChild(errorDiv);
    }
  });
}

function showErrorMessage(message) {
  const toast = document.createElement('div');
  toast.className = 'error-toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => toast.remove(), 5000);
}
```

### 3. Retry Logic

```javascript
class APIClient {
  constructor(baseURL, maxRetries = 3) {
    this.baseURL = baseURL;
    this.maxRetries = maxRetries;
  }
  
  async request(endpoint, options = {}, retries = 0) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Authorization': `Bearer ${this.getToken()}`,
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
      
      if (!response.ok) {
        const error = await response.json();
        
        // Retry on specific errors
        if (retries < this.maxRetries && this.shouldRetry(error)) {
          const delay = this.getRetryDelay(retries);
          await this.wait(delay);
          return this.request(endpoint, options, retries + 1);
        }
        
        throw error;
      }
      
      return await response.json();
    } catch (error) {
      if (retries < this.maxRetries && this.isNetworkError(error)) {
        const delay = this.getRetryDelay(retries);
        await this.wait(delay);
        return this.request(endpoint, options, retries + 1);
      }
      
      throw error;
    }
  }
  
  shouldRetry(error) {
    const retryableCodes = ['SYS002', 'SYS005'];
    const retryableStatus = [502, 503, 504];
    
    return retryableCodes.includes(error.error?.code) ||
           retryableStatus.includes(error.status);
  }
  
  isNetworkError(error) {
    return error instanceof TypeError && error.message === 'Failed to fetch';
  }
  
  getRetryDelay(retryCount) {
    // Exponential backoff: 1s, 2s, 4s
    return Math.pow(2, retryCount) * 1000;
  }
  
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### 4. Error Logging

```javascript
class ErrorLogger {
  static log(error, context = {}) {
    const errorData = {
      timestamp: new Date().toISOString(),
      error: {
        code: error.error?.code,
        message: error.error?.message,
        details: error.error?.details
      },
      context: {
        url: window.location.href,
        userAgent: navigator.userAgent,
        ...context
      }
    };
    
    // Send to logging service
    if (window.errorReportingService) {
      window.errorReportingService.captureException(error, errorData);
    }
    
    // Console log in development
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', errorData);
    }
  }
}

// Usage
try {
  const result = await apiClient.request('/exchanges/');
} catch (error) {
  ErrorLogger.log(error, {
    action: 'fetch_exchanges',
    userId: currentUser.id
  });
}
```

### 5. User-Friendly Messages

```javascript
const errorMessages = {
  'AUTH001': 'Invalid username or password. Please try again.',
  'AUTH002': 'Your session has expired. Please log in again.',
  'AUTH004': 'Your account has been disabled. Please contact support.',
  'FILE001': 'The file is too large. Please choose a file under 10MB.',
  'FILE002': 'Invalid file type. Please upload a PDF, JPG, or PNG file.',
  'WF001': 'This action is not available in the current state.',
  'SYS004': 'Too many requests. Please wait a moment and try again.',
  'SYS005': 'Service temporarily unavailable. Please try again later.'
};

function getUserFriendlyMessage(errorCode) {
  return errorMessages[errorCode] || 'An unexpected error occurred. Please try again.';
}
```

### 6. Error Recovery

```javascript
class ErrorRecovery {
  static async handleAuthError(error) {
    switch (error.error.code) {
      case 'AUTH002':
        // Token expired
        const refreshed = await this.refreshToken();
        if (refreshed) {
          return { retry: true };
        }
        return { redirect: '/login' };
        
      case 'AUTH004':
        // Account disabled
        return { redirect: '/account-disabled' };
        
      case 'AUTH005':
        // Insufficient permissions
        return { redirect: '/access-denied' };
    }
  }
  
  static async refreshToken() {
    try {
      const response = await fetch('/api/auth/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          refresh: localStorage.getItem('refresh_token')
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }
    
    return false;
  }
  
  static handleValidationError(error) {
    const errors = error.error.details;
    const formErrors = {};
    
    // Transform API errors to form-friendly format
    Object.entries(errors).forEach(([field, messages]) => {
      formErrors[field] = Array.isArray(messages) ? messages[0] : messages;
    });
    
    return { formErrors };
  }
  
  static handleFileError(error) {
    switch (error.error.code) {
      case 'FILE001':
        return {
          message: `File is too large. Maximum size is ${error.error.details.max_size_mb}MB`,
          action: 'resize'
        };
        
      case 'FILE002':
        return {
          message: 'Invalid file type. Please upload a PDF, JPG, or PNG file.',
          action: 'convert'
        };
        
      case 'FILE005':
        return {
          message: 'Storage quota exceeded. Please delete some files.',
          action: 'cleanup'
        };
    }
  }
}
```

## Server-Side Error Handling

### Django Example

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'status': 'error',
            'error': {
                'code': getattr(exc, 'code', 'UNKNOWN'),
                'message': str(exc),
                'details': response.data
            }
        }
        response.data = custom_response_data
    
    return response

class SEIMException(Exception):
    def __init__(self, code, message, details=None, status_code=400):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)

# Usage
def validate_exchange(exchange):
    if exchange.start_date < timezone.now().date():
        raise SEIMException(
            code='VAL005',
            message='Start date cannot be in the past',
            details={'start_date': exchange.start_date},
            status_code=400
        )
```

### Middleware Example

```python
class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            response = self.handle_exception(e)
        
        return response
    
    def handle_exception(self, exc):
        if isinstance(exc, SEIMException):
            data = {
                'status': 'error',
                'error': {
                    'code': exc.code,
                    'message': exc.message,
                    'details': exc.details
                }
            }
            return JsonResponse(data, status=exc.status_code)
        
        # Log unexpected errors
        logger.exception('Unexpected error')
        
        data = {
            'status': 'error',
            'error': {
                'code': 'SYS001',
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }
        return JsonResponse(data, status=500)
```

## Error Codes Quick Reference

```javascript
const ERROR_CODES = {
  // Authentication
  AUTH001: 'Invalid credentials',
  AUTH002: 'Token expired',
  AUTH003: 'Invalid token format',
  AUTH004: 'Account disabled',
  AUTH005: 'Insufficient permissions',
  
  // Validation
  VAL001: 'Required field missing',
  VAL002: 'Invalid field format',
  VAL003: 'Field value out of range',
  VAL004: 'Invalid date format',
  VAL005: 'Date out of allowed range',
  VAL006: 'Invalid email format',
  VAL007: 'Duplicate value',
  
  // Resources
  RES001: 'Resource not found',
  RES002: 'Resource already exists',
  RES003: 'Resource locked',
  RES004: 'Resource deleted',
  RES005: 'Parent resource not found',
  
  // Workflow
  WF001: 'Invalid state transition',
  WF002: 'Missing transition requirements',
  WF003: 'Transition not allowed for user',
  WF004: 'Workflow locked',
  WF005: 'Invalid workflow state',
  
  // Files
  FILE001: 'File too large',
  FILE002: 'Invalid file type',
  FILE003: 'File corrupted',
  FILE004: 'Virus detected',
  FILE005: 'Storage quota exceeded',
  FILE006: 'Hash mismatch',
  
  // Business Logic
  BUS001: 'Operation not allowed',
  BUS002: 'Prerequisite not met',
  BUS003: 'Limit exceeded',
  BUS004: 'Deadline passed',
  BUS005: 'Invalid operation',
  
  // System
  SYS001: 'Database error',
  SYS002: 'External service error',
  SYS003: 'Configuration error',
  SYS004: 'Rate limit exceeded',
  SYS005: 'Service temporarily unavailable'
};
```

## Summary

Consistent error handling is crucial for a good API experience. Key principles:

1. **Consistency**: Use the same error format across all endpoints
2. **Clarity**: Provide clear, actionable error messages
3. **Context**: Include relevant details to help debugging
4. **Recovery**: Suggest how to fix or work around the error
5. **Logging**: Track errors for monitoring and improvement
6. **Security**: Don't expose sensitive information in errors

By following these patterns, you can create a robust error handling system that helps developers quickly identify and resolve issues.
