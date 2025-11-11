/**
 * SEIM - Student Exchange Information Manager
 * Optimized Main JavaScript File
 */

import { SEIM_LOGGER } from './modules/logger.js';
import { SEIM_ERROR_HANDLER } from './modules/error-handler.js';
import { SEIM_AUTH } from './modules/auth-unified.js';
import SEIM_PERFORMANCE from './modules/performance.js';
import SEIM_API from './modules/api-enhanced.js';
import SEIM_DYNAMIC_LOADER from './modules/dynamic-loader.js';
import SEIM_ACCESSIBILITY from './modules/accessibility.js';
import SEIM_ACCESSIBILITY_TESTER from './modules/accessibility-tester.js';
import SEIM_UI_ENHANCED from './modules/ui-enhanced.js';
import { initializeTooltips, initializeModals, showPageLoading, hidePageLoading } from './modules/ui.js';
import { initializeFileUpload } from './modules/file_upload.js';
import { showSuccessAlert, showErrorAlert } from './modules/notifications.js';

let initialized = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    SEIM_PERFORMANCE.trackPageLoad();
    initializeApp();
});

/**
 * Initialize the application with performance monitoring
 */
function initializeApp() {
    if (initialized) return;
    
    const startTime = performance.now();
    
    try {
        // Use new SEIM_AUTH for authentication
        SEIM_AUTH.init();
        // Initialize core features
        initializeCoreFeatures();
        // Initialize lazy features
        requestIdleCallback(() => {
            initializeLazyFeatures();
        });
        initialized = true;
        SEIM_LOGGER.info('Application initialized successfully');
    } catch (error) {
        SEIM_ERROR_HANDLER.handleError(error, { context: 'app-initialization' });
        SEIM_LOGGER.error('Application initialization failed', error);
    }
    
    const endTime = performance.now();
    SEIM_PERFORMANCE.trackBundleLoad('main-app', startTime, endTime, 0);
}

/**
 * Initialize core features that are critical for user experience
 */
function initializeCoreFeatures() {
    try {
        // Initialize tooltips
        initializeTooltips();
        
        // Initialize modals
        initializeModals();
        
        // Initialize AJAX setup
        setupAjaxDefaults();
        
        // Initialize notifications
        initializeNotifications();
        SEIM_LOGGER.info('Core features initialized');
    } catch (error) {
        SEIM_ERROR_HANDLER.handleError(error, { context: 'core-features' });
        SEIM_LOGGER.error('Core features initialization failed', error);
    }
}

/**
 * Initialize features that can be loaded lazily
 */
function initializeLazyFeatures() {
    try {
        // Initialize file upload areas
        initializeFileUpload();
        
        // Initialize dynamic loading
        initializeDynamicLoading();
        
        // Initialize accessibility features
        initializeAccessibility();
        
        // Initialize enhanced UI features
        initializeEnhancedUI();
        
        // Initialize service worker if available
        initializeServiceWorker();
        SEIM_LOGGER.info('Lazy features initialized');
    } catch (error) {
        SEIM_ERROR_HANDLER.handleError(error, { context: 'lazy-features' });
        SEIM_LOGGER.error('Lazy features initialization failed', error);
    }
}

/**
 * Initialize notifications system
 */
function initializeNotifications() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Initialize dynamic loading for non-critical features
 */
