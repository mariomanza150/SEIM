# SEIM Front-End Implementation Plan - Part 2: Exchange Detail View

## 1. Exchange Detail View Implementation

The Exchange Detail View is a critical component that displays all information about a specific exchange application, including documents, timeline, and administrative actions.

### File: `exchange/templates/exchange/exchange_detail.html`

```html
{% extends 'base/base.html' %}
{% block title %}Exchange Details - {{ exchange.id }}{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h3>Exchange Application #{{ exchange.id }}</h3>
                    <span class="badge bg-{{ exchange.status|status_color }}">
                        {{ exchange.get_status_display }}
                    </span>
                </div>
                <div class="card-body">
                    <!-- Exchange details -->
                    <h5>Student Information</h5>
                    <dl class="row">
                        <dt class="col-sm-4">Name:</dt>
                        <dd class="col-sm-8">{{ exchange.student.get_full_name }}</dd>
                        
                        <dt class="col-sm-4">Email:</dt>
                        <dd class="col-sm-8">{{ exchange.student.email }}</dd>
                        
                        <dt class="col-sm-4">Home University:</dt>
                        <dd class="col-sm-8">{{ exchange.home_university }}</dd>
                        
                        <dt class="col-sm-4">Host University:</dt>
                        <dd class="col-sm-8">{{ exchange.host_university }}</dd>
                        
                        <dt class="col-sm-4">Program:</dt>
                        <dd class="col-sm-8">{{ exchange.program }}</dd>
                        
                        <dt class="col-sm-4">Duration:</dt>
                        <dd class="col-sm-8">
                            {{ exchange.start_date|date:"M d, Y" }} - 
                            {{ exchange.end_date|date:"M d, Y" }}
                        </dd>
                    </dl>
                </div>
            </div>
            
            <!-- Documents Section -->
            <div class="card mt-3">
                <div class="card-header">
                    <h4>Documents</h4>
                    <button class="btn btn-sm btn-primary float-end" data-bs-toggle="modal" data-bs-target="#uploadModal">
                        <i class="fas fa-upload"></i> Upload Document
                    </button>
                </div>
                <div class="card-body">
                    <div id="documents-container">
                        <!-- Documents will be loaded via AJAX -->
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <!-- Timeline/Status Section -->
            <div class="card">
                <div class="card-header">
                    <h4>Application Timeline</h4>
                </div>
                <div class="card-body">
                    <div id="timeline-container">
                        <!-- Timeline will be loaded via AJAX -->
                    </div>
                </div>
            </div>
            
            <!-- Actions Section -->
            {% if user.profile.role in 'COORDINATOR,ADMINISTRATOR' and exchange.status == 'submitted' %}
            <div class="card mt-3">
                <div class="card-header">
                    <h4>Actions</h4>
                </div>
                <div class="card-body">
                    <button class="btn btn-success btn-block mb-2" onclick="updateStatus('approved')">
                        <i class="fas fa-check"></i> Approve
                    </button>
                    <button class="btn btn-danger btn-block" onclick="updateStatus('rejected')">
                        <i class="fas fa-times"></i> Reject
                    </button>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>

<!-- Upload Modal -->
<div class="modal fade" id="uploadModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Upload Document</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="mb-3">
                        <label class="form-label">Document Type</label>
                        <select class="form-control" name="category" required>
                            <option value="transcript">Transcript</option>
                            <option value="recommendation">Recommendation Letter</option>
                            <option value="financial">Financial Statement</option>
                            <option value="passport">Passport</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">File</label>
                        <input type="file" class="form-control" name="file" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea class="form-control" name="description" rows="3"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="uploadDocument()">Upload</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// Load documents and timeline on page load
$(document).ready(function() {
    loadDocuments();
    loadTimeline();
});

function loadDocuments() {
    $.get(`/api/exchanges/{{ exchange.id }}/documents/`, function(data) {
        let html = '';
        data.forEach(doc => {
            html += `
                <div class="document-item mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6>${doc.name}</h6>
                            <small class="text-muted">${doc.category} - ${new Date(doc.uploaded_at).toLocaleDateString()}</small>
                        </div>
                        <div>
                            <a href="${doc.file}" class="btn btn-sm btn-outline-primary" target="_blank">
                                <i class="fas fa-eye"></i> View
                            </a>
                            <a href="${doc.file}" class="btn btn-sm btn-outline-secondary" download>
                                <i class="fas fa-download"></i> Download
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });
        $('#documents-container').html(html || '<p class="text-muted">No documents uploaded yet.</p>');
    });
}

