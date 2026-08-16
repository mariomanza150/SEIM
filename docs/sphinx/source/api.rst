API Module
=========

The API module provides RESTful API endpoints for SEIM functionality.

Overview
--------

The API module provides:

* RESTful API endpoints for all major functionality
* JWT authentication and authorization
* OpenAPI/Swagger documentation
* Pagination and filtering
* Rate limiting and throttling
* Comprehensive error handling

Authentication
-------------

SEIM uses JWT (JSON Web Token) authentication:

**Getting a Token:**

.. code-block:: bash

    curl -X POST http://localhost:8000/api/token/ \
      -H "Content-Type: application/json" \
      -d '{"username": "your_username", "password": "your_password"}'

**Response:**

.. code-block:: json

    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }

**Using the Token:**

.. code-block:: bash

    curl -X GET http://localhost:8000/api/programs/ \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

**Refreshing the Token:**

.. code-block:: bash

    curl -X POST http://localhost:8000/api/token/refresh/ \
      -H "Content-Type: application/json" \
      -d '{"refresh": "YOUR_REFRESH_TOKEN"}'

Views
-----

.. automodule:: api.views
   :members:
   :undoc-members:
   :show-inheritance:

API Endpoints
------------

**Authentication Endpoints:**

* `POST /api/token/` - Get JWT access and refresh tokens
* `POST /api/token/refresh/` - Refresh JWT access token
* `POST /api/accounts/register/` - Register new user
* `POST /api/accounts/verify-email/` - Verify email address
* `POST /api/accounts/password-reset/` - Request password reset

**User Management Endpoints:**

* `GET /api/accounts/users/` - List users (admin only)
* `GET /api/accounts/users/{id}/` - Get user details
* `PUT /api/accounts/users/{id}/` - Update user
* `DELETE /api/accounts/users/{id}/` - Delete user (admin only)

**Program Endpoints:**

* `GET /api/programs/` - List exchange programs
* `POST /api/programs/` - Create new program (admin only)
* `GET /api/programs/{id}/` - Get program details
* `PUT /api/programs/{id}/` - Update program (admin only)
* `DELETE /api/programs/{id}/` - Delete program (admin only)

**Application Endpoints:**

* `GET /api/applications/` - List applications
* `POST /api/applications/` - Create new application
* `GET /api/applications/{id}/` - Get application details
* `PUT /api/applications/{id}/` - Update application
* `DELETE /api/applications/{id}/` - Delete application
* `POST /api/applications/{id}/submit/` - Submit application
* `POST /api/applications/{id}/withdraw/` - Withdraw application

**Document Endpoints:**

* `GET /api/documents/` - List documents
* `POST /api/documents/` - Upload document
* `GET /api/documents/{id}/` - Get document details
* `PUT /api/documents/{id}/` - Update document
* `DELETE /api/documents/{id}/` - Delete document
* `POST /api/documents/{id}/validate/` - Validate document

**Notification Endpoints:**

* `GET /api/notifications/` - List notifications
* `GET /api/notifications/{id}/` - Get notification details
* `PUT /api/notifications/{id}/mark-read/` - Mark as read
* `DELETE /api/notifications/{id}/` - Delete notification

**Analytics Endpoints:**

* `GET /api/analytics/dashboard/` - Get dashboard metrics
* `GET /api/analytics/programs/{id}/` - Get program analytics
* `GET /api/analytics/reports/` - Generate reports

Example API Usage
----------------

**Python Requests Example:**

.. code-block:: python

    import requests
    
    # Base URL
    base_url = 'http://localhost:8000/api'
    
    # Login and get token
    login_data = {
        'username': 'student@university.edu',
        'password': 'password123'
    }
    
    response = requests.post(f'{base_url}/token/', json=login_data)
    tokens = response.json()
    access_token = tokens['access']
    
    # Set headers for authenticated requests
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get available programs
    response = requests.get(f'{base_url}/programs/', headers=headers)
    programs = response.json()
    
    # Create application
    application_data = {
        'program': programs['results'][0]['id'],
        'status': 'draft'
    }
    
    response = requests.post(f'{base_url}/applications/', 
                           json=application_data, headers=headers)
    application = response.json()

**JavaScript Fetch Example:**

