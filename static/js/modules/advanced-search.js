/**
 * Advanced Search Module
 * 
 * Provides advanced filtering for programs and applications
 * with debounced AJAX, URL state management, and saved searches
 */

class AdvancedSearch {
    constructor(options = {}) {
        this.options = {
            searchType: 'program', // 'program' or 'application'
            apiEndpoint: '/api/programs/',
            debounceDelay: 300,
            updateUrl: true,
            onResults: null,
            ...options
        };
        
        this.filters = {};
        this.debounceTimer = null;
        this.isLoading = false;
        
        this.init();
    }
    
    /**
     * Initialize search
     */
    init() {
        this.initFromUrl();
        this.attachEventListeners();
    }
    
    /**
     * Initialize filters from URL parameters
     */
    initFromUrl() {
        const params = new URLSearchParams(window.location.search);
        params.forEach((value, key) => {
            if (key !== 'page') {
                this.filters[key] = value;
                
                // Set form field values
                const field = document.querySelector(`[name="${key}"]`);
                if (field) {
                    if (field.type === 'checkbox') {
                        field.checked = value === 'true';
                    } else {
                        field.value = value;
                    }
                }
            }
        });
    }
    
    /**
     * Attach event listeners to search form
     */
    attachEventListeners() {
        // Text inputs and selects
        document.querySelectorAll('.search-filter-input').forEach(input => {
            if (input.type === 'text' || input.tagName === 'SELECT') {
                input.addEventListener('input', (e) => {
                    this.handleFilterChange(e.target.name, e.target.value);
                });
            } else if (input.type === 'checkbox') {
                input.addEventListener('change', (e) => {
                    this.handleFilterChange(e.target.name, e.target.checked);
                });
            } else if (input.type === 'date') {
                input.addEventListener('change', (e) => {
                    this.handleFilterChange(e.target.name, e.target.value);
                });
            }
        });
        
        // Clear filters button
        const clearBtn = document.getElementById('clearFiltersBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearFilters());
        }
        
        // Save search button
        const saveBtn = document.getElementById('saveSearchBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.showSaveSearchModal());
        }
    }
    
    /**
     * Handle filter change with debouncing
     */
    handleFilterChange(name, value) {
        // Update filters
        if (value === '' || value === null || value === false) {
            delete this.filters[name];
        } else {
            this.filters[name] = value;
        }
        
        // Clear existing timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Set new timer
        this.debounceTimer = setTimeout(() => {
            this.performSearch();
        }, this.options.debounceDelay);
    }
    
    /**
     * Perform search with current filters
     */
    async performSearch(page = 1) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            // Build query parameters
            const params = new URLSearchParams(this.filters);
            params.append('page', page);
            
            // Get JWT token
            const token = localStorage.getItem('seim_access_token');
            
            // Make API request
            const response = await fetch(`${this.options.apiEndpoint}?${params}`, {
                headers: token ? {
                    'Authorization': `Bearer ${token}`
                } : {}
            });
            
            if (!response.ok) {
                throw new Error('Search request failed');
            }
            
            const data = await response.json();
            
            // Update URL
            if (this.options.updateUrl) {
                this.updateUrl(params);
            }
            
            // Trigger callback
            if (this.options.onResults) {
                this.options.onResults(data);
            }
            
            return data;
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    /**
     * Clear all filters
     */
    clearFilters() {
        this.filters = {};
        
        // Clear form fields
        document.querySelectorAll('.search-filter-input').forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        
        // Perform search
        this.performSearch();
    }
    
    /**
     * Update URL with current filters
     */
    updateUrl(params) {
        const url = new URL(window.location);
        url.search = params.toString();
        window.history.pushState({}, '', url);
    }
    
