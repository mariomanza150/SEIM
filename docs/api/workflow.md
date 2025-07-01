# Workflow API

The Workflow API manages the state transitions of exchange applications through their lifecycle.

## Workflow States

| State | Description | Next States |
|-------|-------------|-------------|
| `draft` | Initial state, application being prepared | submitted, cancelled |
| `submitted` | Application submitted by student | under_review, cancelled |
| `under_review` | Being reviewed by managers | approved, rejected |
| `approved` | Application approved | completed, cancelled |
| `rejected` | Application rejected | draft (resubmit) |
| `completed` | Exchange completed successfully | - |
| `cancelled` | Application cancelled | - |

## State Diagram

```
     ┌─────────┐
     │  draft  │
     └────┬────┘
          │ submit
     ┌────▼────┐
     │submitted│
     └────┬────┘
          │ review
   ┌──────▼──────┐
   │under_review │
   └──────┬──────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼────┐
│approved│   │rejected│
└───┬───┘   └────────┘
    │ complete
┌───▼────┐
│completed│
└─────────┘
```

## Endpoints

### Get Available Transitions

Get the list of possible state transitions for an exchange.

**Endpoint:** `GET /api/exchanges/{id}/available_transitions/`

**Response:**
```json
{
  "current_status": "submitted",
  "available_transitions": [
    {
      "to_status": "under_review",
      "label": "Start Review",
      "requires_comment": false,
      "allowed_for": ["manager"]
    },
    {
      "to_status": "cancelled",
      "label": "Cancel Application",
      "requires_comment": true,
      "allowed_for": ["student", "manager"]
    }
  ]
}
```

### Perform Transition

Change the workflow state of an exchange.

**Endpoint:** `POST /api/exchanges/{id}/transition/`

**Request:**
```json
{
  "status": "approved",
  "comment": "All requirements met, application approved"
}
```

**Response:**
```json
{
  "id": 1,
  "previous_status": "under_review",
  "status": "approved",
  "approved_at": "2025-01-15T14:00:00Z",
  "transitioned_by": "manager@example.com",
  "comment": "All requirements met, application approved",
  "documents_generated": [
    {
      "id": 10,
      "document_type": "acceptance_letter",
      "title": "Acceptance Letter - John Doe"
    }
  ]
}
```

### Get Workflow History

Retrieve the complete workflow history for an exchange.

**Endpoint:** `GET /api/exchanges/{id}/workflow_history/`

**Response:**
```json
{
  "exchange_id": 1,
  "current_status": "approved",
  "history": [
    {
      "id": 1,
      "from_status": null,
      "to_status": "draft",
      "transitioned_at": "2025-01-10T10:00:00Z",
      "transitioned_by": "student@example.com",
      "comment": "Application created",
      "metadata": {}
    },
    {
      "id": 2,
      "from_status": "draft",
      "to_status": "submitted",
      "transitioned_at": "2025-01-12T14:30:00Z",
      "transitioned_by": "student@example.com",
      "comment": "All documents uploaded",
      "metadata": {
        "documents_count": 5
      }
    },
    {
      "id": 3,
      "from_status": "submitted",
      "to_status": "under_review",
      "transitioned_at": "2025-01-13T09:00:00Z",
      "transitioned_by": "manager@example.com",
      "comment": "Starting review process",
      "metadata": {
        "assigned_reviewer": "reviewer@example.com"
      }
    }
  ]
}
```

### Bulk Transition

Perform state transitions on multiple exchanges at once (managers only).

**Endpoint:** `POST /api/exchanges/bulk_transition/`

**Request:**
```json
{
  "exchange_ids": [1, 2, 3, 4, 5],
  "status": "under_review",
  "comment": "Batch review process started"
}
```

**Response:**
```json
{
  "total": 5,
  "successful": 4,
  "failed": 1,
  "results": [
    {
      "exchange_id": 1,
      "success": true,
      "previous_status": "submitted",
      "new_status": "under_review"
    },
    {
      "exchange_id": 2,
      "success": true,
      "previous_status": "submitted",
      "new_status": "under_review"
    },
    {
      "exchange_id": 3,
      "success": false,
      "error": "Invalid transition from draft to under_review",
      "current_status": "draft"
    }
  ]
}
```

## Transition Rules

### Permission Requirements

| Transition | Required Role | Notes |
|------------|--------------|--------|
| draft → submitted | student (owner) | Only the application owner |
| submitted → under_review | manager | Any manager can start review |
| under_review → approved | manager | Requires all documents present |
| under_review → rejected | manager | Must provide rejection reason |
| approved → completed | manager | Mark exchange as finished |
| any → cancelled | owner or manager | Requires cancellation reason |

### Validation Rules

