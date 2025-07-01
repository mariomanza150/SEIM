/**
 * Enhanced Bulk Actions for SGII DataTables
 * Provides progress tracking, visual feedback, and improved user experience
 */

class SGIIBulkActions {
    constructor(tableId, bulkActionEndpoint) {
        this.table = $(tableId).DataTable();
        this.tableId = tableId;
        this.bulkActionEndpoint = bulkActionEndpoint;
        this.selectedItems = new Set();
        this.actionHistory = [];
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        this.createBulkActionBar();
        this.createProgressModal();
        this.createResultsModal();
        this.bindEvents();
        this.setupSelectionHandling();
        
        console.log('SGII Bulk Actions initialized for table:', this.tableId);
    }
    
    createBulkActionBar() {
        const existingBar = document.getElementById('bulkActionBar');
        if (existingBar) {
            return; // Already exists
        }
        
        const actionBar = `
        <div id="bulkActionBar" class="card border-0 shadow-sm mb-3 d-none">
            <div class="card-body py-3">
                <div class="row align-items-center">
                    <div class="col-md-4">
                        <div class="d-flex align-items-center">
                            <div class="form-check me-3">
                                <input class="form-check-input" type="checkbox" id="selectAllItems">
                                <label class="form-check-label" for="selectAllItems">
                                    Select All
                                </label>
                            </div>
                            <span id="selectedCount" class="badge bg-primary-subtle text-primary border border-primary-subtle">
                                0 selected
                            </span>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="d-flex justify-content-end gap-2">
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-success btn-sm" 
                                        id="bulkApproveBtn" 
                                        onclick="sgiiBulkActions.showBulkActionModal('approve')"
                                        disabled>
                                    <i class="bi bi-check-circle me-1"></i>
                                    Approve Selected
                                </button>
                                <button type="button" class="btn btn-danger btn-sm" 
                                        id="bulkRejectBtn" 
                                        onclick="sgiiBulkActions.showBulkActionModal('reject')"
                                        disabled>
                                    <i class="bi bi-x-circle me-1"></i>
                                    Reject Selected
                                </button>
                            </div>
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-outline-secondary btn-sm" 
                                        id="bulkAssignBtn" 
                                        onclick="sgiiBulkActions.showBulkActionModal('assign')"
                                        disabled>
                                    <i class="bi bi-person-plus me-1"></i>
                                    Assign To
                                </button>
                                <button type="button" class="btn btn-outline-info btn-sm" 
                                        id="bulkStatusBtn" 
                                        onclick="sgiiBulkActions.showBulkActionModal('status')"
                                        disabled>
                                    <i class="bi bi-arrow-repeat me-1"></i>
                                    Change Status
                                </button>
                            </div>
                            <button type="button" class="btn btn-outline-secondary btn-sm" 
                                    onclick="sgiiBulkActions.clearSelection()">
                                <i class="bi bi-x-lg me-1"></i>
                                Clear Selection
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        // Insert the action bar before the table
        const tableWrapper = $(this.tableId).closest('.dataTables_wrapper');
        tableWrapper.before(actionBar);
    }
    
    createProgressModal() {
        const modalHtml = `
        <div class="modal fade" id="bulkProgressModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <h5 class="modal-title">
                            <i class="bi bi-gear-fill me-2 text-primary"></i>
                            Processing Bulk Action
                        </h5>
                    </div>
                    <div class="modal-body text-center py-4">
                        <div class="mb-3">
                            <div class="spinner-border text-primary mb-3" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <h6 id="progressAction" class="mb-2">Processing applications...</h6>
                        <div class="progress mb-3" style="height: 12px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                 id="bulkProgressBar" 
                                 role="progressbar" 
                                 style="width: 0%"
                                 aria-valuenow="0" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                            </div>
                        </div>
                        <div class="d-flex justify-content-between text-muted small">
                            <span>Progress: <span id="progressCurrent">0</span> of <span id="progressTotal">0</span></span>
                            <span>Estimated time: <span id="estimatedTime">Calculating...</span></span>
                        </div>
                        <div class="mt-3">
                            <div id="progressDetails" class="text-start small text-muted">
                                <ul id="progressLog" class="list-unstyled mb-0" style="max-height: 150px; overflow-y: auto;"></ul>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-0">
                        <button type="button" class="btn btn-outline-danger btn-sm" 
                                id="cancelBulkAction" 
                                onclick="sgiiBulkActions.cancelBulkAction()"
                                disabled>
                            <i class="bi bi-stop-circle me-1"></i>
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        // Remove existing modal if any
        $('#bulkProgressModal').remove();
        $('body').append(modalHtml);
    }
    