function initializeDynamicLoading() {
    try {
        // Setup lazy loading for different sections
        SEIM_DYNAMIC_LOADER.setupLazyLoading('[data-module="applications"]', 'applications');
        SEIM_DYNAMIC_LOADER.setupLazyLoading('[data-module="documents"]', 'documents');
        SEIM_DYNAMIC_LOADER.setupLazyLoading('[data-module="programs"]', 'programs');
        SEIM_DYNAMIC_LOADER.setupLazyLoading('[data-module="analytics"]', 'analytics');
        
        // Preload high-priority modules
        SEIM_DYNAMIC_LOADER.preloadModule('dashboard');
        
        SEIM_LOGGER.info('Dynamic loading initialized');
    } catch (error) {
        SEIM_ERROR_HANDLER.handleError(error, { context: 'dynamic-loading' });
        SEIM_LOGGER.error('Dynamic loading initialization failed', error);
    }
}

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
    try {
        // Run accessibility test in development mode
        if (process.env.NODE_ENV === 'development') {
            // Run accessibility test after page load
            setTimeout(async () => {
                try {
                    const results = await SEIM_ACCESSIBILITY_TESTER.runFullTest();
                    SEIM_LOGGER.info('Accessibility test completed', results.summary);
                    
                    // Log any issues
                    if (results.failed.length > 0) {
                        SEIM_LOGGER.warn('Accessibility issues found', { 
                            failed: results.failed.length,
                            warnings: results.warnings.length 
                        });
                    }
                } catch (error) {
                    SEIM_LOGGER.error('Accessibility test failed', error);
                }
            }, 2000);
        }
        
        SEIM_LOGGER.info('Accessibility features initialized');
    } catch (error) {
        SEIM_ERROR_HANDLER.handleError(error, { context: 'accessibility' });
        SEIM_LOGGER.error('Accessibility initialization failed', error);
    }
}

/**
 * Initialize enhanced UI features
 */
function initializeEnhancedUI() {
    try {
        // Setup skeleton loading for data tables
        const dataTables = document.querySelectorAll('[data-skeleton-load]');
        dataTables.forEach(table => {
            const skeletonType = table.getAttribute('data-skeleton-load') || 'table';
            SEIM_UI_ENHANCED.showSkeleton(table, skeletonType);
        });
        
        // Setup progressive loading for content areas
        const progressiveElements = document.querySelectorAll('[data-progressive-load]');
        progressiveElements.forEach(element => {
            // Progressive loading is handled by the enhanced UI module
            SEIM_LOGGER.debug('Progressive loading element found', { 
                element: element.tagName, 
                url: element.getAttribute('data-progressive-load') 
            });
        });
        
        // Setup error recovery for forms
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                // Add error recovery options
                const submitButton = form.querySelector('[type="submit"]');
                if (submitButton) {
                    submitButton.addEventListener('click', () => {
                        // Show loading state
                        const loadingOverlay = SEIM_UI_ENHANCED.showLoadingOverlay(form, 'Submitting...');
                        
                        // Store for cleanup
                        form.setAttribute('data-loading-overlay', 'true');
                        
                        // Cleanup after form submission
                        setTimeout(() => {
                            SEIM_UI_ENHANCED.hideLoadingOverlay(loadingOverlay);
                            form.removeAttribute('data-loading-overlay');
                        }, 5000);
                    });
                }
            });
        });
        
        SEIM_LOGGER.info('Enhanced UI features initialized');
    } catch (error) {
        SEIM_ERROR_HANDLER.handleError(error, { context: 'enhanced-ui' });
        SEIM_LOGGER.error('Enhanced UI initialization failed', error);
    }
}



/**
 * SweetAlert2 Utility Functions
 */

/**
 * Show a simple alert
 */
function showAlert(message, icon = 'info', title = null) {
    return Swal.fire({
        title: title,
        text: message,
        icon: icon,
        confirmButtonColor: '#0d6efd',
        confirmButtonText: 'OK'
    });
}

/**
 * Show success alert
 */
function showSuccessAlert(title, message) {
    return Swal.fire({
        title: title,
        text: message,
        icon: 'success',
        confirmButtonColor: '#198754',
        confirmButtonText: 'OK'
    });
}

/**
 * Show error alert
 */
function showErrorAlert(title, message) {
    return Swal.fire({
        title: title,
        text: message,
        icon: 'error',
        confirmButtonColor: '#dc3545',
        confirmButtonText: 'OK'
    });
}

/**
 * Show warning alert
 */
function showWarningAlert(title, message) {
    return Swal.fire({
        title: title,
        text: message,
        icon: 'warning',
        confirmButtonColor: '#ffc107',
        confirmButtonText: 'OK'
    });
}

/**
 * Show confirmation dialog
 */
function showConfirmDialog(title, text, confirmButtonText = 'Yes, proceed') {
    return Swal.fire({
        title: title,
        text: text,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#0d6efd',
        cancelButtonColor: '#6c757d',
        confirmButtonText: confirmButtonText,
        cancelButtonText: 'Cancel'
    });
}

