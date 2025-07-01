# SEIM Front-End Implementation Plan - Part 3: Exchange Create/Edit Forms

## 2. Exchange Create/Edit Forms Implementation

The multi-step form for creating and editing exchange applications provides a user-friendly interface for students to submit their applications.

### File: `exchange/templates/exchange/exchange_form.html`

```html
{% extends 'base/base.html' %}
{% block title %}{% if exchange %}Edit{% else %}Create{% endif %} Exchange Application{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h3>{% if exchange %}Edit{% else %}New{% endif %} Exchange Application</h3>
                    <div class="progress mt-3">
                        <div class="progress-bar" role="progressbar" style="width: 0%" id="formProgress"></div>
                    </div>
                </div>
                <div class="card-body">
                    <form id="exchangeForm" method="post">
                        {% csrf_token %}
                        
                        <!-- Step 1: Personal Information -->
                        <div class="form-step" id="step-1">
                            <h5>Personal Information</h5>
                            <div class="mb-3">
                                <label class="form-label">First Name</label>
                                <input type="text" class="form-control" name="first_name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Last Name</label>
                                <input type="text" class="form-control" name="last_name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" name="email" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Phone</label>
                                <input type="tel" class="form-control" name="phone">
                            </div>
                        </div>
                        
                        <!-- Step 2: Academic Information -->
                        <div class="form-step d-none" id="step-2">
                            <h5>Academic Information</h5>
                            <div class="mb-3">
                                <label class="form-label">Home University</label>
                                <input type="text" class="form-control" name="home_university" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Current Degree</label>
                                <input type="text" class="form-control" name="degree" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Major</label>
                                <input type="text" class="form-control" name="major" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">GPA</label>
                                <input type="number" step="0.01" class="form-control" name="gpa" min="0" max="4.0">
                            </div>
                        </div>
                        
                        <!-- Step 3: Exchange Details -->
                        <div class="form-step d-none" id="step-3">
                            <h5>Exchange Details</h5>
                            <div class="mb-3">
                                <label class="form-label">Host University</label>
                                <select class="form-control" name="host_university" required>
                                    <option value="">Select university...</option>
                                    <!-- Options loaded via AJAX -->
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Exchange Program</label>
                                <select class="form-control" name="program" required>
                                    <option value="">Select program...</option>
                                    <!-- Options loaded via AJAX -->
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Start Date</label>
                                <input type="date" class="form-control" name="start_date" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">End Date</label>
                                <input type="date" class="form-control" name="end_date" required>
                            </div>
                        </div>
                        
                        <!-- Step 4: Additional Information -->
                        <div class="form-step d-none" id="step-4">
                            <h5>Additional Information</h5>
                            <div class="mb-3">
                                <label class="form-label">Language Proficiency</label>
                                <textarea class="form-control" name="language_proficiency" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Study Goals</label>
                                <textarea class="form-control" name="study_goals" rows="4"></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Special Requirements</label>
                                <textarea class="form-control" name="special_requirements" rows="3"></textarea>
                            </div>
                        </div>
                        
                        <div class="d-flex justify-content-between mt-4">
                            <button type="button" class="btn btn-secondary" id="prevBtn" onclick="changeStep(-1)">Previous</button>
                            <button type="button" class="btn btn-primary" id="nextBtn" onclick="changeStep(1)">Next</button>
                            <button type="submit" class="btn btn-success d-none" id="submitBtn">Submit Application</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
let currentStep = 1;
const totalSteps = 4;

function showStep(step) {
    // Hide all steps
    $('.form-step').addClass('d-none');
    
    // Show current step
    $(`#step-${step}`).removeClass('d-none');
    
    // Update progress bar
    const progress = (step / totalSteps) * 100;
    $('#formProgress').css('width', progress + '%');
    
    // Update buttons
    $('#prevBtn').toggle(step > 1);
    $('#nextBtn').toggle(step < totalSteps);
    $('#submitBtn').toggle(step === totalSteps);
}

function changeStep(direction) {
    // Validate current step before moving forward
    if (direction > 0 && !validateStep(currentStep)) {
        return;
    }
    
    currentStep += direction;
    currentStep = Math.max(1, Math.min(currentStep, totalSteps));
    showStep(currentStep);
}

function validateStep(step) {
    const stepElement = $(`#step-${step}`);
    const requiredFields = stepElement.find('[required]');
    let isValid = true;
    
    requiredFields.each(function() {
        if (!$(this).val()) {
            $(this).addClass('is-invalid');
            isValid = false;
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    return isValid;
}

// Save form data to localStorage
$('input, select, textarea').on('change', function() {
    const formData = $('#exchangeForm').serialize();
    localStorage.setItem('exchangeFormData', formData);
});

// Load saved form data
$(document).ready(function() {
    const savedData = localStorage.getItem('exchangeFormData');
    if (savedData) {
        // Parse and populate form
        const params = new URLSearchParams(savedData);
        params.forEach((value, key) => {
            $(`[name="${key}"]`).val(value);
        });
    }
    
    // Load dynamic options
    loadUniversities();
    loadPrograms();
    
    showStep(currentStep);
});

function loadUniversities() {
    $.get('/api/universities/', function(data) {
        const select = $('select[name="host_university"]');
        data.forEach(uni => {
            select.append(`<option value="${uni.id}">${uni.name}</option>`);
        });
    });
}

function loadPrograms() {
    $.get('/api/programs/', function(data) {
        const select = $('select[name="program"]');
        data.forEach(program => {
            select.append(`<option value="${program.id}">${program.name}</option>`);
        });
    });
}

// Form submission
$('#exchangeForm').on('submit', function(e) {
    e.preventDefault();
    
    if (!validateStep(totalSteps)) {
        return;
    }
    
    const formData = $(this).serialize();
    
    $.post({
        url: '{% if exchange %}/api/exchanges/{{ exchange.id }}/{% else %}/api/exchanges/{% endif %}',
        data: formData,
        success: function(response) {
            localStorage.removeItem('exchangeFormData');
            window.location.href = `/exchanges/${response.id}/`;
        },
        error: function(xhr) {
            alert('Error: ' + xhr.responseJSON.detail);
        }
    });
});
</script>
{% endblock %}
```

### Implementation Tasks for Exchange Forms

1. **Backend View Updates**
   - Create `ExchangeCreateView` and `ExchangeUpdateView`
   - Implement form validation logic
   - Add permission checks
   - Handle file uploads

2. **Form Class Creation**
   - Create `ExchangeForm` with field validation
   - Add custom validators for dates
   - Implement conditional field requirements

3. **Dynamic Field Loading**
   - Create API endpoints for universities
   - Create API endpoints for programs
   - Add dependent field loading

4. **Progress Persistence**
   - Implement draft saving functionality
   - Add auto-save feature
   - Create resume later option

5. **Enhanced Validation**
   - Add date range validation
   - Implement GPA format validation
   - Add email verification

### Additional Features for Forms

1. **File Upload Integration**
   - Add document upload steps
   - Progress indicators for uploads
   - Drag-and-drop support

2. **Field Dependencies**
   - Program options based on university
   - Required documents based on program
   - Dynamic form sections

3. **Validation Messages**
   - Inline error messages
   - Success indicators
   - Help text tooltips

4. **Mobile Optimization**
   - Responsive form layout
   - Touch-friendly controls
   - Simplified navigation

## Continue to Part 4 for Advanced Filtering and Document Management implementation.