1. **Document Requirements**:
   - Cannot transition to `approved` without required documents
   - Must have passport, transcript, motivation letter, recommendation

2. **Date Constraints**:
   - Cannot mark as `completed` before exchange end date
   - Cannot approve if start date is in the past

3. **Comment Requirements**:
   - Rejection requires comment explaining reason
   - Cancellation requires comment
   - Other transitions optionally accept comments

### Automatic Actions

Certain transitions trigger automatic actions:

| Transition | Automatic Actions |
|------------|-------------------|
| submitted → under_review | Email notification to student |
| under_review → approved | Generate acceptance letter, email student |
| under_review → rejected | Email student with rejection reason |
| approved → completed | Generate completion certificate |

## Workflow Customization

### Custom Validation

```python
# Custom validation example
def validate_approval(exchange):
    # Check required documents
    required_types = ['passport', 'transcript', 'motivation_letter']
    existing_types = exchange.documents.values_list('document_type', flat=True)
    
    missing = set(required_types) - set(existing_types)
    if missing:
        raise ValidationError(f"Missing documents: {', '.join(missing)}")
    
    # Check dates
    if exchange.start_date < timezone.now().date():
        raise ValidationError("Cannot approve past exchanges")
```

### Custom Actions

```python
# Custom action example
def on_approval(exchange):
    # Generate acceptance letter
    document = DocumentGenerator.generate_acceptance_letter(exchange)
    
    # Send email notification
    NotificationService.send_approval_email(exchange, document)
    
    # Update related records
    exchange.user.profile.approved_exchanges_count += 1
    exchange.user.profile.save()
```

## Error Handling

### Invalid Transition

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_TRANSITION",
    "message": "Cannot transition from completed to draft",
    "details": {
      "current_status": "completed",
      "requested_status": "draft",
      "valid_transitions": []
    }
  }
}
```

### Missing Requirements

```json
{
  "status": "error",
  "error": {
    "code": "MISSING_REQUIREMENTS",
    "message": "Cannot approve without required documents",
    "details": {
      "missing_documents": ["passport", "transcript"],
      "required_documents": ["passport", "transcript", "motivation_letter", "recommendation"]
    }
  }
}
```

### Permission Denied

```json
{
  "status": "error",
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Only managers can approve applications",
    "details": {
      "required_role": "manager",
      "current_role": "student",
      "transition": "under_review → approved"
    }
  }
}
```

## Best Practices

### 1. Check Available Transitions

Always check available transitions before attempting a state change:

```javascript
async function transitionExchange(exchangeId, newStatus) {
  // First, check available transitions
  const response = await fetch(`/api/exchanges/${exchangeId}/available_transitions/`);
  const available = await response.json();
  
  const transition = available.available_transitions.find(t => t.to_status === newStatus);
  if (!transition) {
    throw new Error(`Cannot transition to ${newStatus}`);
  }
  
  // Perform the transition
  return await fetch(`/api/exchanges/${exchangeId}/transition/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      status: newStatus,
      comment: transition.requires_comment ? 'Required comment' : ''
    })
  });
}
```

### 2. Handle Transition Errors

```javascript
async function safeTransition(exchangeId, newStatus, comment) {
  try {
    const response = await transitionExchange(exchangeId, newStatus, comment);
    
    if (!response.ok) {
      const error = await response.json();
      
      switch (error.error.code) {
        case 'INVALID_TRANSITION':
          console.error('Invalid state transition:', error.error.message);
          // Show user-friendly message
          break;
          
        case 'MISSING_REQUIREMENTS':
          console.error('Missing requirements:', error.error.details.missing_documents);
          // Prompt user to upload missing documents
          break;
          
        case 'PERMISSION_DENIED':
          console.error('Permission denied:', error.error.message);
          // Redirect to appropriate page
          break;
          
        default:
          console.error('Unknown error:', error.error.message);
      }
    }
    
    return await response.json();
  } catch (error) {
    console.error('Network error:', error);
    throw error;
  }
}
```

### 3. Implement Workflow UI

```javascript
class WorkflowManager {
  constructor(exchangeId) {
    this.exchangeId = exchangeId;
    this.currentStatus = null;
    this.availableTransitions = [];
  }
  
  async load() {
    // Get current exchange status
    const exchangeResponse = await fetch(`/api/exchanges/${this.exchangeId}/`);
    const exchange = await exchangeResponse.json();
    this.currentStatus = exchange.status;
    
    // Get available transitions
    const transitionsResponse = await fetch(`/api/exchanges/${this.exchangeId}/available_transitions/`);
    const transitions = await transitionsResponse.json();
    this.availableTransitions = transitions.available_transitions;
  }
  
  renderTransitionButtons() {
    const container = document.getElementById('workflow-actions');
    container.innerHTML = '';
    
    this.availableTransitions.forEach(transition => {
      const button = document.createElement('button');
      button.textContent = transition.label;
      button.className = `transition-btn transition-to-${transition.to_status}`;
      
      button.addEventListener('click', () => {
        this.performTransition(transition);
      });
      
      container.appendChild(button);
    });
  }
  
  async performTransition(transition) {
    let comment = '';
    
    if (transition.requires_comment) {
      comment = prompt(`Please provide a comment for ${transition.label}:`);
      if (!comment) return; // User cancelled
    }
    
    try {
      const response = await fetch(`/api/exchanges/${this.exchangeId}/transition/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          status: transition.to_status,
          comment: comment
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        // Update UI
        this.currentStatus = result.status;
        await this.load(); // Reload available transitions
        this.renderTransitionButtons();
        
        // Show success message
        this.showMessage(`Successfully transitioned to ${result.status}`);
        
        // Handle generated documents
        if (result.documents_generated && result.documents_generated.length > 0) {
          this.showGeneratedDocuments(result.documents_generated);
        }
      } else {
        const error = await response.json();
        this.showError(error.error.message);
      }
    } catch (error) {
      this.showError('Network error occurred');
    }
  }
  
  showMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
  }
  
  showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
  }
  
  showGeneratedDocuments(documents) {
    const container = document.getElementById('generated-documents');
    documents.forEach(doc => {
      const link = document.createElement('a');
      link.href = `/api/documents/${doc.id}/download/`;
      link.textContent = `Download ${doc.title}`;
      link.className = 'document-link';
      container.appendChild(link);
    });
  }
}

