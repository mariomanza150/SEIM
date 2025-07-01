/**
 * SGII Phase 3 Integration Script
 * Initializes and coordinates all Phase 3 DataTables enhancements
 */

class SGIIPhase3Integration {
    constructor(config = {}) {
        this.config = {
            tableId: '#exchangesTable',
            apiEndpoints: {
                exchanges: '/api/exchanges-datatable/',
                bulkActions: '/api/bulk-actions/',
                globalSearch: '/api/global-search/',
                websocket: 'ws://localhost:8000/ws/exchanges/'
            },
            features: {
                advancedFilters: true,
                bulkActions: true,
                keyboardNavigation: true,
                realtimeUpdates: false, // Enable when WebSocket is available
                globalSearch: true,
                animations: true,
                caching: true
            },
            ...config
        };
        
        this.components = {};
        this.isInitialized = false;
        
        console.log('SGII Phase 3 Integration starting...', this.config);
    }
    
    async init() {
        if (this.isInitialized) {
            console.warn('SGII Phase 3 already initialized');
            return;
        }
        
        try {
            // Initialize core components in order
            await this.initializeCore();
            await this.initializeAdvancedFilters();
            await this.initializeBulkActions();
            await this.initializeKeyboardNavigation();
            await this.initializeGlobalSearch();
            await this.initializeRealtimeUpdates();
            
            // Setup inter-component communication
            this.setupComponentIntegration();
            
            // Apply animations and styling
            this.applyEnhancements();
            
            // Setup event listeners
            this.bindGlobalEvents();
            
            this.isInitialized = true;
            console.log('✅ SGII Phase 3 Integration completed successfully');
            
            // Show welcome message
            this.showWelcomeNotification();
            
        } catch (error) {
            console.error('❌ SGII Phase 3 Integration failed:', error);
            this.showErrorNotification(error.message);
        }
    }
    
    async initializeCore() {
        console.log('🔧 Initializing core DataTables...');
        
        // Ensure DataTables is properly configured
        if (!$(this.config.tableId).length) {
            throw new Error(`Table ${this.config.tableId} not found`);
        }
        
        // Verify DataTables initialization
        if (!$.fn.DataTable.isDataTable(this.config.tableId)) {
            throw new Error('DataTables not initialized on table');
        }
        
        this.components.dataTable = $(this.config.tableId).DataTable();
        console.log('✅ Core DataTables initialized');
    }
    
    async initializeAdvancedFilters() {
        if (!this.config.features.advancedFilters) {
            console.log('⏭️  Advanced Filters disabled');
            return;
        }
        
        console.log('🔍 Initializing Advanced Filters...');
        
        try {
            // Initialize advanced filters component
            this.components.advancedFilters = initializeSGIIAdvancedFilters(
                this.config.tableId,
                this.config.apiEndpoints.exchanges,
                {
                    enableDateRange: true,
                    enableMultiSelect: true,
                    enableSavedPresets: true,
                    autoApply: false,
                    debounceDelay: 300
                }
            );
            
            // Show advanced filters panel
            this.showAdvancedFiltersPanel();
            
            console.log('✅ Advanced Filters initialized');
        } catch (error) {
            console.warn('⚠️  Advanced Filters initialization failed:', error);
        }
    }
    
    async initializeBulkActions() {
        if (!this.config.features.bulkActions) {
            console.log('⏭️  Bulk Actions disabled');
            return;
        }
        
        console.log('⚡ Initializing Bulk Actions...');
        
        try {
            // Initialize bulk actions component
            this.components.bulkActions = initializeSGIIBulkActions(
                this.config.tableId,
                this.config.apiEndpoints.bulkActions
            );
            
            console.log('✅ Bulk Actions initialized');
        } catch (error) {
            console.warn('⚠️  Bulk Actions initialization failed:', error);
        }
    }
    
