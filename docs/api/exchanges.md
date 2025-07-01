# Exchanges API

The Exchanges API manages student exchange applications throughout their lifecycle.

## Exchange Model

```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "university": "Home University",
  "destination_university": "Partner University",
  "exchange_type": "semester",
  "start_date": "2025-09-01",
  "end_date": "2026-01-31",
  "status": "submitted",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z",
  "submitted_at": "2025-01-15T14:30:00Z",
  "approved_at": null,
  "completed_at": null,
  "user": 1,
  "documents_count": 3,
  "workflow_logs_count": 2
}
```

## Endpoints

### List Exchanges

Get a paginated list of exchange applications.

**Endpoint:** `GET /api/exchanges/`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `status`: Filter by status
- `user`: Filter by user ID (managers only)
- `start_date_after`: Filter by start date
- `start_date_before`: Filter by start date
- `search`: Search in names and universities

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/exchanges/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      // ... full exchange object
    }
  ]
}
```

**Permissions:**
- Students can only see their own exchanges
- Managers can see all exchanges

### Create Exchange

Create a new exchange application.

**Endpoint:** `POST /api/exchanges/`

**Request:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1234567890",
  "university": "Home University",
  "destination_university": "Partner University",
  "exchange_type": "semester",
  "start_date": "2025-09-01",
  "end_date": "2026-01-31"
}
```

**Response:**
```json
{
  "id": 2,
  "status": "draft",
  "created_at": "2025-01-15T15:00:00Z",
  // ... full exchange object
}
```

**Validation:**
- All fields are required
- `exchange_type` must be one of: `semester`, `year`, `summer`
- `end_date` must be after `start_date`
- Email must be unique per user

### Retrieve Exchange

Get details of a specific exchange.

**Endpoint:** `GET /api/exchanges/{id}/`

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  // ... full exchange object
  "documents": [
    {
      "id": 1,
      "document_type": "passport",
      "title": "Passport Scan",
      "uploaded_at": "2025-01-15T11:00:00Z"
    }
  ],
  "workflow_logs": [
    {
      "id": 1,
      "from_status": "draft",
      "to_status": "submitted",
      "transitioned_at": "2025-01-15T14:30:00Z",
      "comment": "Application ready for review"
    }
  ]
}
```

### Update Exchange

Update an existing exchange application.

**Endpoint:** `PUT /api/exchanges/{id}/`

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "university": "Updated University",
  "destination_university": "Partner University",
  "exchange_type": "year",
  "start_date": "2025-09-01",
  "end_date": "2026-06-30"
}
```

**Restrictions:**
- Cannot update once status is beyond "submitted"
- Cannot change user association

### Delete Exchange

Delete an exchange application.

**Endpoint:** `DELETE /api/exchanges/{id}/`

**Response:** `204 No Content`

**Restrictions:**
- Can only delete if status is "draft"
- Managers can delete any draft exchange
- Students can only delete their own

## Workflow Operations

### Available Transitions

Get available workflow transitions for an exchange.

**Endpoint:** `GET /api/exchanges/{id}/available_transitions/`

**Response:**
```json
{
  "available_transitions": [
    {
      "to_status": "submitted",
      "label": "Submit for Review",
      "requires_comment": false
    },
    {
      "to_status": "cancelled",
      "label": "Cancel Application",
      "requires_comment": true
    }
  ]
}
```

### Perform Transition

Change the status of an exchange.

**Endpoint:** `POST /api/exchanges/{id}/transition/`

**Request:**
```json
{
  "status": "submitted",
  "comment": "All documents uploaded, ready for review"
}
```

**Response:**
```json
{
  "id": 1,
  "status": "submitted",
  "submitted_at": "2025-01-15T16:00:00Z",
  // ... updated exchange object
}
```

**Workflow Rules:**
- `draft` → `submitted`: Student only
- `submitted` → `under_review`: Manager only
- `under_review` → `approved`/`rejected`: Manager only
- `approved` → `completed`: Manager only
- Any status → `cancelled`: Owner or Manager

### Workflow History

Get the complete workflow history for an exchange.

**Endpoint:** `GET /api/exchanges/{id}/workflow_history/`

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "from_status": null,
      "to_status": "draft",
      "transitioned_at": "2025-01-15T10:00:00Z",
      "transitioned_by": "john.doe@example.com",
      "comment": "Application created"
    },
    {
      "id": 2,
      "from_status": "draft",
      "to_status": "submitted",
      "transitioned_at": "2025-01-15T14:30:00Z",
      "transitioned_by": "john.doe@example.com",
      "comment": "Ready for review"
    }
  ]
}
```

## Bulk Operations

### Bulk Status Update

Update status for multiple exchanges (managers only).

**Endpoint:** `POST /api/exchanges/bulk_transition/`

**Request:**
```json
{
  "exchange_ids": [1, 2, 3],
  "status": "under_review",
  "comment": "Batch processing for review"
}
```

**Response:**
```json
{
  "updated": [1, 2],
  "failed": [
    {
      "id": 3,
      "error": "Invalid transition from completed to under_review"
    }
  ]
}
```

## Form Progress

### Check Form Completion

Get the form completion status for an exchange.

**Endpoint:** `GET /api/exchanges/{id}/form_progress/`

**Response:**
```json
{
  "total_steps": 4,
  "completed_steps": 3,
  "completion_percentage": 75,
  "steps": [
    {
      "step_number": 1,
      "name": "Personal Information",
      "completed": true
    },
    {
      "step_number": 2,
      "name": "Academic Information",
      "completed": true
    },
    {
      "step_number": 3,
      "name": "Documents",
      "completed": true
    },
    {
      "step_number": 4,
      "name": "Additional Information",
      "completed": false
    }
  ]
}
```

## Error Responses

### Validation Errors

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "end_date": ["End date must be after start date"],
      "email": ["This email is already in use"]
    }
  }
}
```

### Permission Errors

```json
{
  "status": "error",
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You don't have permission to perform this action",
    "details": {
      "required_role": "manager",
      "current_role": "student"
    }
  }
}
```

### Workflow Errors

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_TRANSITION",
    "message": "Cannot transition from approved to draft",
    "details": {
      "current_status": "approved",
      "requested_status": "draft",
      "allowed_transitions": ["completed", "cancelled"]
    }
  }
}
```

## Examples

### Complete Exchange Application Flow

```python
import requests

# 1. Create exchange
response = requests.post(
    'http://localhost:8000/api/exchanges/',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': 'jane@example.com',
        'university': 'Home University',
        'destination_university': 'Partner University',
        'exchange_type': 'semester',
        'start_date': '2025-09-01',
        'end_date': '2026-01-31'
    }
)
exchange_id = response.json()['id']

# 2. Upload documents
with open('passport.pdf', 'rb') as f:
    requests.post(
        'http://localhost:8000/api/documents/',
        headers={'Authorization': f'Bearer {token}'},
        files={'file': f},
        data={
            'exchange': exchange_id,
            'document_type': 'passport',
            'title': 'Passport Scan'
        }
    )

# 3. Submit for review
requests.post(
    f'http://localhost:8000/api/exchanges/{exchange_id}/transition/',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'status': 'submitted',
        'comment': 'All documents uploaded'
    }
)
```

### JavaScript Example with Error Handling

```javascript
async function createExchange(data) {
  try {
    const response = await fetch('/api/exchanges/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('Validation errors:', error.error.details);
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error('Network error:', error);
    return null;
  }
}
```
