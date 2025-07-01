// Exchange module for SEIM application
const Exchange = {
    // Initialize the module
    init: function() {
        this.setupCSRF();
        this.bindEvents();
        this.initializeTooltips();
    },
    
    // Setup CSRF token for all AJAX requests
    setupCSRF: function() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", Exchange.getCsrfToken());
                }
            }
        });
    },
    
    // Get CSRF token from cookies
    getCsrfToken: function() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    },
    
    // Bind event handlers
    bindEvents: function() {
        // Document upload buttons
        $(document).on('click', '.upload-document-btn', function() {
            const exchangeId = $(this).data('exchange-id');
            $('#documentUploadModal').data('exchange-id', exchangeId);
            $('#documentUploadModal').modal('show');
        });
        
        // Workflow action buttons
        $(document).on('click', '.workflow-action', function() {
            const action = $(this).data('action');
            const exchangeId = $(this).data('exchange-id');
            Exchange.handleWorkflowAction(action, exchangeId);
        });
        
        // Document preview
        $(document).on('click', '.preview-document', function() {
            const documentId = $(this).data('document-id');
            Exchange.previewDocument(documentId);
        });
        
        // Delete document
        $(document).on('click', '.delete-document', function() {
            const documentId = $(this).data('document-id');
            const documentName = $(this).data('document-name');
            Exchange.deleteDocument(documentId, documentName);
        });
    },
    
    // Initialize Bootstrap tooltips
    initializeTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    // Handle workflow actions
    handleWorkflowAction: function(action, exchangeId) {
        let confirmMessage = '';
        let apiUrl = `/api/exchanges/${exchangeId}/`;
        
        switch(action) {
            case 'submit':
                confirmMessage = 'Are you sure you want to submit this exchange application? Once submitted, you cannot make changes.';
                apiUrl += 'submit/';
                break;
            case 'start_review':
                confirmMessage = 'Start reviewing this exchange application?';
                apiUrl += 'review/';
                break;
            case 'approve':
                confirmMessage = 'Are you sure you want to approve this exchange?';
                apiUrl += 'approve/';
                break;
            case 'reject':
                confirmMessage = 'Are you sure you want to reject this exchange?';
                const reason = prompt('Please provide a reason for rejection:');
                if (!reason) return;
                apiUrl += 'reject/';
                break;
            case 'cancel':
                confirmMessage = 'Are you sure you want to cancel this exchange?';
                apiUrl += 'cancel/';
                break;
            default:
                console.error('Unknown action:', action);
                return;
        }
        
        if (confirm(confirmMessage)) {
            Exchange.showLoader();
            
            const data = {};
            if (action === 'reject' && reason) {
                data.reason = reason;
            }
            
            $.ajax({
                url: apiUrl,
                type: 'POST',
                data: JSON.stringify(data),
                contentType: 'application/json',
                success: function(response) {
                    Exchange.hideLoader();
                    Exchange.showAlert('Action completed successfully!', 'success');
                    setTimeout(() => location.reload(), 1500);
                },
                error: function(xhr) {
                    Exchange.hideLoader();
                    const error = xhr.responseJSON?.error || 'An error occurred';
                    Exchange.showAlert(error, 'danger');
                }
            });
        }
    },
    
    // Preview document
    previewDocument: function(documentId) {
        const previewUrl = `/api/documents/${documentId}/preview/`;
        
        // Create preview modal if it doesn't exist
        if ($('#documentPreviewModal').length === 0) {
            const modalHtml = `
                <div class="modal fade" id="documentPreviewModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Document Preview</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div id="documentPreviewContent">
                                    <div class="text-center">
                                        <div class="spinner-border" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            $('body').append(modalHtml);
        }
        
        // Show modal and load content
        $('#documentPreviewModal').modal('show');
        $('#documentPreviewContent').html(`
            <iframe src="${previewUrl}" style="width: 100%; height: 600px; border: none;"></iframe>
        `);
    },
    
    // Delete document
    deleteDocument: function(documentId, documentName) {
        if (confirm(`Are you sure you want to delete "${documentName}"?`)) {
            Exchange.showLoader();
            
            $.ajax({
                url: `/api/documents/${documentId}/`,
                type: 'DELETE',
                success: function() {
                    Exchange.hideLoader();
                    Exchange.showAlert('Document deleted successfully!', 'success');
                    // Remove document from UI
                    $(`#document-${documentId}`).fadeOut(() => {
                        $(`#document-${documentId}`).remove();
                    });
                },
                error: function(xhr) {
                    Exchange.hideLoader();
                    const error = xhr.responseJSON?.error || 'Failed to delete document';
                    Exchange.showAlert(error, 'danger');
                }
            });
        }
    },
    
    // Show loader
    showLoader: function() {
        if ($('#globalLoader').length === 0) {
            const loaderHtml = `
                <div class="modal" id="globalLoader" data-bs-backdrop="static" tabindex="-1">
                    <div class="modal-dialog modal-sm modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-body text-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p class="mt-2 mb-0">Processing...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            $('body').append(loaderHtml);
        }
        $('#globalLoader').modal('show');
    },
    
    // Hide loader
    hideLoader: function() {
        $('#globalLoader').modal('hide');
    },
    
    // Show alert message
    showAlert: function(message, type = 'info') {
        // Create alert container if it doesn't exist
        if ($('#alertContainer').length === 0) {
            $('body').append('<div id="alertContainer" class="position-fixed top-0 end-0 p-3" style="z-index: 9999;"></div>');
        }
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        const alert = $(alertHtml);
        $('#alertContainer').append(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.fadeOut(() => alert.remove());
        }, 5000);
    },
    
    // Reload documents list
    reloadDocuments: function(exchangeId) {
        $.ajax({
            url: `/api/exchanges/${exchangeId}/documents/`,
            type: 'GET',
            success: function(documents) {
                let documentsHtml = '';
                documents.forEach(doc => {
                    documentsHtml += `
                        <tr id="document-${doc.id}">
                            <td>${doc.get_category_display}</td>
                            <td>
                                <a href="${doc.file}" target="_blank">${doc.name}</a>
                            </td>
                            <td>${new Date(doc.uploaded_at).toLocaleDateString()}</td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-info preview-document" 
                                            data-document-id="${doc.id}"
                                            title="Preview">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <a href="${doc.file}" 
                                       class="btn btn-primary" 
                                       download
                                       title="Download">
                                        <i class="fas fa-download"></i>
                                    </a>
                                    <button class="btn btn-danger delete-document" 
                                            data-document-id="${doc.id}"
                                            data-document-name="${doc.name}"
                                            title="Delete">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                });
                
                $('#documentsTableBody').html(documentsHtml);
                this.initializeTooltips();
            },
            error: function(xhr) {
                console.error('Failed to reload documents:', xhr);
            }
        });
    },
    
    // Form validation
    validateForm: function(formId) {
        const form = document.getElementById(formId);
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return false;
        }
        return true;
    },
    
    // Format date for display
    formatDate: function(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    // Handle multi-step form navigation
    navigateForm: function(direction) {
        const currentStep = $('.form-step.active');
        let nextStep;
        
        if (direction === 'next') {
            nextStep = currentStep.next('.form-step');
            if (nextStep.length === 0) return false;
            
            // Validate current step
            const inputs = currentStep.find('input[required], select[required], textarea[required]');
            let isValid = true;
            
            inputs.each(function() {
                if (!this.checkValidity()) {
                    $(this).addClass('is-invalid');
                    isValid = false;
                } else {
                    $(this).removeClass('is-invalid');
                }
            });
            
            if (!isValid) {
                currentStep.find('.invalid-feedback').show();
                return false;
            }
        } else {
            nextStep = currentStep.prev('.form-step');
            if (nextStep.length === 0) return false;
        }
        
        // Switch steps
        currentStep.removeClass('active').fadeOut(300, function() {
            nextStep.addClass('active').fadeIn(300);
        });
        
        // Update progress bar
        const totalSteps = $('.form-step').length;
        const currentIndex = nextStep.index() + 1;
        const progress = (currentIndex / totalSteps) * 100;
        
        $('.progress-bar').css('width', progress + '%')
                        .attr('aria-valuenow', progress)
                        .text(`Step ${currentIndex} of ${totalSteps}`);
        
        // Update navigation buttons
        $('#prevBtn').prop('disabled', currentIndex === 1);
        $('#nextBtn').text(currentIndex === totalSteps ? 'Submit' : 'Next');
        
        return true;
    }
};

// Initialize when document is ready
$(document).ready(function() {
    Exchange.init();
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });
    
    // Auto-save form data
    if ($('#exchangeForm').length) {
        setInterval(function() {
            const formData = $('#exchangeForm').serialize();
            localStorage.setItem('exchangeFormData', formData);
            Exchange.showAlert('Form data auto-saved', 'info');
        }, 30000); // Auto-save every 30 seconds
        
        // Restore saved data on page load
        const savedData = localStorage.getItem('exchangeFormData');
        if (savedData) {
            // Parse and restore form data
            const params = new URLSearchParams(savedData);
            params.forEach((value, key) => {
                $(`[name="${key}"]`).val(value);
            });
        }
    }
});

// Export for use in other modules
window.Exchange = Exchange;