    async initializeKeyboardNavigation() {
        if (!this.config.features.keyboardNavigation) {
            console.log('⏭️  Keyboard Navigation disabled');
            return;
        }
        
        console.log('⌨️  Initializing Keyboard Navigation...');
        
        try {
            // Initialize keyboard navigation component
            this.components.keyboardNavigation = initializeSGIIKeyboardNavigation(
                this.config.tableId,
                {
                    enableCellNavigation: true,
                    enableRowSelection: true,
                    enableQuickActions: true,
                    showHelp: true
                }
            );
            
            console.log('✅ Keyboard Navigation initialized');
        } catch (error) {
            console.warn('⚠️  Keyboard Navigation initialization failed:', error);
        }
    }
    
    async initializeGlobalSearch() {
        if (!this.config.features.globalSearch) {
            console.log('⏭️  Global Search disabled');
            return;
        }
        
        console.log('🔎 Initializing Global Search...');
        
        try {
            // Initialize global search component
            this.components.globalSearch = initializeSGIIGlobalSearch({
                enableHistory: true,
                enableSuggestions: true,
                enableCache: true,
                enableQueryBuilder: true
            });
            
            console.log('✅ Global Search initialized');
        } catch (error) {
            console.warn('⚠️  Global Search initialization failed:', error);
        }
    }
    
    async initializeRealtimeUpdates() {
        if (!this.config.features.realtimeUpdates) {
            console.log('⏭️  Real-time Updates disabled');
            return;
        }
        
        console.log('🔄 Initializing Real-time Updates...');
        
        try {
            // Initialize real-time updates component
            this.components.realtimeUpdates = initializeSGIIRealtimeUpdates(
                this.config.tableId,
                this.config.apiEndpoints.websocket,
                {
                    enableHeartbeat: true,
                    enableNotifications: true,
                    enableVisualFeedback: true
                }
            );
            
            console.log('✅ Real-time Updates initialized');
        } catch (error) {
            console.warn('⚠️  Real-time Updates initialization failed:', error);
        }
    }
    
    showAdvancedFiltersPanel() {
        // Create toggle button for advanced filters
        const toggleButton = `
            <button type="button" 
                    id="advancedFiltersToggle" 
                    class="btn btn-outline-secondary btn-sm me-2"
                    onclick="sgiiPhase3.toggleAdvancedFilters()">
                <i class="bi bi-funnel me-1"></i>Advanced Filters
            </button>
        `;
        
        // Add toggle button to DataTables buttons container
        const buttonsContainer = $('.dt-buttons');
        if (buttonsContainer.length) {
            buttonsContainer.prepend(toggleButton);
        } else {
            // Add to table wrapper if no buttons container
            $(this.config.tableId).closest('.dataTables_wrapper').prepend(toggleButton);
        }
        
        // Include the advanced filters panel template
        const tableWrapper = $(this.config.tableId).closest('.dataTables_wrapper');
        if (!$('#advancedFiltersPanel').length) {
            fetch('/exchange/templates/includes/advanced_filters_panel.html')
                .then(response => response.text())
                .then(html => {
                    tableWrapper.before(html);
                })
                .catch(error => {
                    console.warn('Could not load advanced filters panel:', error);
                });
        }
    }
    
    setupComponentIntegration() {
        console.log('🔗 Setting up component integration...');
        
        // Advanced Filters <-> DataTable integration
        if (this.components.advancedFilters) {
            // Update DataTable when filters change
            this.components.advancedFilters.onFiltersChanged = (filters) => {
                if (this.components.bulkActions) {
                    this.components.bulkActions.clearSelection();
                }
            };
        }
        
        // Bulk Actions <-> DataTable integration
        if (this.components.bulkActions) {
            // Refresh table after bulk actions
            this.components.bulkActions.onActionComplete = () => {
                this.components.dataTable.ajax.reload(null, false);
            };
        }
        
        // Keyboard Navigation <-> All components integration
        if (this.components.keyboardNavigation) {
            // Integrate with other components
            this.components.keyboardNavigation.onQuickSearch = () => {
                if (this.components.globalSearch) {
                    $('#globalSearchModal').modal('show');
                }
            };
        }
        
        // Real-time Updates <-> All components integration
        if (this.components.realtimeUpdates) {
            // Update other components when data changes
            this.components.realtimeUpdates.onDataUpdate = () => {
                // Update filters if they exist
                if (this.components.advancedFilters) {
                    this.components.advancedFilters.refreshOptions();
                }
            };
        }
        
        console.log('✅ Component integration completed');
    }
    