    /**
     * Show save search modal
     */
    showSaveSearchModal() {
        const modalHtml = `
            <div class="modal fade" id="saveSearchModal" tabindex="-1" aria-labelledby="saveSearchModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="saveSearchModalLabel">Save Search</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <form id="saveSearchForm">
                                <div class="mb-3">
                                    <label for="searchName" class="form-label">Search Name</label>
                                    <input type="text" class="form-control" id="searchName" required placeholder="e.g., Active Programs in Europe">
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="setAsDefault">
                                    <label class="form-check-label" for="setAsDefault">
                                        Set as default search
                                    </label>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="confirmSaveSearch">Save Search</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body if it doesn't exist
        let modal = document.getElementById('saveSearchModal');
        if (!modal) {
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('saveSearchModal');
        }
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Handle save
        document.getElementById('confirmSaveSearch').onclick = () => {
            this.saveSearch();
            bsModal.hide();
        };
    }
    
    /**
     * Save current search
     */
    async saveSearch() {
        const name = document.getElementById('searchName').value;
        const isDefault = document.getElementById('setAsDefault').checked;
        
        if (!name) {
            this.showError('Please enter a search name');
            return;
        }
        
        try {
            const token = localStorage.getItem('seim_access_token');
            
            const response = await fetch('/api/saved-searches/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    search_type: this.options.searchType,
                    filters: this.filters,
                    is_default: isDefault
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to save search');
            }
            
            this.showSuccess('Search saved successfully');
            
            // Refresh saved searches list
            if (window.savedSearchesManager) {
                window.savedSearchesManager.loadSavedSearches();
            }
            
        } catch (error) {
            console.error('Error saving search:', error);
            this.showError('Failed to save search');
        }
    }
    
    /**
     * Apply saved search
     */
    applySavedSearch(filters) {
        this.filters = { ...filters };
        
        // Update form fields
        document.querySelectorAll('.search-filter-input').forEach(input => {
            const value = this.filters[input.name];
            if (value !== undefined) {
                if (input.type === 'checkbox') {
                    input.checked = value === 'true' || value === true;
                } else {
                    input.value = value;
                }
            } else {
                if (input.type === 'checkbox') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            }
        });
        
        // Perform search
        this.performSearch();
    }
    
    /**
     * Export results to CSV
     */
    async exportToCsv() {
        try {
            // Get all results (no pagination)
            const params = new URLSearchParams(this.filters);
            params.append('page_size', '1000'); // Large page size
            
            const token = localStorage.getItem('seim_access_token');
            const response = await fetch(`${this.options.apiEndpoint}?${params}`, {
                headers: token ? {
                    'Authorization': `Bearer ${token}`
                } : {}
            });
            
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const data = await response.json();
            const results = data.results || [];
            
            if (results.length === 0) {
                this.showError('No results to export');
                return;
            }
            
            // Convert to CSV
            const csv = this.convertToCsv(results);
            
            // Download
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.options.searchType}_search_results_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showSuccess('Results exported successfully');
            
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Export failed');
        }
    }
    
    /**
     * Convert results to CSV
     */
    convertToCsv(results) {
        if (results.length === 0) return '';
        
        // Get headers from first result
        const headers = Object.keys(results[0]);
        
        // Build CSV
        let csv = headers.join(',') + '\n';
        
        results.forEach(result => {
            const row = headers.map(header => {
                let value = result[header];
                
                // Handle nested objects and arrays
                if (typeof value === 'object' && value !== null) {
                    value = JSON.stringify(value);
                }
                
                // Escape quotes and wrap in quotes if contains comma
                if (typeof value === 'string') {
                    value = value.replace(/"/g, '""');
                    if (value.includes(',') || value.includes('\n')) {
                        value = `"${value}"`;
                    }
                }
                
                return value;
            });
            
            csv += row.join(',') + '\n';
        });
        
        return csv;
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const loader = document.getElementById('searchLoader');
        if (loader) {
            loader.classList.remove('d-none');
        }
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        const loader = document.getElementById('searchLoader');
        if (loader) {
            loader.classList.add('d-none');
        }
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        if (window.toastNotifications) {
            window.toastNotifications.success('Success', message);
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        if (window.toastNotifications) {
            window.toastNotifications.error('Error', message);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedSearch;
}

// Make available globally
window.AdvancedSearch = AdvancedSearch;

