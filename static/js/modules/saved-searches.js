/**
 * Saved Searches Manager
 * 
 * Manages saved searches dropdown and CRUD operations
 */

class SavedSearchesManager {
    constructor(searchType = 'program') {
        this.searchType = searchType;
        this.savedSearches = [];
        this.dropdownElement = null;
        
        this.init();
    }
    
    /**
     * Initialize saved searches
     */
    init() {
        this.dropdownElement = document.getElementById('savedSearchesDropdown');
        if (this.dropdownElement) {
            this.loadSavedSearches();
        }
    }
    
    /**
     * Load saved searches from API
     */
    async loadSavedSearches() {
        try {
            const token = localStorage.getItem('seim_access_token');
            const response = await fetch(`/api/saved-searches/?search_type=${this.searchType}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to load saved searches');
            }
            
            const data = await response.json();
            this.savedSearches = data.results || [];
            
            this.render();
            
        } catch (error) {
            console.error('Error loading saved searches:', error);
        }
    }
    
    /**
     * Render saved searches dropdown
     */
    render() {
        if (!this.dropdownElement) return;
        
        const menu = this.dropdownElement.querySelector('.dropdown-menu');
        if (!menu) return;
        
        // Clear existing items
        menu.innerHTML = '';
        
        if (this.savedSearches.length === 0) {
            menu.innerHTML = '<li><span class="dropdown-item text-muted">No saved searches</span></li>';
            return;
        }
        
        // Add saved searches
        this.savedSearches.forEach(search => {
            const item = document.createElement('li');
            item.innerHTML = `
                <a class="dropdown-item d-flex justify-content-between align-items-center" href="#" data-search-id="${search.id}">
                    <span>
                        ${search.is_default ? '<i class="bi bi-star-fill text-warning"></i> ' : ''}
                        ${this.escapeHtml(search.name)}
                    </span>
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-sm btn-link text-warning star-btn" title="${search.is_default ? 'Remove default' : 'Set as default'}" data-search-id="${search.id}">
                            <i class="bi bi-star${search.is_default ? '-fill' : ''}"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-link text-danger delete-btn" title="Delete" data-search-id="${search.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </a>
            `;
            
            menu.appendChild(item);
            
            // Attach event listeners
            const link = item.querySelector('a');
            link.addEventListener('click', (e) => {
                e.preventDefault();
                if (!e.target.closest('.btn')) {
                    this.applySearch(search.id);
                }
            });
            
            const starBtn = item.querySelector('.star-btn');
            starBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleDefault(search.id);
            });
            
            const deleteBtn = item.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.confirmDelete(search.id, search.name);
            });
        });
        
        // Add divider and manage option
        menu.innerHTML += `
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item text-primary" href="#" id="manageSearchesLink">
                <i class="bi bi-gear"></i> Manage Searches
            </a></li>
        `;
        
        // Attach manage link
        const manageLink = menu.querySelector('#manageSearchesLink');
        if (manageLink) {
            manageLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showManageModal();
            });
        }
    }
    
    /**
     * Apply saved search
     */
    async applySearch(searchId) {
        try {
            const token = localStorage.getItem('seim_access_token');
            const response = await fetch(`/api/saved-searches/${searchId}/apply/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to apply search');
            }
            
            const data = await response.json();
            
            // Apply filters using AdvancedSearch
            if (window.advancedSearch) {
                window.advancedSearch.applySavedSearch(data.filters);
            }
            
            this.showSuccess(`Applied search: ${data.name}`);
            
        } catch (error) {
            console.error('Error applying search:', error);
            this.showError('Failed to apply search');
        }
    }
    
    /**
     * Toggle default status
     */
    async toggleDefault(searchId) {
        try {
            const token = localStorage.getItem('seim_access_token');
            const response = await fetch(`/api/saved-searches/${searchId}/set_default/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to set default');
            }
            
            // Reload searches
            await this.loadSavedSearches();
            
        } catch (error) {
            console.error('Error setting default:', error);
            this.showError('Failed to set default');
        }
    }
    
    /**
     * Confirm and delete search
     */
    async confirmDelete(searchId, searchName) {
        if (!confirm(`Are you sure you want to delete "${searchName}"?`)) {
            return;
        }
        
        await this.deleteSearch(searchId);
    }
    
    /**
     * Delete search
     */
    async deleteSearch(searchId) {
        try {
            const token = localStorage.getItem('seim_access_token');
            const response = await fetch(`/api/saved-searches/${searchId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete search');
            }
            
            this.showSuccess('Search deleted successfully');
            
            // Reload searches
            await this.loadSavedSearches();
            
        } catch (error) {
            console.error('Error deleting search:', error);
            this.showError('Failed to delete search');
        }
    }
    
    /**
     * Show manage searches modal
     */
    showManageModal() {
        const modalHtml = `
            <div class="modal fade" id="manageSearchesModal" tabindex="-1" aria-labelledby="manageSearchesModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="manageSearchesModalLabel">Manage Saved Searches</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="list-group" id="manageSearchesList">
                                ${this.renderManageList()}
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body if it doesn't exist
        let modal = document.getElementById('manageSearchesModal');
        if (modal) {
            modal.remove();
        }
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        modal = document.getElementById('manageSearchesModal');
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Attach event listeners
        this.attachManageListeners();
    }
    
    /**
     * Render manage searches list
     */
    renderManageList() {
        if (this.savedSearches.length === 0) {
            return '<p class="text-muted text-center py-4">No saved searches</p>';
        }
        
        return this.savedSearches.map(search => `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">
                            ${search.is_default ? '<i class="bi bi-star-fill text-warning"></i> ' : ''}
                            ${this.escapeHtml(search.name)}
                        </h6>
                        <small class="text-muted">${Object.keys(search.filters).length} filters applied</small>
                    </div>
                    <div class="btn-group">
                        <button type="button" class="btn btn-sm btn-outline-primary apply-btn" data-search-id="${search.id}">
                            <i class="bi bi-check-circle"></i> Apply
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-warning star-btn" data-search-id="${search.id}">
                            <i class="bi bi-star${search.is_default ? '-fill' : ''}"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger delete-btn" data-search-id="${search.id}" data-search-name="${this.escapeHtml(search.name)}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    /**
     * Attach listeners to manage modal
     */
    attachManageListeners() {
        // Apply buttons
        document.querySelectorAll('.apply-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const searchId = e.currentTarget.dataset.searchId;
                await this.applySearch(searchId);
                bootstrap.Modal.getInstance(document.getElementById('manageSearchesModal')).hide();
            });
        });
        
        // Star buttons
        document.querySelectorAll('.star-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const searchId = e.currentTarget.dataset.searchId;
                await this.toggleDefault(searchId);
                // Refresh modal content
                document.getElementById('manageSearchesList').innerHTML = this.renderManageList();
                this.attachManageListeners();
            });
        });
        
        // Delete buttons
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const searchId = e.currentTarget.dataset.searchId;
                const searchName = e.currentTarget.dataset.searchName;
                await this.confirmDelete(searchId, searchName);
                // Refresh modal content
                document.getElementById('manageSearchesList').innerHTML = this.renderManageList();
                this.attachManageListeners();
            });
        });
    }
    
    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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
    module.exports = SavedSearchesManager;
}

// Make available globally
window.SavedSearchesManager = SavedSearchesManager;