    createResultsModal() {
        const modalHtml = `
        <div class="modal fade" id="bulkResultsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-clipboard-check me-2"></i>
                            Bulk Action Results
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div id="resultsContent">
                            <!-- Results will be populated here -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-primary" id="exportResults">
                            <i class="bi bi-download me-1"></i>
                            Export Results
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        // Remove existing modal if any
        $('#bulkResultsModal').remove();
        $('body').append(modalHtml);
    }
    
    bindEvents() {
        // Select all checkbox
        $('#selectAllItems').on('change', (e) => {
            this.toggleSelectAll(e.target.checked);
        });
        
        // Export results button
        $('#exportResults').on('click', () => {
            this.exportResults();
        });
    }
    
    setupSelectionHandling() {\n        // Add selection checkboxes to table\n        const self = this;\n        \n        // Override table drawing to add checkboxes\n        this.table.on('draw.dt', function() {\n            self.addSelectionCheckboxes();\n        });\n        \n        // Initial checkbox addition\n        this.addSelectionCheckboxes();\n    }\n    \n    addSelectionCheckboxes() {\n        const self = this;\n        \n        // Add checkboxes to each row if not already present\n        this.table.rows().every(function() {\n            const row = this.node();\n            const data = this.data();\n            const exchangeId = data[0]; // Assuming first column is ID\n            \n            // Check if checkbox already exists\n            if ($(row).find('.row-selector').length === 0) {\n                // Insert checkbox as first cell\n                const checkboxCell = `\n                    <td class=\"pe-2\">\n                        <div class=\"form-check\">\n                            <input class=\"form-check-input row-selector\" \n                                   type=\"checkbox\" \n                                   value=\"${exchangeId}\" \n                                   id=\"row_${exchangeId}\">\n                            <label class=\"form-check-label\" for=\"row_${exchangeId}\"></label>\n                        </div>\n                    </td>\n                `;\n                \n                $(row).prepend(checkboxCell);\n            }\n        });\n        \n        // Bind checkbox events\n        $('.row-selector').off('change').on('change', function() {\n            const exchangeId = $(this).val();\n            if ($(this).is(':checked')) {\n                self.selectedItems.add(exchangeId);\n            } else {\n                self.selectedItems.delete(exchangeId);\n            }\n            self.updateSelectionUI();\n        });\n    }\n    \n    toggleSelectAll(checked) {\n        $('.row-selector').prop('checked', checked);\n        \n        if (checked) {\n            $('.row-selector').each((index, checkbox) => {\n                this.selectedItems.add($(checkbox).val());\n            });\n        } else {\n            this.selectedItems.clear();\n        }\n        \n        this.updateSelectionUI();\n    }\n    \n    updateSelectionUI() {\n        const count = this.selectedItems.size;\n        const actionBar = $('#bulkActionBar');\n        \n        if (count > 0) {\n            actionBar.removeClass('d-none');\n            $('#selectedCount').text(`${count} selected`);\n            $('#bulkApproveBtn, #bulkRejectBtn, #bulkAssignBtn, #bulkStatusBtn').prop('disabled', false);\n        } else {\n            actionBar.addClass('d-none');\n            $('#bulkApproveBtn, #bulkRejectBtn, #bulkAssignBtn, #bulkStatusBtn').prop('disabled', true);\n        }\n        \n        // Update select all checkbox state\n        const totalCheckboxes = $('.row-selector').length;\n        const selectAllCheckbox = $('#selectAllItems');\n        \n        if (count === 0) {\n            selectAllCheckbox.prop('indeterminate', false).prop('checked', false);\n        } else if (count === totalCheckboxes) {\n            selectAllCheckbox.prop('indeterminate', false).prop('checked', true);\n        } else {\n            selectAllCheckbox.prop('indeterminate', true).prop('checked', false);\n        }\n    }\n    \n    clearSelection() {\n        this.selectedItems.clear();\n        $('.row-selector').prop('checked', false);\n        this.updateSelectionUI();\n    }\n    \n    showBulkActionModal(action) {\n        if (this.selectedItems.size === 0) {\n            alert('Please select items first.');\n            return;\n        }\n        \n        const modalContent = this.createBulkActionModalContent(action);\n        \n        // Create and show modal\n        const modalHtml = `\n        <div class=\"modal fade\" id=\"bulkActionModal\" tabindex=\"-1\">\n            <div class=\"modal-dialog\">\n                <div class=\"modal-content\">\n                    ${modalContent}\n                </div>\n            </div>\n        </div>\n        `;\n        \n        $('#bulkActionModal').remove();\n        $('body').append(modalHtml);\n        $('#bulkActionModal').modal('show');\n    }\n    \n    createBulkActionModalContent(action) {\n        const selectedCount = this.selectedItems.size;\n        let title, body, actionButton;\n        \n        switch (action) {\n            case 'approve':\n                title = `<i class=\"bi bi-check-circle me-2 text-success\"></i>Approve ${selectedCount} Applications`;\n                body = `\n                    <p>You are about to approve <strong>${selectedCount}</strong> selected applications.</p>\n                    <div class=\"mb-3\">\n                        <label class=\"form-label\">Comment (Optional)</label>\n                        <textarea class=\"form-control\" id=\"bulkComment\" rows=\"3\" \n                                  placeholder=\"Add a comment for this bulk approval...\"></textarea>\n                    </div>\n                `;\n                actionButton = `\n                    <button type=\"button\" class=\"btn btn-success\" \n                            onclick=\"sgiiBulkActions.performBulkAction('approve')\">\n                        <i class=\"bi bi-check-circle me-1\"></i>Approve All\n                    </button>\n                `;\n                break;\n                \n            case 'reject':\n                title = `<i class=\"bi bi-x-circle me-2 text-danger\"></i>Reject ${selectedCount} Applications`;\n                body = `\n                    <div class=\"alert alert-warning\" role=\"alert\">\n                        <i class=\"bi bi-exclamation-triangle me-2\"></i>\n                        You are about to reject <strong>${selectedCount}</strong> selected applications.\n                    </div>\n                    <div class=\"mb-3\">\n                        <label class=\"form-label\">Rejection Reason <span class=\"text-danger\">*</span></label>\n                        <textarea class=\"form-control\" id=\"bulkComment\" rows=\"3\" \n                                  placeholder=\"Please provide a reason for rejection...\" \n                                  required></textarea>\n                    </div>\n                `;\n                actionButton = `\n                    <button type=\"button\" class=\"btn btn-danger\" \n                            onclick=\"sgiiBulkActions.performBulkAction('reject')\">\n                        <i class=\"bi bi-x-circle me-1\"></i>Reject All\n                    </button>\n                `;\n                break;\n                \n            case 'assign':\n                title = `<i class=\"bi bi-person-plus me-2 text-info\"></i>Assign ${selectedCount} Applications`;\n                body = `\n                    <p>Assign <strong>${selectedCount}</strong> selected applications to a reviewer.</p>\n                    <div class=\"mb-3\">\n                        <label class=\"form-label\">Assign To <span class=\"text-danger\">*</span></label>\n                        <select class=\"form-select\" id=\"assignTo\" required>\n                            <option value=\"\">Select a reviewer...</option>\n                            <option value=\"coordinator1\">Dr. Smith (Coordinator)</option>\n                            <option value=\"coordinator2\">Prof. Johnson (Coordinator)</option>\n                            <option value=\"manager1\">Alice Brown (Manager)</option>\n                        </select>\n                    </div>\n                    <div class=\"mb-3\">\n                        <label class=\"form-label\">Comment (Optional)</label>\n                        <textarea class=\"form-control\" id=\"bulkComment\" rows=\"2\" \n                                  placeholder=\"Add a note about this assignment...\"></textarea>\n                    </div>\n                `;\n                actionButton = `\n                    <button type=\"button\" class=\"btn btn-info\" \n                            onclick=\"sgiiBulkActions.performBulkAction('assign')\">\n                        <i class=\"bi bi-person-plus me-1\"></i>Assign All\n                    </button>\n                `;\n                break;\n                \n            case 'status':\n                title = `<i class=\"bi bi-arrow-repeat me-2 text-warning\"></i>Change Status for ${selectedCount} Applications`;\n                body = `\n                    <p>Change status for <strong>${selectedCount}</strong> selected applications.</p>\n                    <div class=\"mb-3\">\n                        <label class=\"form-label\">New Status <span class=\"text-danger\">*</span></label>\n                        <select class=\"form-select\" id=\"newStatus\" required>\n                            <option value=\"\">Select new status...</option>\n                            <option value=\"UNDER_REVIEW\">Under Review</option>\n                            <option value=\"APPROVED\">Approved</option>\n                            <option value=\"REJECTED\">Rejected</option>\n                            <option value=\"COMPLETED\">Completed</option>\n                        </select>\n                    </div>\n                    <div class=\"mb-3\">\n                        <label class=\"form-label\">Comment (Optional)</label>\n                        <textarea class=\"form-control\" id=\"bulkComment\" rows=\"2\" \n                                  placeholder=\"Add a note about this status change...\"></textarea>\n                    </div>\n                `;\n                actionButton = `\n                    <button type=\"button\" class=\"btn btn-warning\" \n                            onclick=\"sgiiBulkActions.performBulkAction('status')\">\n                        <i class=\"bi bi-arrow-repeat me-1\"></i>Update Status\n                    </button>\n                `;\n                break;\n        }\n        \n        return `\n            <div class=\"modal-header\">\n                <h5 class=\"modal-title\">${title}</h5>\n                <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"modal\"></button>\n            </div>\n            <div class=\"modal-body\">\n                ${body}\n            </div>\n            <div class=\"modal-footer\">\n                <button type=\"button\" class=\"btn btn-outline-secondary\" data-bs-dismiss=\"modal\">\n                    Cancel\n                </button>\n                ${actionButton}\n            </div>\n        `;\n    }\n    \n    async performBulkAction(action) {\n        if (this.isProcessing) {\n            return; // Prevent multiple simultaneous actions\n        }\n        \n        // Validate inputs\n        if (!this.validateBulkAction(action)) {\n            return;\n        }\n        \n        this.isProcessing = true;\n        \n        // Hide action modal and show progress modal\n        $('#bulkActionModal').modal('hide');\n        $('#bulkProgressModal').modal('show');\n        \n        // Prepare data\n        const selectedIds = Array.from(this.selectedItems);\n        const comment = $('#bulkComment').val() || '';\n        const assignTo = $('#assignTo').val() || '';\n        const newStatus = $('#newStatus').val() || '';\n        \n        try {\n            // Initialize progress\n            this.initializeProgress(action, selectedIds.length);\n            \n            // Process in batches\n            const results = await this.processBulkInBatches(action, selectedIds, {\n                comment,\n                assignTo,\n                newStatus,\n                batchSize: 5 // Process 5 items at a time\n            });\n            \n            // Hide progress modal and show results\n            $('#bulkProgressModal').modal('hide');\n            this.showResultsSummary(results);\n            \n            // Clear selection and refresh table\n            this.clearSelection();\n            this.table.ajax.reload();\n            \n        } catch (error) {\n            console.error('Bulk action failed:', error);\n            $('#bulkProgressModal').modal('hide');\n            alert('Bulk action failed: ' + error.message);\n        } finally {\n            this.isProcessing = false;\n        }\n    }\n    \n    validateBulkAction(action) {\n        if (action === 'reject') {\n            const comment = $('#bulkComment').val().trim();\n            if (!comment) {\n                alert('Please provide a reason for rejection.');\n                $('#bulkComment').focus();\n                return false;\n            }\n        }\n        \n        if (action === 'assign') {\n            const assignTo = $('#assignTo').val();\n            if (!assignTo) {\n                alert('Please select a reviewer to assign to.');\n                $('#assignTo').focus();\n                return false;\n            }\n        }\n        \n        if (action === 'status') {\n            const newStatus = $('#newStatus').val();\n            if (!newStatus) {\n                alert('Please select a new status.');\n                $('#newStatus').focus();\n                return false;\n            }\n        }\n        \n        return true;\n    }\n    \n    initializeProgress(action, total) {\n        const actionLabels = {\n            approve: 'Approving',\n            reject: 'Rejecting',\n            assign: 'Assigning',\n            status: 'Updating status for'\n        };\n        \n        $('#progressAction').text(`${actionLabels[action]} applications...`);\n        $('#progressCurrent').text('0');\n        $('#progressTotal').text(total);\n        $('#bulkProgressBar').css('width', '0%').attr('aria-valuenow', 0);\n        $('#estimatedTime').text('Calculating...');\n        $('#progressLog').empty();\n        \n        this.startTime = Date.now();\n    }\n    \n    async processBulkInBatches(action, items, options) {\n        const { batchSize = 5, comment = '', assignTo = '', newStatus = '' } = options;\n        const results = {\n            success: [],\n            errors: [],\n            total: items.length,\n            processed: 0\n        };\n        \n        for (let i = 0; i < items.length; i += batchSize) {\n            const batch = items.slice(i, i + batchSize);\n            \n            try {\n                const response = await fetch(this.bulkActionEndpoint, {\n                    method: 'POST',\n                    headers: {\n                        'Content-Type': 'application/x-www-form-urlencoded',\n                        'X-CSRFToken': this.getCSRFToken()\n                    },\n                    body: new URLSearchParams({\n                        action_type: action,\n                        exchange_ids: batch.join(','),\n                        bulk_comment: comment,\n                        assign_to: assignTo,\n                        new_status: newStatus\n                    })\n                });\n                \n                const data = await response.json();\n                \n                if (data.success) {\n                    results.success.push(...batch);\n                    this.logProgress(`✓ Processed batch of ${batch.length} items`, 'success');\n                } else {\n                    results.errors.push({ items: batch, error: data.error });\n                    this.logProgress(`✗ Failed to process batch: ${data.error}`, 'error');\n                }\n                \n            } catch (error) {\n                results.errors.push({ items: batch, error: error.message });\n                this.logProgress(`✗ Network error for batch: ${error.message}`, 'error');\n            }\n            \n            results.processed += batch.length;\n            this.updateProgress(results.processed, results.total);\n            \n            // Small delay between batches to prevent overwhelming the server\n            await new Promise(resolve => setTimeout(resolve, 200));\n        }\n        \n        return results;\n    }\n    \n    updateProgress(current, total) {\n        const percentage = Math.round((current / total) * 100);\n        $('#progressCurrent').text(current);\n        $('#bulkProgressBar').css('width', `${percentage}%`).attr('aria-valuenow', percentage);\n        \n        // Update estimated time\n        if (current > 0) {\n            const elapsed = Date.now() - this.startTime;\n            const estimated = (elapsed / current) * (total - current);\n            const estimatedSeconds = Math.round(estimated / 1000);\n            $('#estimatedTime').text(`${estimatedSeconds}s remaining`);\n        }\n    }\n    \n    logProgress(message, type = 'info') {\n        const iconMap = {\n            info: 'bi-info-circle text-info',\n            success: 'bi-check-circle text-success',\n            error: 'bi-exclamation-circle text-danger'\n        };\n        \n        const logEntry = `\n            <li class=\"d-flex align-items-center mb-1\">\n                <i class=\"bi ${iconMap[type]} me-2\"></i>\n                <span class=\"small\">${message}</span>\n            </li>\n        `;\n        \n        $('#progressLog').append(logEntry);\n        \n        // Scroll to bottom\n        const logContainer = $('#progressLog')[0];\n        logContainer.scrollTop = logContainer.scrollHeight;\n    }\n    \n    showResultsSummary(results) {\n        const successCount = results.success.length;\n        const errorCount = results.errors.length;\n        const totalCount = results.total;\n        \n        let content = `\n            <div class=\"row g-3 mb-4\">\n                <div class=\"col-md-4\">\n                    <div class=\"card border-success\">\n                        <div class=\"card-body text-center\">\n                            <i class=\"bi bi-check-circle display-6 text-success mb-2\"></i>\n                            <h3 class=\"text-success mb-1\">${successCount}</h3>\n                            <p class=\"mb-0 text-muted\">Successful</p>\n                        </div>\n                    </div>\n                </div>\n                <div class=\"col-md-4\">\n                    <div class=\"card border-danger\">\n                        <div class=\"card-body text-center\">\n                            <i class=\"bi bi-x-circle display-6 text-danger mb-2\"></i>\n                            <h3 class=\"text-danger mb-1\">${errorCount}</h3>\n                            <p class=\"mb-0 text-muted\">Failed</p>\n                        </div>\n                    </div>\n                </div>\n                <div class=\"col-md-4\">\n                    <div class=\"card border-primary\">\n                        <div class=\"card-body text-center\">\n                            <i class=\"bi bi-list-check display-6 text-primary mb-2\"></i>\n                            <h3 class=\"text-primary mb-1\">${totalCount}</h3>\n                            <p class=\"mb-0 text-muted\">Total</p>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        `;\n        \n        if (errorCount > 0) {\n            content += `\n                <div class=\"alert alert-warning\" role=\"alert\">\n                    <h6 class=\"alert-heading\"><i class=\"bi bi-exclamation-triangle me-2\"></i>Some items failed to process</h6>\n                    <ul class=\"mb-0\">\n            `;\n            \n            results.errors.forEach(error => {\n                content += `<li>Items ${error.items.join(', ')}: ${error.error}</li>`;\n            });\n            \n            content += '</ul></div>';\n        }\n        \n        if (successCount > 0) {\n            content += `\n                <div class=\"alert alert-success\" role=\"alert\">\n                    <i class=\"bi bi-check-circle me-2\"></i>\n                    Successfully processed ${successCount} items.\n                </div>\n            `;\n        }\n        \n        $('#resultsContent').html(content);\n        $('#bulkResultsModal').modal('show');\n        \n        // Store results for export\n        this.lastResults = results;\n        \n        // Record action history\n        this.recordActionHistory(results);\n    }\n    \n    recordActionHistory(results) {\n        const historyEntry = {\n            timestamp: new Date().toISOString(),\n            total: results.total,\n            successful: results.success.length,\n            failed: results.errors.length,\n            results: results\n        };\n        \n        this.actionHistory.push(historyEntry);\n        \n        // Keep only last 50 entries\n        if (this.actionHistory.length > 50) {\n            this.actionHistory = this.actionHistory.slice(-50);\n        }\n        \n        // Save to localStorage\n        try {\n            localStorage.setItem('sgii_bulk_action_history', JSON.stringify(this.actionHistory));\n        } catch (e) {\n            console.warn('Failed to save bulk action history:', e);\n        }\n    }\n    \n    exportResults() {\n        if (!this.lastResults) {\n            alert('No results to export.');\n            return;\n        }\n        \n        const csvContent = this.generateResultsCSV(this.lastResults);\n        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });\n        const link = document.createElement('a');\n        \n        if (link.download !== undefined) {\n            const url = URL.createObjectURL(blob);\n            link.setAttribute('href', url);\n            link.setAttribute('download', `bulk_action_results_${new Date().toISOString().split('T')[0]}.csv`);\n            link.style.visibility = 'hidden';\n            document.body.appendChild(link);\n            link.click();\n            document.body.removeChild(link);\n        }\n    }\n    \n    generateResultsCSV(results) {\n        let csv = 'Item ID,Status,Error\\n';\n        \n        results.success.forEach(id => {\n            csv += `${id},Success,\\n`;\n        });\n        \n        results.errors.forEach(error => {\n            error.items.forEach(id => {\n                csv += `${id},Failed,\"${error.error.replace(/\"/g, '\"\"')}\"\\n`;\n            });\n        });\n        \n        return csv;\n    }\n    \n    cancelBulkAction() {\n        // In a real implementation, this would cancel the ongoing requests\n        this.isProcessing = false;\n        $('#bulkProgressModal').modal('hide');\n        alert('Bulk action cancelled.');\n    }\n    \n    getCSRFToken() {\n        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || \n               document.querySelector('meta[name=\"csrf-token\"]')?.getAttribute('content') || '';\n    }\n}\n\n// Global instance variable\nlet sgiiBulkActions = null;\n\n// Auto-initialization function\nfunction initializeSGIIBulkActions(tableId, bulkActionEndpoint) {\n    if (sgiiBulkActions) {\n        console.warn('SGII Bulk Actions already initialized');\n        return sgiiBulkActions;\n    }\n    \n    sgiiBulkActions = new SGIIBulkActions(tableId, bulkActionEndpoint);\n    return sgiiBulkActions;\n}\n\n// Export for module usage\nif (typeof module !== 'undefined' && module.exports) {\n    module.exports = SGIIBulkActions;\n}