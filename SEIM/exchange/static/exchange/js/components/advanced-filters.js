/**
 * Advanced Filtering System for SGII DataTables
 * Provides multi-criteria filtering, saved filter presets, and enhanced user experience
 */

class SGIIAdvancedFilters {
    constructor(tableId, apiEndpoint, filterConfig = {}) {
        this.table = $(tableId).DataTable();
        this.tableId = tableId;
        this.apiEndpoint = apiEndpoint;
        this.filterConfig = {
            enableDateRange: true,
            enableMultiSelect: true,
            enableSavedPresets: true,
            autoApply: false,
            debounceDelay: 300,
            ...filterConfig
        };
        
        this.activeFilters = {};
        this.savedFilters = this.loadSavedFilters();
        this.debounceTimer = null;
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        this.buildFilterUI();
        this.bindEvents();
        this.loadUserPreferences();
        this.initializeMultiSelect();
        this.isInitialized = true;
        
        console.log('SGII Advanced Filters initialized for table:', this.tableId);
    }
    
    buildFilterUI() {
        // Create advanced filter panel if it doesn't exist
        const existingPanel = document.getElementById('advancedFiltersPanel');
        if (existingPanel) {
            return; // Already exists, don't recreate
        }
        
        const filterPanel = this.createAdvancedFilterPanel();
        
        // Insert the panel before the DataTable
        const tableWrapper = $(this.tableId).closest('.dataTables_wrapper');
        tableWrapper.before(filterPanel);
    }
    
    createAdvancedFilterPanel() {
        return `
        <div id="advancedFiltersPanel" class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-transparent d-flex justify-content-between align-items-center">
                <h6 class="mb-0">
                    <i class="bi bi-funnel me-2"></i>Advanced Filters
                </h6>
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-outline-primary" onclick="sgiiFilters.saveFilterPreset()">
                        <i class="bi bi-bookmark-plus me-1"></i>Save Preset
                    </button>
                    <button type="button" class="btn btn-outline-secondary" onclick="sgiiFilters.managePresets()">
                        <i class="bi bi-gear"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick="sgiiFilters.clearAllFilters()">
                        <i class="bi bi-x-circle me-1"></i>Clear All
                    </button>
                </div>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <!-- Date Range Filter -->
                    <div class="col-md-3">
                        <label class="form-label small">Date Range</label>
                        <div class="input-group input-group-sm">
                            <input type="date" class="form-control" id="dateFrom" name="date_from">
                            <span class="input-group-text">to</span>
                            <input type="date" class="form-control" id="dateTo" name="date_to">
                        </div>
                    </div>
                    
                    <!-- Status Multi-Select -->
                    <div class="col-md-3">
                        <label class="form-label small">Status (Multiple)</label>
                        <select class="form-select form-select-sm" id="statusFilter" multiple>
                            <option value="DRAFT">Draft</option>
                            <option value="SUBMITTED">Submitted</option>
                            <option value="UNDER_REVIEW">Under Review</option>
                            <option value="APPROVED">Approved</option>
                            <option value="REJECTED">Rejected</option>
                            <option value="COMPLETED">Completed</option>
                        </select>
                    </div>
                    
                    <!-- Country Multi-Select -->
                    <div class="col-md-3">
                        <label class="form-label small">Countries (Multiple)</label>
                        <select class="form-select form-select-sm" id="countryFilter" multiple>
                            <option value="USA">United States</option>
                            <option value="UK">United Kingdom</option>
                            <option value="DE">Germany</option>
                            <option value="FR">France</option>
                            <option value="JP">Japan</option>
                            <option value="AU">Australia</option>
                            <option value="CA">Canada</option>
                            <option value="IT">Italy</option>
                            <option value="ES">Spain</option>
                            <option value="NL">Netherlands</option>
                        </select>
                    </div>
                    
                    <!-- Quick Presets -->
                    <div class="col-md-3">
                        <label class="form-label small">Quick Presets</label>
                        <select class="form-select form-select-sm" id="filterPresets">
                            <option value="">Select Preset...</option>
                            <option value="pending">Pending Review</option>
                            <option value="approved_recent">Recently Approved</option>
                            <option value="overdue">Overdue Applications</option>
                            <option value="this_month">This Month</option>
                            <option value="last_30_days">Last 30 Days</option>
                        </select>
                    </div>
                </div>
                
                <!-- Search and Apply Row -->
                <div class="row g-3 mt-2">
                    <div class="col-md-6">
                        <label class="form-label small">Global Search</label>
                        <div class="input-group input-group-sm">
                            <span class="input-group-text">
                                <i class="bi bi-search"></i>
                            </span>
                            <input type="text" class="form-control" id="globalSearch" 
                                   placeholder="Search across all fields...">
                        </div>
                    </div>
                    <div class="col-md-6 d-flex align-items-end">
                        <div class="btn-group w-100">
                            <button type="button" class="btn btn-primary btn-sm" onclick="sgiiFilters.applyAdvancedFilters()">
                                <i class="bi bi-search me-1"></i>Apply Filters
                            </button>
                            <button type="button" class="btn btn-outline-secondary btn-sm" onclick="sgiiFilters.toggleAutoApply()">
                                <i class="bi bi-lightning me-1"></i>
                                <span id="autoApplyText">Auto Apply: Off</span>
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Active Filters Display -->
                <div id="activeFiltersDisplay" class="mt-3 d-none">
                    <div class="d-flex align-items-center flex-wrap gap-2">
                        <small class="text-muted me-2">Active Filters:</small>
                        <div id="activeFilterTags"></div>
                    </div>
                </div>
            </div>
        </div>
        `;
    }
    
