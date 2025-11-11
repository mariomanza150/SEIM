/**
 * SEIM Enhanced UI Module
 * Provides advanced loading states, error handling, and mobile experience improvements
 */

import { SEIM_LOGGER } from './logger.js';
import { SEIM_ERROR_HANDLER } from './error-handler.js';

class EnhancedUI {
    constructor() {
        this.loadingStates = new Map();
        this.skeletonTemplates = new Map();
        this.errorStates = new Map();
        
        this.config = {
            skeletonAnimationDuration: 1500,
            loadingTimeout: 10000,
            errorRetryAttempts: 3,
            mobileBreakpoint: 768,
            enableSkeletonLoading: true,
            enableProgressiveLoading: true,
            enableErrorRecovery: true
        };
        
        this.mobileDetected = this.detectMobile();
        this.init();
    }
    
    init() {
        this.setupSkeletonTemplates();
        this.setupMobileOptimizations();
        this.setupErrorRecovery();
        this.setupProgressiveLoading();
        
        SEIM_LOGGER.info('Enhanced UI initialized');
    }
    
    /**
     * Detect mobile device
     */
    detectMobile() {
        return window.innerWidth <= this.config.mobileBreakpoint ||
               /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    /**
     * Setup skeleton loading templates
     */
    setupSkeletonTemplates() {
        // Table skeleton
        this.skeletonTemplates.set('table', `
            <div class="skeleton-table">
                <div class="skeleton-header">
                    ${Array(5).fill('<div class="skeleton-cell"></div>').join('')}
                </div>
                ${Array(3).fill(`
                    <div class="skeleton-row">
                        ${Array(5).fill('<div class="skeleton-cell"></div>').join('')}
                    </div>
                `).join('')}
            </div>
        `);
        
        // Card skeleton
        this.skeletonTemplates.set('card', `
            <div class="skeleton-card">
                <div class="skeleton-image"></div>
                <div class="skeleton-content">
                    <div class="skeleton-title"></div>
                    <div class="skeleton-text"></div>
                    <div class="skeleton-text short"></div>
                </div>
            </div>
        `);
        
        // Form skeleton
        this.skeletonTemplates.set('form', `
            <div class="skeleton-form">
                <div class="skeleton-field"></div>
                <div class="skeleton-field"></div>
                <div class="skeleton-field short"></div>
                <div class="skeleton-button"></div>
            </div>
        `);
        
        // List skeleton
        this.skeletonTemplates.set('list', `
            <div class="skeleton-list">
                ${Array(5).fill(`
                    <div class="skeleton-item">
                        <div class="skeleton-avatar"></div>
                        <div class="skeleton-content">
                            <div class="skeleton-title"></div>
                            <div class="skeleton-text"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `);
        
        // Add skeleton CSS
        this.addSkeletonCSS();
    }
    
    /**
     * Add skeleton loading CSS
     */
    addSkeletonCSS() {
        const style = document.createElement('style');
        style.textContent = `
            /* Skeleton Loading Animation */
            @keyframes skeleton-loading {
                0% { background-position: -200px 0; }
                100% { background-position: calc(200px + 100%) 0; }
            }
            
            .skeleton {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200px 100%;
                animation: skeleton-loading ${this.config.skeletonAnimationDuration}ms infinite;
                border-radius: 4px;
            }
            
            /* Skeleton Table */
            .skeleton-table {
                width: 100%;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
            }
            
            .skeleton-header {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                background: #f8f9fa;
                border-bottom: 1px solid #e0e0e0;
            }
            
            .skeleton-row {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                border-bottom: 1px solid #e0e0e0;
            }
            
            .skeleton-cell {
                height: 40px;
                margin: 8px;
            }
            
            /* Skeleton Card */
            .skeleton-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
            }
            
            .skeleton-image {
                height: 120px;
                margin-bottom: 12px;
            }
            
            .skeleton-title {
                height: 24px;
                margin-bottom: 8px;
                width: 70%;
            }
            
            .skeleton-text {
                height: 16px;
                margin-bottom: 6px;
                width: 100%;
            }
            
            .skeleton-text.short {
                width: 60%;
            }
            
            /* Skeleton Form */
            .skeleton-form {
                padding: 16px;
            }
            
            .skeleton-field {
                height: 40px;
                margin-bottom: 16px;
            }
            
            .skeleton-field.short {
                width: 50%;
            }
            
            .skeleton-button {
                height: 40px;
                width: 120px;
            }
            
            /* Skeleton List */
            .skeleton-list {
                padding: 16px;
            }
            
            .skeleton-item {
                display: flex;
                align-items: center;
                margin-bottom: 16px;
            }
            
            .skeleton-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin-right: 12px;
            }
            
            .skeleton-content {
                flex: 1;
            }
            
            /* Progressive Loading */
            .progressive-loading {
                position: relative;
                min-height: 200px;
            }
            
            .progressive-loading .loading-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }
            
