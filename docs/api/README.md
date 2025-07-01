# SEIM API Documentation

This directory contains the comprehensive API documentation for the Student Exchange Information Manager (SEIM) system.

## Table of Contents

1. [Authentication](authentication.md)
2. [Exchanges API](exchanges.md)
3. [Documents API](documents.md)
4. [Forms API](forms.md)
5. [Workflow API](workflow.md)
6. [Error Handling](errors.md)
7. [Examples](examples.md)

## Base URL

```
http://localhost:8000/api/
```

## Authentication

All API endpoints (except login) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All responses follow a consistent format:

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data here
  }
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    }
  }
}
```

### Pagination

List endpoints support pagination:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/exchanges/?page=2",
  "previous": null,
  "results": [
    // Array of results
  ]
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour
- Bulk operations: 10 requests per minute

## Versioning

The API uses URL-based versioning. Current version: v1

```
http://localhost:8000/api/v1/
```

## Quick Start

1. Authenticate to get a JWT token:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
        -H "Content-Type: application/json" \
        -d '{"username": "user@example.com", "password": "password"}'
   ```

2. Use the token in subsequent requests:
   ```bash
   curl -X GET http://localhost:8000/api/exchanges/ \
        -H "Authorization: Bearer <your-token>"
   ```

## API Endpoints

### Exchanges API

#### List Exchanges
- **URL**: `/api/v1/exchanges/`
- **Method**: `GET`
- **Description**: Retrieve a paginated list of exchanges.
- **Request Parameters**:
  - `page` (optional): Page number for pagination.
- **Response**:
  ```json
  {
    "count": 100,
    "next": "http://localhost:8000/api/v1/exchanges/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Exchange Name",
        "status": "active"
      }
    ]
  }
  ```

#### Create Exchange
- **URL**: `/api/v1/exchanges/`
- **Method**: `POST`
- **Description**: Create a new exchange.
- **Request Body**:
  ```json
  {
    "name": "Exchange Name",
    "description": "Description of the exchange"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Exchange Name",
    "description": "Description of the exchange",
    "status": "active"
  }
  ```

#### Retrieve Exchange
- **URL**: `/api/v1/exchanges/{id}/`
- **Method**: `GET`
- **Description**: Retrieve details of a specific exchange.
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Exchange Name",
    "description": "Description of the exchange",
    "status": "active"
  }
  ```

#### Update Exchange
- **URL**: `/api/v1/exchanges/{id}/`
- **Method**: `PUT`
- **Description**: Update details of a specific exchange.
- **Request Body**:
  ```json
  {
    "name": "Updated Exchange Name",
    "description": "Updated description"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Updated Exchange Name",
    "description": "Updated description",
    "status": "active"
  }
  ```

#### Delete Exchange
- **URL**: `/api/v1/exchanges/{id}/`
- **Method**: `DELETE`
- **Description**: Delete a specific exchange.
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Exchange deleted successfully"
  }
  ```

### Documents API

#### List Documents
- **URL**: `/api/v1/documents/`
- **Method**: `GET`
- **Description**: Retrieve a paginated list of documents.
- **Request Parameters**:
  - `page` (optional): Page number for pagination.
- **Response**:
  ```json
  {
    "count": 50,
    "next": "http://localhost:8000/api/v1/documents/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Document Title",
        "status": "verified"
      }
    ]
  }
  ```

#### Upload Document
- **URL**: `/api/v1/documents/`
- **Method**: `POST`
- **Description**: Upload a new document.
- **Request Body**:
  ```json
  {
    "title": "Document Title",
    "file": "<base64-encoded-file>"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "title": "Document Title",
    "status": "pending"
  }
  ```

#### Retrieve Document
- **URL**: `/api/v1/documents/{id}/`
- **Method**: `GET`
- **Description**: Retrieve details of a specific document.
- **Response**:
  ```json
  {
    "id": 1,
    "title": "Document Title",
    "status": "verified"
  }
  ```

#### Update Document
- **URL**: `/api/v1/documents/{id}/`
- **Method**: `PUT`
- **Description**: Update details of a specific document.
- **Request Body**:
  ```json
  {
    "title": "Updated Document Title"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "title": "Updated Document Title",
    "status": "verified"
  }
  ```

#### Delete Document
- **URL**: `/api/v1/documents/{id}/`
- **Method**: `DELETE`
- **Description**: Delete a specific document.
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Document deleted successfully"
  }
  ```

## Support

For API support, please:

1. Check the documentation in this directory
2. Review the [examples](examples.md)
3. Open an issue on GitHub
4. Contact the development team
