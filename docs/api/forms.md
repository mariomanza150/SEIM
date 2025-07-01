# Forms API

The Forms API provides a dynamic, multi-step form system for collecting exchange application data.

## Form Step Model

```json
{
  "id": 1,
  "step_number": 1,
  "name": "Personal Information",
  "description": "Basic personal details",
  "fields": [
    {
      "name": "first_name",
      "type": "text",
      "label": "First Name",
      "required": true,
      "placeholder": "Enter your first name",
      "validation": {
        "min_length": 2,
        "max_length": 50
      }
    },
    {
      "name": "date_of_birth",
      "type": "date",
      "label": "Date of Birth",
      "required": true,
      "validation": {
        "min_date": "1950-01-01",
        "max_date": "2010-12-31"
      }
    }
  ],
  "is_active": true,
  "created_at": "2025-01-15T09:00:00Z"
}
```

## Field Types

| Type | Description | Validation Options |
|------|-------------|-------------------|
| `text` | Single line text input | min_length, max_length, pattern |
| `email` | Email address | automatic email validation |
| `date` | Date picker | min_date, max_date |
| `file` | File upload | file_types, max_size |
| `choice` | Dropdown selection | choices array |
| `textarea` | Multi-line text | min_length, max_length |
| `boolean` | Checkbox | none |
| `number` | Numeric input | min, max, step |

## Endpoints

### List Form Steps

Get all active form steps.

**Endpoint:** `GET /api/form-steps/`

**Query Parameters:**
- `is_active`: Filter by active status
- `ordering`: Order by step_number (default)

**Response:**
```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "step_number": 1,
      "name": "Personal Information",
      // ... full step object
    }
  ]
}
```

### Get Form Step

Get details of a specific form step.

**Endpoint:** `GET /api/form-steps/{id}/`

**Response:**
```json
{
  "id": 1,
  "step_number": 1,
  "name": "Personal Information",
  "fields": [
    {
      "name": "first_name",
      "type": "text",
      "label": "First Name",
      // ... full field configuration
    }
  ]
}
```

### Submit Form Data

Submit data for a form step.

**Endpoint:** `POST /api/form-submissions/`

**Request:**
```json
{
  "exchange": 1,
  "form_step": 1,
  "data": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1995-06-15",
    "nationality": "US"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "exchange": 1,
  "form_step": 1,
  "data": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1995-06-15",
    "nationality": "US"
  },
  "is_complete": true,
  "validation_errors": null,
  "submitted_at": "2025-01-15T10:30:00Z"
}
```

### Update Form Submission

Update previously submitted form data.

**Endpoint:** `PUT /api/form-submissions/{id}/`

**Request:**
```json
{
  "data": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1995-06-15",
    "nationality": "CA"
  }
}
```

### Get Form Progress

Check overall form completion status.

**Endpoint:** `GET /api/exchanges/{id}/form_progress/`

**Response:**
```json
{
  "total_steps": 4,
  "completed_steps": 3,
  "completion_percentage": 75,
  "next_step": 4,
  "steps": [
    {
      "step_number": 1,
      "name": "Personal Information",
      "completed": true,
      "submission_id": 1
    },
    {
      "step_number": 2,
      "name": "Academic Information",
      "completed": true,
      "submission_id": 2
    },
    {
      "step_number": 3,
      "name": "Documents",
      "completed": true,
      "submission_id": 3
    },
    {
      "step_number": 4,
      "name": "Additional Information",
      "completed": false,
      "submission_id": null
    }
  ]
}
```

### Validate Form Data

Validate form data without saving.

**Endpoint:** `POST /api/form-steps/{id}/validate/`

**Request:**
```json
{
  "data": {
    "first_name": "J",
    "last_name": "",
    "email": "invalid-email"
  }
}
```

**Response:**
```json
{
  "is_valid": false,
  "errors": {
    "first_name": ["Minimum length is 2 characters"],
    "last_name": ["This field is required"],
    "email": ["Enter a valid email address"]
  }
}
```

## Form Configuration

### Field Configuration Structure

```json
{
  "name": "field_name",
  "type": "text",
  "label": "Field Label",
  "required": true,
  "placeholder": "Enter value",
  "help_text": "Additional help for this field",
  "default_value": "",
  "validation": {
    "min_length": 2,
    "max_length": 100,
    "pattern": "^[A-Za-z]+$",
    "pattern_message": "Only letters allowed"
  },
  "conditional": {
    "show_if": {
      "field": "other_field",
      "value": "specific_value"
    }
  }
}
```

### Choice Field Configuration

```json
{
  "name": "country",
  "type": "choice",
  "label": "Country",
  "required": true,
  "choices": [
    {"value": "US", "label": "United States"},
    {"value": "CA", "label": "Canada"},
    {"value": "MX", "label": "Mexico"}
  ],
  "default_value": "US"
}
```

### File Field Configuration