            /* Error States */
            .error-state {
                text-align: center;
                padding: 32px 16px;
                background: #f8f9fa;
                border-radius: 8px;
                margin: 16px 0;
            }
            
            .error-state .error-icon {
                font-size: 48px;
                color: #dc3545;
                margin-bottom: 16px;
            }
            
            .error-state .error-title {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 8px;
                color: #343a40;
            }
            
            .error-state .error-message {
                color: #6c757d;
                margin-bottom: 16px;
            }
            
            .error-state .error-actions {
                display: flex;
                gap: 8px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            /* Mobile Optimizations */
            @media (max-width: 768px) {
                .skeleton-cell {
                    height: 32px;
                    margin: 4px;
                }
                
                .skeleton-card {
                    padding: 12px;
                }
                
                .skeleton-image {
                    height: 80px;
                }
                
                .error-state {
                    padding: 24px 12px;
                }
                
                .error-state .error-actions {
                    flex-direction: column;
                    align-items: center;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Show skeleton loading
     */
    showSkeleton(container, type = 'table', options = {}) {
        if (!this.config.enableSkeletonLoading) return;
        
        const template = this.skeletonTemplates.get(type);
        if (!template) {
            SEIM_LOGGER.warn('Skeleton template not found', { type });
            return;
        }
        
        const skeletonId = `skeleton-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Store original content
        const originalContent = container.innerHTML;
        this.loadingStates.set(skeletonId, {
            container,
            originalContent,
            type,
            startTime: Date.now()
        });
        
        // Show skeleton - use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(container, template);
        } else {
            // Fallback to textContent for safety
            container.textContent = 'Loading...';
        }
        container.classList.add('skeleton-loading');
        container.setAttribute('data-skeleton-id', skeletonId);
        
        // Set timeout for loading
        setTimeout(() => {
            this.hideSkeleton(skeletonId);
        }, options.timeout || this.config.loadingTimeout);
        
        return skeletonId;
    }
    
    /**
     * Hide skeleton loading
     */
    hideSkeleton(skeletonId) {
        const loadingState = this.loadingStates.get(skeletonId);
        if (!loadingState) return;
        
        const { container, originalContent } = loadingState;
        
        // Restore original content - use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(container, originalContent);
        } else {
            // Fallback to textContent for safety
            container.textContent = 'Content loaded';
        }
        container.classList.remove('skeleton-loading');
        container.removeAttribute('data-skeleton-id');
        
        // Remove from tracking
        this.loadingStates.delete(skeletonId);
        
        const duration = Date.now() - loadingState.startTime;
        SEIM_LOGGER.debug('Skeleton loading completed', { skeletonId, duration });
    }
    
    /**
     * Setup progressive loading
     */
    setupProgressiveLoading() {
        if (!this.config.enableProgressiveLoading) return;
        
        // Observe elements with progressive loading
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadProgressiveContent(entry.target);
                }
            });
        });
        
        // Find elements with progressive loading
        document.querySelectorAll('[data-progressive-load]').forEach(element => {
            observer.observe(element);
        });
    }
    
    /**
     * Load progressive content
     */
    async loadProgressiveContent(element) {
        const loadUrl = element.getAttribute('data-progressive-load');
        if (!loadUrl) return;
        
        try {
            // Show loading overlay
            this.showProgressiveLoading(element);
            
            // Load content
            const response = await fetch(loadUrl);
            const content = await response.text();
            
            // Update element - use security utilities for safe innerHTML setting
            if (window.SEIM_SECURITY_UTILS) {
                window.SEIM_SECURITY_UTILS.safeSetInnerHTML(element, content);
            } else {
                // Fallback to textContent for safety
                element.textContent = 'Content loaded';
            }
            element.removeAttribute('data-progressive-load');
            
            // Hide loading overlay
            this.hideProgressiveLoading(element);
            
            SEIM_LOGGER.debug('Progressive content loaded', { url: loadUrl });
            
        } catch (error) {
            SEIM_ERROR_HANDLER.handleError(error, { context: 'Progressive Loading', url: loadUrl });
            this.showErrorState(element, 'Failed to load content', error);
        }
    }
    
    /**
     * Show progressive loading overlay
     */
    showProgressiveLoading(element) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        // Use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(overlay, `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            `);
        } else {
            // Fallback to textContent for safety
            overlay.textContent = 'Loading...';
        }
        
        element.classList.add('progressive-loading');
        element.appendChild(overlay);
    }
    
    /**
     * Hide progressive loading overlay
     */
    hideProgressiveLoading(element) {
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
        element.classList.remove('progressive-loading');
    }
    
    /**
     * Setup error recovery
     */
    setupErrorRecovery() {
        if (!this.config.enableErrorRecovery) return;
        
        // Global error handler
        window.addEventListener('error', (event) => {
            this.handleGlobalError(event);
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.handlePromiseRejection(event);
        });
    }
    
    /**
     * Handle global errors
     */
    handleGlobalError(event) {
        SEIM_LOGGER.error('Global error occurred', event.error);
        
        // Show user-friendly error message
        this.showGlobalError('An unexpected error occurred. Please refresh the page or try again later.');
    }
    
    /**
     * Handle promise rejections
     */
    handlePromiseRejection(event) {
        SEIM_LOGGER.error('Unhandled promise rejection', event.reason);
        
        // Show user-friendly error message
        this.showGlobalError('A network error occurred. Please check your connection and try again.');
    }
    
    /**
     * Show global error message
     */
    showGlobalError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger alert-dismissible fade show';
        notification.setAttribute('role', 'alert');
        // Use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(notification, `
                <strong>Error:</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `);
        } else {
            // Fallback to textContent for safety
            notification.textContent = `Error: ${message}`;
        }
        
        // Add to page
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(notification, container.firstChild);
        
        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }
    
    /**
     * Show error state for specific element
     */
    showErrorState(element, title, error, options = {}) {
        const errorId = `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Use security utilities for safe HTML creation
        let errorHTML;
        if (window.SEIM_SECURITY_UTILS) {
            errorHTML = window.SEIM_SECURITY_UTILS.createSafeHTML(`
                <div class="error-state" data-error-id="{{errorId}}">
                    <div class="error-icon">⚠️</div>
                    <div class="error-title">{{title}}</div>
                    <div class="error-message">{{message}}</div>
                    <div class="error-actions">
                        {{retryButton}}
                        {{refreshButton}}
                        {{backButton}}
                    </div>
                </div>
            `, {
                errorId: errorId,
                title: title,
                message: options.message || 'Something went wrong. Please try again.',
                retryButton: options.showRetry ? `<button class="btn btn-primary btn-sm" onclick="window.SEIM_UI_ENHANCED.retryError('${errorId}')">Try Again</button>` : '',
                refreshButton: options.showRefresh ? `<button class="btn btn-secondary btn-sm" onclick="location.reload()">Refresh Page</button>` : '',
                backButton: options.showBack ? `<button class="btn btn-outline-secondary btn-sm" onclick="history.back()">Go Back</button>` : ''
            });
        } else {
            // Fallback to simple text content
            errorHTML = `<div class="error-state">Error: ${title}</div>`;
        }
        
        // Store error state
        this.errorStates.set(errorId, {
            element,
            originalContent: element.innerHTML,
            error,
            retryCount: 0,
            retryFunction: options.retryFunction
        });
        
        // Show error state
        element.innerHTML = errorHTML;
        
        SEIM_LOGGER.warn('Error state shown', { errorId, title, error: error.message });
        
        return errorId;
    }
    
    /**
     * Retry error
     */
    async retryError(errorId) {
        const errorState = this.errorStates.get(errorId);
        if (!errorState) return;
        
        const { element, error, retryCount, retryFunction } = errorState;
        
        if (retryCount >= this.config.errorRetryAttempts) {
            this.showErrorState(element, 'Maximum retry attempts reached', error, {
                message: 'Please refresh the page or contact support.',
                showRefresh: true
            });
            return;
        }
        
        // Update retry count
        errorState.retryCount = retryCount + 1;
        
        try {
            // Show loading state
            element.innerHTML = `
                <div class="text-center p-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Retrying...</span>
                    </div>
                    <p class="mt-2">Retrying... (${retryCount + 1}/${this.config.errorRetryAttempts})</p>
                </div>
            `;
            
            // Execute retry function
            if (retryFunction) {
                await retryFunction();
            }
            
            // Restore original content
            element.innerHTML = errorState.originalContent;
            this.errorStates.delete(errorId);
            
            SEIM_LOGGER.info('Error retry successful', { errorId, retryCount: retryCount + 1 });
            
        } catch (retryError) {
            SEIM_LOGGER.error('Error retry failed', { errorId, retryError });
            
            // Show updated error state
            this.showErrorState(element, 'Retry failed', retryError, {
                message: `Retry attempt ${retryCount + 1} failed. Please try again.`,
                showRetry: true,
                showRefresh: true
            });
        }
    }
    
    /**
     * Setup mobile optimizations
     */
    setupMobileOptimizations() {
        if (!this.mobileDetected) return;
        
        // Add mobile-specific classes
        document.documentElement.classList.add('mobile-device');
        
        // Optimize touch targets
        this.optimizeTouchTargets();
        
        // Setup mobile navigation
        this.setupMobileNavigation();
        
        // Optimize images for mobile
        this.optimizeImagesForMobile();
        
        SEIM_LOGGER.info('Mobile optimizations applied');
    }
    
    /**
     * Optimize touch targets
     */
    optimizeTouchTargets() {
        const touchElements = document.querySelectorAll('button, a, input, select, textarea, [role="button"]');
        
        touchElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            
            // Ensure minimum touch target size
            if (rect.width < 44 || rect.height < 44) {
                element.classList.add('touch-target-optimized');
            }
        });
    }
    
    /**
     * Setup mobile navigation
     */
    setupMobileNavigation() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        // Add mobile menu toggle
        const toggleButton = document.createElement('button');
        toggleButton.className = 'navbar-toggler d-md-none';
        toggleButton.setAttribute('type', 'button');
        toggleButton.setAttribute('aria-label', 'Toggle navigation');
        toggleButton.setAttribute('aria-expanded', 'false');
        toggleButton.innerHTML = `
            <span class="navbar-toggler-icon"></span>
        `;
        
        // Add mobile menu
        const mobileMenu = document.createElement('div');
        mobileMenu.className = 'collapse navbar-collapse';
        mobileMenu.id = 'mobileNavbar';
        
        // Move existing nav items to mobile menu
        const navItems = navbar.querySelector('.navbar-nav');
        if (navItems) {
            mobileMenu.appendChild(navItems.cloneNode(true));
        }
        
        // Add toggle functionality
        toggleButton.addEventListener('click', () => {
            const isExpanded = toggleButton.getAttribute('aria-expanded') === 'true';
            toggleButton.setAttribute('aria-expanded', !isExpanded);
            mobileMenu.classList.toggle('show');
        });
        
        // Insert into navbar
        navbar.appendChild(toggleButton);
        navbar.appendChild(mobileMenu);
    }
    