// Initialize workflow manager
const workflowManager = new WorkflowManager(exchangeId);
workflowManager.load().then(() => {
  workflowManager.renderTransitionButtons();
});
```

## Complete Example

### Python Implementation

```python
from exchange.services.workflow import WorkflowService

# Example service usage
class ExchangeWorkflowView(APIView):
    def post(self, request, pk):
        exchange = Exchange.objects.get(pk=pk)
        new_status = request.data.get('status')
        comment = request.data.get('comment', '')
        
        try:
            # Validate transition
            if not WorkflowService.can_transition(exchange, new_status, request.user):
                return Response(
                    {'error': 'Invalid transition'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform transition
            result = WorkflowService.transition(
                exchange=exchange,
                new_status=new_status,
                user=request.user,
                comment=comment
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

### React Implementation

```jsx
// React component for workflow management
import React, { useState, useEffect } from 'react';
import { api } from './api';

function WorkflowManager({ exchangeId }) {
  const [exchange, setExchange] = useState(null);
  const [transitions, setTransitions] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadExchange();
    loadTransitions();
  }, [exchangeId]);
  
  const loadExchange = async () => {
    const response = await api.get(`/exchanges/${exchangeId}/`);
    setExchange(response.data);
  };
  
  const loadTransitions = async () => {
    const response = await api.get(`/exchanges/${exchangeId}/available_transitions/`);
    setTransitions(response.data.available_transitions);
  };
  
  const handleTransition = async (transition) => {
    let comment = '';
    
    if (transition.requires_comment) {
      comment = window.prompt(`Comment for ${transition.label}:`);
      if (!comment) return;
    }
    
    setLoading(true);
    
    try {
      const response = await api.post(`/exchanges/${exchangeId}/transition/`, {
        status: transition.to_status,
        comment: comment
      });
      
      // Reload data
      await loadExchange();
      await loadTransitions();
      
      // Handle generated documents
      if (response.data.documents_generated) {
        // Show download links
      }
      
      alert('Transition successful!');
    } catch (error) {
      alert(`Error: ${error.response.data.error.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  if (!exchange) return <div>Loading...</div>;
  
  return (
    <div className="workflow-manager">
      <h3>Current Status: {exchange.status}</h3>
      
      <div className="transitions">
        {transitions.map(transition => (
          <button
            key={transition.to_status}
            onClick={() => handleTransition(transition)}
            disabled={loading}
          >
            {transition.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default WorkflowManager;
```

## Summary

The Workflow API provides a robust state machine for managing exchange applications through their lifecycle. Key features include:

1. **Clear State Transitions**: Well-defined states and allowed transitions
2. **Permission Control**: Role-based access to transitions
3. **Validation**: Ensure data integrity before state changes
4. **Automatic Actions**: Trigger document generation and notifications
5. **History Tracking**: Complete audit trail of all transitions
6. **Bulk Operations**: Efficient processing of multiple applications
7. **Error Handling**: Clear error messages and recovery options

Always check available transitions, handle errors gracefully, and provide clear feedback to users about the workflow state and available actions.