    bindEvents() {
        // Date range inputs
        $('#dateFrom, #dateTo').on('change', () => {
            if (this.filterConfig.autoApply) {
                this.debounceApplyFilters();
            }
        });
        
        // Multi-select dropdowns
        $('#statusFilter, #countryFilter').on('change', () => {
            if (this.filterConfig.autoApply) {
                this.debounceApplyFilters();
            }
        });
        
        // Global search with debounce
        $('#globalSearch').on('input', () => {
            this.debounceApplyFilters();
        });
        
        // Quick presets
        $('#filterPresets').on('change', (e) => {
            const preset = e.target.value;
            if (preset) {
                this.applyQuickPreset(preset);
            }
        });
        
        // Auto-apply toggle
        this.updateAutoApplyUI();
    }
    
    debounceApplyFilters() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.applyAdvancedFilters();
        }, this.filterConfig.debounceDelay);
    }
    
    applyAdvancedFilters() {
        const filters = this.collectFilterValues();
        this.activeFilters = filters;
        
        // Update the DataTable with new filters
        this.table.ajax.url(this.buildFilteredUrl(filters)).load();
        
        // Update active filters display
        this.updateActiveFiltersDisplay(filters);
        
        // Save filter state
        this.saveFilterState(filters);
        
        console.log('Applied advanced filters:', filters);
    }
    
    collectFilterValues() {
        const filters = {};
        
        // Date range
        const dateFrom = $('#dateFrom').val();
        const dateTo = $('#dateTo').val();
        if (dateFrom || dateTo) {
            filters.date_range = { start: dateFrom, end: dateTo };
        }
        
        // Status multi-select
        const statuses = $('#statusFilter').val();
        if (statuses && statuses.length > 0) {
            filters.statuses = statuses;
        }
        
        // Country multi-select
        const countries = $('#countryFilter').val();
        if (countries && countries.length > 0) {
            filters.countries = countries;
        }
        
        // Global search
        const search = $('#globalSearch').val().trim();
        if (search) {
            filters.global_search = search;
        }
        
        return filters;
    }
    
    buildFilteredUrl(filters) {
        const url = new URL(this.apiEndpoint, window.location.origin);
        url.searchParams.set('advanced_filters', JSON.stringify(filters));
        return url.toString();
    }
    
    updateActiveFiltersDisplay(filters) {
        const display = $('#activeFiltersDisplay');
        const tagsContainer = $('#activeFilterTags');
        
        if (Object.keys(filters).length === 0) {
            display.addClass('d-none');
            return;
        }
        
        display.removeClass('d-none');
        tagsContainer.empty();
        
        // Create filter tags
        Object.entries(filters).forEach(([key, value]) => {
            const tag = this.createFilterTag(key, value);
            if (tag) {
                tagsContainer.append(tag);
            }
        });
    }
    
    createFilterTag(key, value) {
        let label = '';
        let displayValue = '';
        
        switch (key) {
            case 'date_range':
                label = 'Date Range';
                displayValue = `${value.start || 'Start'} to ${value.end || 'End'}`;
                break;
            case 'statuses':
                label = 'Status';
                displayValue = value.length > 3 ? `${value.length} selected` : value.join(', ');
                break;
            case 'countries':
                label = 'Countries';
                displayValue = value.length > 3 ? `${value.length} selected` : value.join(', ');
                break;
            case 'global_search':
                label = 'Search';
                displayValue = value;
                break;
            default:
                return null;
        }
        
        return `
            <span class="badge bg-primary-subtle text-primary border border-primary-subtle me-1 mb-1">
                ${label}: ${displayValue}
                <button type="button" class="btn-close btn-close-sm ms-1" 
                        onclick="sgiiFilters.removeFilter('${key}')"
                        aria-label="Remove filter"></button>
            </span>
        `;
    }
    
    removeFilter(filterKey) {
        // Remove from UI
        switch (filterKey) {
            case 'date_range':
                $('#dateFrom, #dateTo').val('');
                break;
            case 'statuses':
                $('#statusFilter').val([]).trigger('change');
                break;
            case 'countries':
                $('#countryFilter').val([]).trigger('change');
                break;
            case 'global_search':
                $('#globalSearch').val('');
                break;
        }
        
        // Reapply filters
        this.applyAdvancedFilters();
    }
    
    clearAllFilters() {
        // Clear all filter inputs
        $('#dateFrom, #dateTo, #globalSearch').val('');
        $('#statusFilter, #countryFilter').val([]).trigger('change');
        $('#filterPresets').val('');
        
        // Reset active filters
        this.activeFilters = {};
        
        // Reload table with no filters
        this.table.ajax.url(this.apiEndpoint).load();
        
        // Update display
        this.updateActiveFiltersDisplay({});
        
        // Clear saved state
        this.clearFilterState();
        
        console.log('Cleared all advanced filters');
    }
    
    applyQuickPreset(presetName) {
        const presets = {
            pending: {
                statuses: ['SUBMITTED', 'UNDER_REVIEW']
            },
            approved_recent: {
                statuses: ['APPROVED'],
                date_range: {
                    start: this.getDateDaysAgo(30),
                    end: this.getTodayDate()
                }
            },
            overdue: {
                statuses: ['SUBMITTED'],
                date_range: {
                    end: this.getDateDaysAgo(14)
                }
            },
            this_month: {
                date_range: {
                    start: this.getMonthStartDate(),
                    end: this.getTodayDate()
                }
            },
            last_30_days: {
                date_range: {
                    start: this.getDateDaysAgo(30),
                    end: this.getTodayDate()
                }
            }
        };
        
        const preset = presets[presetName];
        if (preset) {
            this.applyFilterPreset(preset);
        }
    }
    
    applyFilterPreset(preset) {
        // Clear existing filters first
        this.clearAllFilters();
        
        // Apply preset values
        if (preset.date_range) {
            $('#dateFrom').val(preset.date_range.start || '');
            $('#dateTo').val(preset.date_range.end || '');
        }
        
        if (preset.statuses) {
            $('#statusFilter').val(preset.statuses).trigger('change');
        }
        
        if (preset.countries) {
            $('#countryFilter').val(preset.countries).trigger('change');
        }
        
        if (preset.global_search) {
            $('#globalSearch').val(preset.global_search);
        }
        
        // Apply the filters
        this.applyAdvancedFilters();
    }
    
    saveFilterPreset() {
        const filters = this.collectFilterValues();
        if (Object.keys(filters).length === 0) {
            alert('No filters to save. Please apply some filters first.');
            return;
        }
        
        const name = prompt('Enter a name for this filter preset:');
        if (name && name.trim()) {
            this.savedFilters[name.trim()] = filters;
            this.saveSavedFilters();
            this.updatePresetsDropdown();
            alert(`Filter preset "${name.trim()}" saved successfully!`);
        }
    }
    
    managePresets() {
        // Create a simple preset management modal
        const presetsList = Object.keys(this.savedFilters).map(name => 
            `<li class="list-group-item d-flex justify-content-between align-items-center">
                ${name}
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="sgiiFilters.loadPreset('${name}')">Load</button>
                    <button class="btn btn-outline-danger" onclick="sgiiFilters.deletePreset('${name}')">Delete</button>
                </div>
            </li>`
        ).join('');
        
        const modalHtml = `
            <div class="modal fade" id="presetsModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Manage Filter Presets</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${presetsList ? 
                                `<ul class="list-group">${presetsList}</ul>` : 
                                '<p class="text-muted">No saved presets found.</p>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        $('#presetsModal').remove();
        
        // Add and show modal
        $('body').append(modalHtml);
        $('#presetsModal').modal('show');
    }
    
    loadPreset(name) {
        const preset = this.savedFilters[name];
        if (preset) {
            this.applyFilterPreset(preset);
            $('#presetsModal').modal('hide');
        }
    }
    
    deletePreset(name) {
        if (confirm(`Are you sure you want to delete the preset "${name}"?`)) {
            delete this.savedFilters[name];
            this.saveSavedFilters();
            $('#presetsModal').modal('hide');
            this.managePresets(); // Refresh the modal
        }
    }
    
    toggleAutoApply() {
        this.filterConfig.autoApply = !this.filterConfig.autoApply;
        this.updateAutoApplyUI();
        this.saveUserPreferences();
    }
    
    updateAutoApplyUI() {
        const text = this.filterConfig.autoApply ? 'Auto Apply: On' : 'Auto Apply: Off';
        $('#autoApplyText').text(text);
    }
    
    // Utility methods for date handling
    getTodayDate() {
        return new Date().toISOString().split('T')[0];
    }
    
    getDateDaysAgo(days) {
        const date = new Date();
        date.setDate(date.getDate() - days);
        return date.toISOString().split('T')[0];
    }
    
    getMonthStartDate() {
        const date = new Date();
        date.setDate(1);
        return date.toISOString().split('T')[0];
    }
    
    // Local storage methods
    loadSavedFilters() {
        try {
            const saved = localStorage.getItem('sgii_saved_filters');
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            console.warn('Error loading saved filters:', e);
            return {};
        }
    }
    
    saveSavedFilters() {
        try {
            localStorage.setItem('sgii_saved_filters', JSON.stringify(this.savedFilters));
        } catch (e) {
            console.warn('Error saving filters:', e);
        }
    }
    
    loadUserPreferences() {
        try {
            const prefs = localStorage.getItem('sgii_filter_preferences');
            if (prefs) {
                const parsed = JSON.parse(prefs);
                this.filterConfig.autoApply = parsed.autoApply || false;
            }
        } catch (e) {
            console.warn('Error loading user preferences:', e);
        }
    }
    
    saveUserPreferences() {
        try {
            const prefs = {
                autoApply: this.filterConfig.autoApply
            };
            localStorage.setItem('sgii_filter_preferences', JSON.stringify(prefs));
        } catch (e) {
            console.warn('Error saving user preferences:', e);
        }
    }
    
    saveFilterState(filters) {
        try {
            localStorage.setItem('sgii_current_filters', JSON.stringify(filters));
        } catch (e) {
            console.warn('Error saving filter state:', e);
        }
    }
    
    clearFilterState() {
        try {
            localStorage.removeItem('sgii_current_filters');
        } catch (e) {
            console.warn('Error clearing filter state:', e);
        }
    }
    
    initializeMultiSelect() {
        // Initialize multi-select dropdowns with better UX
        $('#statusFilter, #countryFilter').each(function() {
            const select = $(this);
            const placeholder = select.attr('id') === 'statusFilter' ? 
                'Select statuses...' : 'Select countries...';
            
            // Add a placeholder option if not exists
            if (select.find('option[value=""]').length === 0) {
                select.prepend(`<option value="" disabled>${placeholder}</option>`);
            }
        });
    }
    
    updatePresetsDropdown() {
        const presetsDropdown = $('#filterPresets');
        const currentOptions = presetsDropdown.find('option[data-custom="true"]');
        currentOptions.remove();
        
        // Add saved presets to dropdown
        Object.keys(this.savedFilters).forEach(name => {
            presetsDropdown.append(`<option value="custom_${name}" data-custom="true">${name} (Custom)</option>`);
        });
    }
}

// Global instance variable for easy access
let sgiiFilters = null;

// Auto-initialization function
function initializeSGIIAdvancedFilters(tableId, apiEndpoint, config = {}) {
    if (sgiiFilters) {
        console.warn('SGII Advanced Filters already initialized');
        return sgiiFilters;
    }
    
    sgiiFilters = new SGIIAdvancedFilters(tableId, apiEndpoint, config);
    return sgiiFilters;
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SGIIAdvancedFilters;
}