function loadTimeline() {
    $.get(`/api/exchanges/{{ exchange.id }}/workflow_history/`, function(data) {
        let html = '<ul class="timeline">';
        data.forEach(event => {
            html += `
                <li class="timeline-item">
                    <span class="timeline-badge bg-${getStatusColor(event.new_status)}">
                        <i class="fas fa-${getStatusIcon(event.new_status)}"></i>
                    </span>
                    <div class="timeline-content">
                        <h6>${event.new_status}</h6>
                        <p class="text-muted">${event.comment || 'No comment'}</p>
                        <small>${new Date(event.created_at).toLocaleDateString()}</small>
                    </div>
                </li>
            `;
        });
        html += '</ul>';
        $('#timeline-container').html(html);
    });
}

function updateStatus(newStatus) {
    const comment = prompt('Please provide a comment for this action:');
    if (comment !== null) {
        $.post({
            url: `/api/exchanges/{{ exchange.id }}/transition/`,
            data: JSON.stringify({ status: newStatus, comment: comment }),
            contentType: 'application/json',
            success: function() {
                window.location.reload();
            },
            error: function(xhr) {
                alert('Error: ' + xhr.responseJSON.detail);
            }
        });
    }
}

function uploadDocument() {
    const formData = new FormData($('#uploadForm')[0]);
    formData.append('exchange', {{ exchange.id }});
    
    $.ajax({
        url: '/api/documents/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function() {
            $('#uploadModal').modal('hide');
            loadDocuments();
        },
        error: function(xhr) {
            alert('Error: ' + xhr.responseJSON.detail);
        }
    });
}

function getStatusColor(status) {
    const colors = {
        'draft': 'secondary',
        'submitted': 'warning',
        'under_review': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'completed': 'primary'
    };
    return colors[status] || 'secondary';
}

function getStatusIcon(status) {
    const icons = {
        'draft': 'edit',
        'submitted': 'paper-plane',
        'under_review': 'search',
        'approved': 'check',
        'rejected': 'times',
        'completed': 'trophy'
    };
    return icons[status] || 'circle';
}
</script>
{% endblock %}
```

### Implementation Tasks for Exchange Detail View

1. **Update View Function**
   - Update `exchange_detail_view` in `template_views.py`
   - Add permission checks
   - Pass exchange object to template

2. **Create Template Tags**
   - Create custom template filter for status colors
   - Add helper functions for formatting

3. **Enhance JavaScript**
   - Add error handling for AJAX calls
   - Implement loading indicators
   - Add confirmation dialogs

4. **CSS Styling**
   - Create timeline styles
   - Style document cards
   - Add responsive design

5. **Testing Requirements**
   - Test document upload functionality
   - Verify status transitions
   - Check permission restrictions

### Additional Features to Implement

1. **Document Preview**
   - Integrate PDF.js for inline preview
   - Add image preview for supported formats
   - Create preview modal

2. **Comments System**
   - Add comment thread for exchanges
   - Real-time updates using WebSockets
   - Notification for new comments

3. **File Validation**
   - Client-side file size validation
   - File type restrictions
   - Virus scanning integration

4. **Audit Trail**
   - Display who made changes
   - Show IP addresses
   - Add detailed timestamps

## Continue to Part 3 for Exchange Create/Edit Forms implementation.