```json
{
  "name": "resume",
  "type": "file",
  "label": "Resume/CV",
  "required": true,
  "validation": {
    "file_types": ["pdf", "doc", "docx"],
    "max_size": 5242880,
    "max_size_label": "5MB"
  }
}
```

## Form Submission Flow

### 1. Get Form Configuration

```javascript
// Get all form steps
const response = await fetch('/api/form-steps/', {
  headers: {'Authorization': `Bearer ${token}`}
});
const steps = await response.json();
```

### 2. Render Dynamic Form

```javascript
// Render form fields dynamically
function renderField(field) {
  switch(field.type) {
    case 'text':
      return `<input type="text" name="${field.name}" required="${field.required}">`;
    case 'choice':
      return `<select name="${field.name}">
        ${field.choices.map(c => `<option value="${c.value}">${c.label}</option>`)}
        </select>`;
    case 'date':
      return `<input type="date" name="${field.name}" required="${field.required}">`;
    // ... other field types
  }
}
```

### 3. Submit Form Data

```javascript
async function submitFormStep(exchangeId, stepId, formData) {
  const response = await fetch('/api/form-submissions/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      exchange: exchangeId,
      form_step: stepId,
      data: formData
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    // Handle validation errors
    displayErrors(error.errors);
    return null;
  }
  
  return await response.json();
}
```

### 4. Navigate Steps

```javascript
class FormWizard {
  constructor(exchangeId) {
    this.exchangeId = exchangeId;
    this.currentStep = 1;
    this.steps = [];
  }
  
  async loadSteps() {
    const response = await fetch('/api/form-steps/');
    this.steps = await response.json();
  }
  
  async loadProgress() {
    const response = await fetch(`/api/exchanges/${this.exchangeId}/form_progress/`);
    const progress = await response.json();
    this.currentStep = progress.next_step;
    return progress;
  }
  
  async submitCurrentStep(data) {
    const step = this.steps.find(s => s.step_number === this.currentStep);
    const submission = await submitFormStep(this.exchangeId, step.id, data);
    
    if (submission) {
      this.currentStep++;
      return true;
    }
    return false;
  }
  
  canGoBack() {
    return this.currentStep > 1;
  }
  
  canGoForward() {
    return this.currentStep < this.steps.length;
  }
}
```

## Validation Rules

### Built-in Validators

```javascript
// Text field validation
{
  "validation": {
    "min_length": 2,
    "max_length": 50,
    "pattern": "^[A-Za-z\\s]+$",
    "pattern_message": "Only letters and spaces allowed"
  }
}

// Number field validation
{
  "validation": {
    "min": 0,
    "max": 100,
    "step": 0.5,
    "decimal_places": 2
  }
}

// Date field validation
{
  "validation": {
    "min_date": "1990-01-01",
    "max_date": "today",
    "disallow_future": true
  }
}
```

### Custom Validation

```python
# Server-side custom validation example
def validate_student_id(value):
    if not value.startswith('STU'):
        raise ValidationError('Student ID must start with STU')
    if len(value) != 10:
        raise ValidationError('Student ID must be 10 characters')
```

## Conditional Fields

### Configuration

```json
{
  "name": "visa_required",
  "type": "boolean",
  "label": "Do you require a visa?"
},
{
  "name": "visa_type",
  "type": "choice",
  "label": "Visa Type",
  "conditional": {
    "show_if": {
      "field": "visa_required",
      "value": true
    }
  },
  "choices": [
    {"value": "student", "label": "Student Visa"},
    {"value": "exchange", "label": "Exchange Visa"}
  ]
}
```

### Client-side Implementation

```javascript
function handleConditionalFields(formData) {
  fields.forEach(field => {
    if (field.conditional) {
      const condition = field.conditional.show_if;
      const dependentValue = formData[condition.field];
      const shouldShow = dependentValue === condition.value;
      
      // Show/hide field based on condition
      document.querySelector(`[name="${field.name}"]`)
        .closest('.form-field')
        .style.display = shouldShow ? 'block' : 'none';
    }
  });
}
```

## Error Handling