.. code-block:: javascript

    // Login and get token
    async function login(username, password) {
        const response = await fetch('/api/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const tokens = await response.json();
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        
        return tokens;
    }
    
    // Get programs
    async function getPrograms() {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/programs/', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        return await response.json();
    }
    
    // Upload document
    async function uploadDocument(file, applicationId) {
        const token = localStorage.getItem('access_token');
        const formData = new FormData();
        formData.append('file', file);
        formData.append('application', applicationId);
        formData.append('document_type', 'transcript');
        
        const response = await fetch('/api/documents/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        return await response.json();
    }

Serializers
-----------

.. automodule:: api.serializers
   :members:
   :undoc-members:
   :show-inheritance:

URLs
----

.. automodule:: api.urls
   :members:
   :undoc-members:
   :show-inheritance:

Pagination
----------

SEIM uses Django REST Framework's pagination:

**Default Pagination:**

.. code-block:: json

    {
        "count": 100,
        "next": "http://localhost:8000/api/programs/?page=2",
        "previous": null,
        "results": [
            {
                "id": "uuid",
                "name": "Program Name",
                "description": "Program Description"
            }
        ]
    }

**Custom Pagination:**

.. code-block:: python

    # settings.py
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
    }

Filtering
---------

SEIM supports filtering on API endpoints:

**Query Parameters:**

* `search` - Search by name or description
* `status` - Filter by status
* `program` - Filter by program ID
* `student` - Filter by student ID
* `created_at` - Filter by creation date
* `updated_at` - Filter by update date

**Example:**

.. code-block:: bash

    # Search programs
    GET /api/programs/?search=erasmus
    
    # Filter applications by status
    GET /api/applications/?status=submitted
    
    # Filter by date range
    GET /api/applications/?created_at__gte=2024-01-01&created_at__lte=2024-12-31

Error Handling
-------------

SEIM provides comprehensive error handling:

**Error Response Format:**

.. code-block:: json

    {
        "error": "Error message",
        "code": "ERROR_CODE",
        "details": {
            "field": "Field-specific error"
        }
    }

**Common Error Codes:**

* `AUTHENTICATION_FAILED` - Invalid credentials
* `PERMISSION_DENIED` - Insufficient permissions
* `VALIDATION_ERROR` - Invalid data
* `NOT_FOUND` - Resource not found
* `RATE_LIMIT_EXCEEDED` - Too many requests

**Example Error Handling:**

.. code-block:: python

    import requests
    
    try:
        response = requests.get('/api/programs/', headers=headers)
        response.raise_for_status()
        programs = response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Authentication failed")
        elif e.response.status_code == 403:
            print("Permission denied")
        elif e.response.status_code == 404:
            print("Resource not found")
        else:
            print(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

Rate Limiting
-------------

SEIM implements rate limiting to prevent abuse:

**Default Limits:**

* **Anonymous**: 100 requests per hour
* **Authenticated**: 1000 requests per hour
* **Admin**: 5000 requests per hour

**Rate Limit Headers:**

.. code-block:: http

    X-RateLimit-Limit: 1000
    X-RateLimit-Remaining: 999
    X-RateLimit-Reset: 1640995200

**Custom Rate Limits:**

.. code-block:: python

    from rest_framework.throttling import UserRateThrottle
    
    class CustomUserRateThrottle(UserRateThrottle):
        rate = '100/hour'
    
    class MyViewSet(viewsets.ModelViewSet):
        throttle_classes = [CustomUserRateThrottle]

OpenAPI Documentation
--------------------

SEIM provides automatic OpenAPI documentation:

**Access Documentation:**

* **Swagger UI**: http://localhost:8000/api/docs/
* **ReDoc**: http://localhost:8000/api/redoc/
* **OpenAPI Schema**: http://localhost:8000/api/schema/

**Schema Configuration:**

.. code-block:: python

    # settings.py
    SPECTACULAR_SETTINGS = {
        'TITLE': 'SEIM API',
        'DESCRIPTION': 'Student Exchange Information Manager API',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': False,
        'COMPONENT_SPLIT_REQUEST': True,
        'SCHEMA_PATH_PREFIX': '/api/',
    }

Testing
-------

SEIM includes comprehensive API testing:

**Test Configuration:**

.. code-block:: python

    # tests/test_api.py
    from rest_framework.test import APITestCase
    from rest_framework import status
    
    class ProgramAPITestCase(APITestCase):
        def setUp(self):
            self.user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            self.client.force_authenticate(user=self.user)
        
        def test_list_programs(self):
            response = self.client.get('/api/programs/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        def test_create_program(self):
            data = {
                'name': 'Test Program',
                'description': 'Test Description',
                'start_date': '2024-09-01',
                'end_date': '2024-12-31'
            }
            response = self.client.post('/api/programs/', data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

Business Rules
-------------

* All API endpoints require authentication except registration and login
* JWT tokens expire after 5 minutes (access) and 1 day (refresh)
* Rate limiting is enforced to prevent abuse
* All responses are paginated for large datasets
* Error responses follow consistent format
* API documentation is automatically generated
* All endpoints support filtering and searching
* File uploads are limited to 10MB per file
* Sensitive operations require admin permissions

Related Documentation
--------------------

* :doc:`authentication` - Authentication and authorization
* :doc:`business_rules` - Business logic and validation rules
* :doc:`architecture` - System architecture overview
* :doc:`testing` - API testing strategies
* :doc:`deployment` - Production API configuration 