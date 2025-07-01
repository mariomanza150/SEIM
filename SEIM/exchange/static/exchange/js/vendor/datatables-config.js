// DataTables Standard Configuration for SGII
// Prevent redeclaration if already loaded
if (typeof window.SGII_DataTables_Config === 'undefined') {
window.SGII_DataTables_Config = {
    responsive: true,
    processing: true,
    serverSide: true,
    pageLength: 25,
    lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    dom: 'Bfrtip',
    buttons: [
        {
            extend: 'copy',
            className: 'btn btn-secondary btn-sm',
            text: '<i class="bi bi-clipboard me-1"></i>Copy'
        },
        {
            extend: 'csv', 
            className: 'btn btn-secondary btn-sm',
            text: '<i class="bi bi-filetype-csv me-1"></i>CSV'
        },
        {
            extend: 'excel',
            className: 'btn btn-secondary btn-sm',
            text: '<i class="bi bi-file-earmark-excel me-1"></i>Excel'
        },
        {
            extend: 'pdf',
            className: 'btn btn-secondary btn-sm',
            text: '<i class="bi bi-filetype-pdf me-1"></i>PDF'
        },
        {
            extend: 'colvis',
            text: '<i class="bi bi-columns me-1"></i>Columns',
            className: 'btn btn-secondary btn-sm'
        }
    ],
    language: {
        processing: '<div class="d-flex justify-content-center align-items-center p-4"><div class="spinner-border text-primary me-3" role="status"><span class="visually-hidden">Loading...</span></div><span>Processing...</span></div>',
        emptyTable: '<div class="text-center py-5"><div class="avatar mx-auto mb-3 bg-light text-muted d-flex align-items-center justify-content-center" style="width: 4rem; height: 4rem;"><i class="bi bi-inbox display-6"></i></div><h6 class="text-muted">No data available</h6></div>',
        zeroRecords: '<div class="text-center py-5"><div class="avatar mx-auto mb-3 bg-light text-muted d-flex align-items-center justify-content-center" style="width: 4rem; height: 4rem;"><i class="bi bi-search display-6"></i></div><h6 class="text-muted">No matching records found</h6><p class="text-muted small mb-0">Try adjusting your search terms</p></div>',
        lengthMenu: "Show _MENU_ entries per page",
        info: "Showing _START_ to _END_ of _TOTAL_ entries",
        infoEmpty: "Showing 0 to 0 of 0 entries",
        infoFiltered: "(filtered from _MAX_ total entries)",
        search: "Search:",
        paginate: {
            first: '<i class="bi bi-chevron-double-left"></i>',
            last: '<i class="bi bi-chevron-double-right"></i>',
            next: '<i class="bi bi-chevron-right"></i>',
            previous: '<i class="bi bi-chevron-left"></i>'
        }
    },
    initComplete: function() {
        // Add custom styling after initialization
        this.api().buttons().container().addClass('mb-3');
    }
};
}

// Helper function to get CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Initialize DataTables with SGII config
function initSGIIDataTable(tableId, ajaxUrl, columns, customConfig = {}) {
    const config = Object.assign({}, window.SGII_DataTables_Config, {
        ajax: {
            url: ajaxUrl,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            error: function(xhr, error, code) {
                console.error('DataTables AJAX error:', error, code);
                // Show user-friendly error message
                const table = $(tableId).closest('.dataTables_wrapper');
                table.find('.dataTables_processing').html(
                    '<div class="text-center py-4 text-danger">' +
                    '<i class="bi bi-exclamation-triangle display-6 mb-3"></i>' +
                    '<h6>Error loading data</h6>' +
                    '<p class="small mb-0">Please refresh the page and try again</p>' +
                    '</div>'
                );
            }
        },
        columns: columns
    }, customConfig);
    
    return $(tableId).DataTable(config);
}

// Status color helper function for exchanges
function getExchangeStatusBadge(status) {
    const statusConfig = {
        'DRAFT': { class: 'bg-light text-muted border', label: 'Draft' },
        'SUBMITTED': { class: 'bg-warning-subtle text-warning border border-warning-subtle', label: 'Submitted' },
        'UNDER_REVIEW': { class: 'bg-info-subtle text-info border border-info-subtle', label: 'Under Review' },
        'APPROVED': { class: 'bg-success-subtle text-success border border-success-subtle', label: 'Approved' },
        'REJECTED': { class: 'bg-danger-subtle text-danger border border-danger-subtle', label: 'Rejected' },
        'COMPLETED': { class: 'bg-secondary-subtle text-secondary border border-secondary-subtle', label: 'Completed' }
    };
    
    const config = statusConfig[status] || statusConfig['DRAFT'];
    return `<span class="badge ${config.class}">${config.label}</span>`;
}

// Format date helper
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

// Format duration helper
function formatDuration(startDate, endDate) {
    if (!startDate || !endDate) return '<span class="text-muted">Not specified</span>';
    const start = new Date(startDate);
    const end = new Date(endDate);
    return `${start.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}`;
}