### Validation Error Response

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Form validation failed",
    "details": {
      "first_name": ["This field is required"],
      "email": ["Enter a valid email address"],
      "date_of_birth": ["Date cannot be in the future"]
    }
  }
}
```

### Field-level Error Display

```javascript
function displayErrors(errors) {
  // Clear previous errors
  document.querySelectorAll('.error-message').forEach(el => el.remove());
  
  // Display new errors
  Object.entries(errors).forEach(([fieldName, messages]) => {
    const field = document.querySelector(`[name="${fieldName}"]`);
    if (field) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'error-message';
      errorDiv.textContent = messages.join(', ');
      field.parentNode.appendChild(errorDiv);
    }
  });
}
```

## Complete Example

### Multi-step Form Implementation

```javascript
// Complete multi-step form example
class ExchangeApplicationForm {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.exchangeId = null;
    this.currentStep = 1;
    this.steps = [];
    this.submissions = {};
  }
  
  async initialize() {
    // Load form configuration
    await this.loadSteps();
    
    // Create new exchange
    this.exchangeId = await this.createExchange();
    
    // Load existing progress
    await this.loadProgress();
    
    // Render current step
    this.renderStep();
  }
  
  async loadSteps() {
    const response = await fetch('/api/form-steps/', {
      headers: {'Authorization': `Bearer ${token}`}
    });
    this.steps = await response.json().results;
  }
  
  async createExchange() {
    const response = await fetch('/api/exchanges/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        // Basic exchange data
      })
    });
    const exchange = await response.json();
    return exchange.id;
  }
  
  async loadProgress() {
    const response = await fetch(`/api/exchanges/${this.exchangeId}/form_progress/`, {
      headers: {'Authorization': `Bearer ${token}`}
    });
    const progress = await response.json();
    this.currentStep = progress.next_step || 1;
    
    // Load existing submissions
    progress.steps.forEach(step => {
      if (step.submission_id) {
        this.submissions[step.step_number] = step.submission_id;
      }
    });
  }
  
  renderStep() {
    const step = this.steps.find(s => s.step_number === this.currentStep);
    if (!step) return;
    
    let html = `
      <h2>${step.name}</h2>
      <p>${step.description}</p>
      <form id="step-form">
    `;
    
    step.fields.forEach(field => {
      html += this.renderField(field);
    });
    
    html += `
      <div class="form-navigation">
        ${this.currentStep > 1 ? '<button type="button" onclick="app.previousStep()">Previous</button>' : ''}
        <button type="submit">
          ${this.currentStep === this.steps.length ? 'Submit Application' : 'Next'}
        </button>
      </div>
      </form>
    `;
    
    this.container.innerHTML = html;
    
    // Add event listener
    document.getElementById('step-form').addEventListener('submit', (e) => this.handleSubmit(e));
  }
  
  renderField(field) {
    let html = `<div class="form-field">`;
    html += `<label for="${field.name}">${field.label}`;
    if (field.required) html += ' *';
    html += '</label>';
    
    switch (field.type) {
      case 'text':
      case 'email':
        html += `<input type="${field.type}" id="${field.name}" name="${field.name}" 
                 placeholder="${field.placeholder || ''}" 
                 ${field.required ? 'required' : ''}>`;
        break;
        
      case 'choice':
        html += `<select id="${field.name}" name="${field.name}" ${field.required ? 'required' : ''}>`;
        html += '<option value="">Select...</option>';
        field.choices.forEach(choice => {
          html += `<option value="${choice.value}">${choice.label}</option>`;
        });
        html += '</select>';
        break;
        
      case 'textarea':
        html += `<textarea id="${field.name}" name="${field.name}" 
                 rows="4" ${field.required ? 'required' : ''}></textarea>`;
        break;
        
      case 'date':
        html += `<input type="date" id="${field.name}" name="${field.name}" 
                 ${field.required ? 'required' : ''}>`;
        break;
        
      case 'boolean':
        html += `<input type="checkbox" id="${field.name}" name="${field.name}">`;
        break;
    }
    
    if (field.help_text) {
      html += `<small class="help-text">${field.help_text}</small>`;
    }
    
    html += '</div>';
    return html;
  }
  
  async handleSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {};
    
    // Convert FormData to object
    formData.forEach((value, key) => {
      data[key] = value;
    });
    
    // Submit to server
    const step = this.steps.find(s => s.step_number === this.currentStep);
    const response = await fetch('/api/form-submissions/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        exchange: this.exchangeId,
        form_step: step.id,
        data: data
      })
    });
    
    if (response.ok) {
      const submission = await response.json();
      this.submissions[this.currentStep] = submission.id;
      
      if (this.currentStep < this.steps.length) {
        this.currentStep++;
        this.renderStep();
      } else {
        // Final submission
        await this.submitApplication();
      }
    } else {
      const error = await response.json();
      this.displayErrors(error.errors);
    }
  }
  
  async submitApplication() {
    // Transition exchange to submitted status
    const response = await fetch(`/api/exchanges/${this.exchangeId}/transition/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: 'submitted',
        comment: 'Application completed'
      })
    });
    
    if (response.ok) {
      // Show success message
      this.container.innerHTML = `
        <div class="success-message">
          <h2>Application Submitted Successfully!</h2>
          <p>Your exchange application has been submitted for review.</p>
          <a href="/applications/${this.exchangeId}">View Application</a>
        </div>
      `;
    }
  }
  
  previousStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.renderStep();
    }
  }
  
  displayErrors(errors) {
    // Implementation from earlier example
  }
}

// Initialize the form
const app = new ExchangeApplicationForm('form-container');
app.initialize();
```

## Best Practices

1. **Progressive Enhancement**: Forms should work without JavaScript
2. **Validation**: Implement both client and server-side validation
3. **Error Handling**: Provide clear, actionable error messages
4. **Accessibility**: Use proper labels, ARIA attributes
5. **Save Progress**: Auto-save form data to prevent loss
6. **Mobile Friendly**: Ensure forms work on all devices