    /**
     * Optimize images for mobile
     */
    optimizeImagesForMobile() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            // Add lazy loading
            if (!img.loading) {
                img.loading = 'lazy';
            }
            
            // Add responsive images
            if (img.srcset) {
                img.sizes = '(max-width: 768px) 100vw, 50vw';
            }
        });
    }
    
    /**
     * Create loading indicator
     */
    createLoadingIndicator(type = 'spinner', options = {}) {
        const indicators = {
            spinner: `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            `,
            dots: `
                <div class="loading-dots">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            `,
            progress: `
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" 
                         style="width: 0%"
                         aria-valuenow="0" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                    </div>
                </div>
            `,
            skeleton: `
                <div class="skeleton ${options.className || ''}"></div>
            `
        };
        
        return indicators[type] || indicators.spinner;
    }
    
    /**
     * Show loading overlay
     */
    showLoadingOverlay(container, message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="text-center">
                ${this.createLoadingIndicator()}
                <p class="mt-2">${message}</p>
            </div>
        `;
        
        container.appendChild(overlay);
        return overlay;
    }
    
    /**
     * Hide loading overlay
     */
    hideLoadingOverlay(overlay) {
        if (overlay && overlay.parentNode) {
            overlay.remove();
        }
    }
}

// Create and export singleton instance
const enhancedUI = new EnhancedUI();

// Export for use in other modules
window.SEIM_UI_ENHANCED = enhancedUI;

export default enhancedUI;
export { EnhancedUI }; 