    applyEnhancements() {
        console.log('🎨 Applying visual enhancements...');
        
        if (this.config.features.animations) {
            // Ensure animations CSS is loaded
            if (!document.getElementById('datatables-animations-css')) {
                const link = document.createElement('link');
                link.id = 'datatables-animations-css';
                link.rel = 'stylesheet';
                link.href = '/static/css/datatables-animations.css';
                document.head.appendChild(link);
            }
            
            // Add animation classes to table
            $(this.config.tableId).addClass('sgii-enhanced-table');
        }
        
        // Apply professional styling
        this.applyProfessionalStyling();
        
        console.log('✅ Visual enhancements applied');
    }
    
    applyProfessionalStyling() {
        // Enhanced table styling
        $(this.config.tableId).closest('.dataTables_wrapper').addClass('sgii-datatable-wrapper');
        
        // Improve pagination styling
        $('.dataTables_paginate .paginate_button').addClass('sgii-page-button');
        
        // Enhanced search styling
        $('.dataTables_filter input').addClass('form-control-sm');
        $('.dataTables_length select').addClass('form-select-sm');
        
        // Add loading overlay improvements
        $('.dataTables_processing').addClass('sgii-processing');
    }
    
    bindGlobalEvents() {
        console.log('🔧 Binding global events...');
        
        // Window resize handler
        $(window).on('resize.sgii', this.debounce(() => {
            if (this.components.dataTable) {
                this.components.dataTable.columns.adjust().responsive.recalc();
            }
        }, 250));
        
        // Page visibility handler
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseComponents();
            } else {
                this.resumeComponents();
            }
        });
        
        // Error handling
        window.addEventListener('error', (e) => {
            if (e.error && e.error.message && e.error.message.includes('SGII')) {
                console.error('SGII Error caught:', e.error);
                this.handleComponentError(e.error);
            }
        });
        
        console.log('✅ Global events bound');
    }
    
    pauseComponents() {
        console.log('⏸️  Pausing components (page hidden)');
        
        if (this.components.realtimeUpdates) {
            this.components.realtimeUpdates.pauseUpdates();
        }
    }
    
    resumeComponents() {
        console.log('▶️  Resuming components (page visible)');
        
        if (this.components.realtimeUpdates) {
            this.components.realtimeUpdates.resumeUpdates();
        }
        
        // Refresh data when page becomes visible
        if (this.components.dataTable) {
            this.components.dataTable.ajax.reload(null, false);
        }
    }
    
    // Public API methods
    toggleAdvancedFilters() {
        const panel = $('#advancedFiltersPanel');
        const button = $('#advancedFiltersToggle');
        
        if (panel.hasClass('d-none')) {
            panel.removeClass('d-none');
            button.html('<i class=\"bi bi-funnel-fill me-1\"></i>Advanced Filters');
            button.addClass('active');
        } else {
            panel.addClass('d-none');
            button.html('<i class=\"bi bi-funnel me-1\"></i>Advanced Filters');
            button.removeClass('active');
        }
    }
    
    refreshAllComponents() {
        console.log('🔄 Refreshing all components...');
        
        if (this.components.dataTable) {
            this.components.dataTable.ajax.reload(null, false);
        }
        
        if (this.components.advancedFilters) {
            this.components.advancedFilters.refreshOptions();
        }
        
        if (this.components.globalSearch) {
            this.components.globalSearch.clearSearchResults();
        }
    }
    
    getComponentStatus() {
        const status = {
            initialized: this.isInitialized,
            components: {}
        };
        
        Object.keys(this.components).forEach(key => {
            status.components[key] = !!this.components[key];
        });
        
        return status;
    }
    
    showWelcomeNotification() {
        if (this.hasShownWelcome) return;
        
        const welcomeHtml = `
            <div class="alert alert-success alert-dismissible fade show sgii-welcome-alert" role="alert">
                <div class="d-flex align-items-center">
                    <i class="bi bi-rocket-takeoff fs-4 me-3"></i>
                    <div>
                        <h6 class="alert-heading mb-1">🎉 SGII Phase 3 Features Activated!</h6>
                        <p class="mb-1">Enhanced DataTables with advanced filtering, bulk actions, and keyboard navigation are now available.</p>
                        <small class="text-muted">
                            <kbd>Ctrl+K</kbd> for global search • 
                            <kbd>Ctrl+H</kbd> for keyboard shortcuts • 
                            <kbd>F</kbd> to focus search
                        </small>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Show at top of page
        const container = $('.container-fluid, .container').first();
        if (container.length) {
            container.prepend(welcomeHtml);
            
            // Auto-dismiss after 10 seconds
            setTimeout(() => {
                $('.sgii-welcome-alert').alert('close');
            }, 10000);
        }
        
        this.hasShownWelcome = true;
    }
    
    showErrorNotification(message) {
        const errorHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <div class="d-flex align-items-center">
                    <i class="bi bi-exclamation-triangle fs-4 me-3"></i>
                    <div>
                        <h6 class="alert-heading mb-1">SGII Initialization Error</h6>
                        <p class="mb-0">${message}</p>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = $('.container-fluid, .container').first();
        if (container.length) {
            container.prepend(errorHtml);
        }
    }
    
    handleComponentError(error) {
        console.error('Component error:', error);
        
        // Try to recover from common errors
        if (error.message.includes('DataTable')) {
            console.log('Attempting DataTable recovery...');
            setTimeout(() => {
                this.refreshAllComponents();
            }, 1000);
        }
    }
    
    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    destroy() {
        console.log('🧹 Destroying SGII Phase 3 components...');
        
        // Destroy components
        Object.values(this.components).forEach(component => {
            if (component && typeof component.destroy === 'function') {
                component.destroy();
            }
        });
        
        // Remove event listeners
        $(window).off('.sgii');
        
        // Clean up DOM
        $('#advancedFiltersPanel, #globalSearchModal, #bulkActionBar').remove();
        $('.sgii-welcome-alert').remove();
        
        this.isInitialized = false;
        console.log('✅ SGII Phase 3 components destroyed');
    }
}

// Global instance
let sgiiPhase3 = null;

// Auto-initialization function
function initializeSGIIPhase3(config = {}) {
    if (sgiiPhase3) {
        console.warn('SGII Phase 3 already initialized');
        return sgiiPhase3;
    }
    
    sgiiPhase3 = new SGIIPhase3Integration(config);
    return sgiiPhase3;
}

// Auto-initialize when DOM is ready
$(document).ready(function() {
    // Check if we're on a page with DataTables
    if ($('.dataTable, [data-sgii-enhance]').length > 0) {
        console.log('🚀 SGII Phase 3 auto-initialization starting...');
        
        // Wait a bit for DataTables to initialize
        setTimeout(() => {
            const config = {
                // Get configuration from data attributes
                tableId: $('.dataTable').first().attr('id') ? '#' + $('.dataTable').first().attr('id') : '#exchangesTable',
                features: {
                    advancedFilters: $('[data-feature="advanced-filters"]').length > 0,
                    bulkActions: $('[data-feature="bulk-actions"]').length > 0,
                    keyboardNavigation: $('[data-feature="keyboard-nav"]').length > 0,
                    realtimeUpdates: $('[data-feature="realtime"]').length > 0,
                    globalSearch: $('[data-feature="global-search"]').length > 0
                }
            };
            
            const phase3 = initializeSGIIPhase3(config);
            phase3.init().catch(error => {
                console.error('Auto-initialization failed:', error);
            });
        }, 500);
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SGIIPhase3Integration;
}