/**
 * Show loading alert
 */
function showLoadingAlert(title = 'Loading...') {
    return Swal.fire({
        title: title,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

/**
 * Close current SweetAlert2
 */
function closeAlert() {
    Swal.close();
}

/**
 * Loading State Management
 */

/**
 * Set loading state for form elements
 */
function setLoadingState(element, isLoading, loadingText = 'Loading...') {
    if (isLoading) {
        element.disabled = true;
        element.dataset.originalText = element.innerHTML;
        // Use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(element, `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${loadingText}`);
        } else {
            // Fallback to textContent for safety
            element.textContent = loadingText;
        }
    } else {
        element.disabled = false;
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(element, element.dataset.originalText || 'Submit');
        } else {
            element.textContent = element.dataset.originalText || 'Submit';
        }
    }
}

/**
 * Set loading state for multiple elements
 */
function setLoadingStates(elements, isLoading, loadingText = 'Loading...') {
    if (Array.isArray(elements)) {
        elements.forEach(element => setLoadingState(element, isLoading, loadingText));
    } else {
        setLoadingState(elements, isLoading, loadingText);
    }
}

/**
 * Show loading overlay for entire page
 */
function showPageLoading(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.id = 'page-loading-overlay';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
    overlay.style.cssText = `
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 9999;
        backdrop-filter: blur(2px);
    `;
    
    // Use security utilities for safe innerHTML setting
    if (window.SEIM_SECURITY_UTILS) {
        window.SEIM_SECURITY_UTILS.safeSetInnerHTML(overlay, `
            <div class="text-center text-white">
                <div class="spinner-border mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div>${message}</div>
            </div>
        `);
    } else {
        // Fallback to textContent for safety
        overlay.textContent = message;
    }
    
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hidePageLoading() {
    const overlay = document.getElementById('page-loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Show loading state for specific section
 */
function showSectionLoading(selector, message = 'Loading...') {
    const section = document.querySelector(selector);
    if (!section) return;
    
    const overlay = document.createElement('div');
    overlay.className = 'position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
    overlay.style.cssText = `
        background-color: rgba(255, 255, 255, 0.8);
        z-index: 1000;
    `;
    
    // Use security utilities for safe innerHTML setting
    if (window.SEIM_SECURITY_UTILS) {
        window.SEIM_SECURITY_UTILS.safeSetInnerHTML(overlay, `
            <div class="text-center">
                <div class="spinner-border text-primary mb-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="text-muted">${message}</div>
            </div>
        `);
    } else {
        // Fallback to textContent for safety
        overlay.textContent = message;
    }
    
    section.style.position = 'relative';
    section.appendChild(overlay);
}

/**
 * Hide section loading
 */
function hideSectionLoading(selector) {
    const section = document.querySelector(selector);
    if (!section) return;
    
    const overlay = section.querySelector('.position-absolute');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Start token refresh timer
 */
function startTokenRefreshTimer() {
    // Refresh token every 50 minutes (tokens expire in 60 minutes)
    setInterval(() => {
        refreshToken();
    }, 50 * 60 * 1000);
}

/**
 * Refresh JWT token
 */
async function refreshToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        clearTokens();
        window.location.href = '/login/';
        return;
    }
    
    try {
        const data = await apiRequest(window.API_ENDPOINTS.refresh, {
            method: 'POST',
            body: JSON.stringify({
                refresh: refreshToken
            })
        });
        
        storeTokens(data.access, data.refresh);
        return true; // Indicate successful refresh
    } catch (error) {
        errorHandler.handleAuthError(error, { action: 'refreshToken' });
        logger.error('Token refresh failed', error);
        clearTokens();
        window.location.href = '/login/';
        return false; // Indicate failed refresh
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
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

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showSuccessAlert('Success', 'Copied to clipboard!');
    } catch (err) {
        errorHandler.handleApiError(err, { action: 'copyToClipboard' });
        logger.error('Failed to copy text', err);
        showErrorAlert('Error', 'Failed to copy to clipboard');
    }
}

/**
 * Input Sanitization Functions
 */

/**
 * Sanitize user input to prevent XSS
 */
function sanitizeInput(input) {
    if (typeof input !== 'string') {
        return input;
    }
    
    // Remove potentially dangerous characters
    return input
        .trim()
        .replace(/[<>]/g, '') // Remove < and >
        .replace(/javascript:/gi, '') // Remove javascript: protocol
        .replace(/on\w+=/gi, '') // Remove event handlers
        .replace(/data:/gi, '') // Remove data: protocol
        .replace(/vbscript:/gi, ''); // Remove vbscript: protocol
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (typeof text !== 'string') {
        return text;
    }
    
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Sanitize form data
 */
function sanitizeFormData(formData) {
    const sanitized = {};
    
    for (const [key, value] of formData.entries()) {
        // Don't sanitize passwords or sensitive fields
        if (key.toLowerCase().includes('password') || key.toLowerCase().includes('token')) {
            sanitized[key] = value;
        } else {
            sanitized[key] = sanitizeInput(value);
        }
    }
    
    return sanitized;
}

/**
 * Validate and sanitize email
 */
function validateAndSanitizeEmail(email) {
    const sanitized = sanitizeInput(email);
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(sanitized)) {
        throw new Error('Please enter a valid email address');
    }
    
    return sanitized;
}

/**
 * Validate and sanitize username
 */
function validateAndSanitizeUsername(username) {
    const sanitized = sanitizeInput(username);
    
    if (sanitized.length < 3) {
        throw new Error('Username must be at least 3 characters long');
    }
    
    if (sanitized.length > 30) {
        throw new Error('Username must be less than 30 characters');
    }
    
    if (!/^[a-zA-Z0-9_]+$/.test(sanitized)) {
        throw new Error('Username can only contain letters, numbers, and underscores');
    }
    
    return sanitized;
}

/**
 * Download file from URL
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate password strength
 */
function validatePassword(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    return {
        isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar,
        errors: {
            length: password.length < minLength,
            uppercase: !hasUpperCase,
            lowercase: !hasLowerCase,
            numbers: !hasNumbers,
            special: !hasSpecialChar
        }
    };
}

// Export functions for use in other modules
window.SEIM = {
    apiRequest,
    formatDate,
    formatCurrency,
    validateEmail,
    validatePassword,
    copyToClipboard,
    downloadFile
}; 

// --- Programs List AJAX Filter/Search ---
document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('programsFilterForm');
    const programsListContainer = document.getElementById('programsListContainer');
    if (filterForm && programsListContainer) {
        // Debounce input changes
        const debouncedFetch = debounce(fetchPrograms, 400);
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            fetchPrograms();
        });
        // Listen to input/select changes for live filtering
        filterForm.querySelectorAll('input, select').forEach(el => {
            el.addEventListener('change', debouncedFetch);
        });
    }

    async function fetchPrograms() {
        showSectionLoading('#programsListContainer', 'Loading programs...');
        const params = new URLSearchParams(new FormData(filterForm)).toString();
        try {
            const data = await apiRequest(`/api/programs/?${params}`);
            // Render the programs list (assume a renderProgramsList function exists or implement here)
            renderProgramsList(data.results || data); // DRF paginated or plain list
            showToast('Programs updated!', 'success');
        } catch (err) {
            let title = 'Error', message = 'Could not load programs.';
            if (err && err.title) title = err.title;
            if (err && err.message) message = err.message;
            showErrorAlert(title, message);
        } finally {
            hideSectionLoading('#programsListContainer');
        }
    }

    function renderProgramsList(programs) {
        if (!Array.isArray(programs)) return;
        if (programs.length === 0) {
            // Use security utilities for safe innerHTML setting
        if (window.SEIM_SECURITY_UTILS) {
            window.SEIM_SECURITY_UTILS.safeSetInnerHTML(programsListContainer, `<div class='col-12'><div class='card'><div class='card-body text-center py-5'><i class='bi bi-calendar-x display-4 text-muted'></i><h4 class='mt-3'>No Programs Found</h4><p class='text-muted'>There are currently no exchange programs available.</p></div></div></div>`);
        } else {
            // Fallback to textContent for safety
            programsListContainer.textContent = 'No Programs Found - There are currently no exchange programs available.';
        }
            return;
        }
        // ... rest of render logic ...
    }
}
); 