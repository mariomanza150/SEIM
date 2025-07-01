/**
 * Enhanced Bootstrap Components for SEIM
 * Provides additional functionality and utilities for the Bootstrap implementation
 */

// Global SEIM object
window.SEIM = window.SEIM || {};

// Theme Management
SEIM.Theme = {
    init: function() {
        const savedTheme = localStorage.getItem('theme') || 'auto';
        this.setTheme(savedTheme);
        this.initThemeSwitcher();
    },

    setTheme: function(theme) {
        if (theme === 'auto') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme);
        }
        localStorage.setItem('theme', theme);
        this.updateThemeIcon(theme);
    },

    updateThemeIcon: function(theme) {
        document.querySelectorAll('.theme-icon').forEach(icon => {
            icon.style.display = 'none';
        });
        
        const activeIcon = document.querySelector(`.theme-icon[data-theme-icon="${theme}"]`);
        if (activeIcon) {
            activeIcon.style.display = 'inline-block';
        }

        // Update active state in dropdown
        document.querySelectorAll('[data-bs-theme-value]').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-bs-theme-value') === theme);
        });
    },

    initThemeSwitcher: function() {
        document.querySelectorAll('[data-bs-theme-value]').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                const theme = e.target.getAttribute('data-bs-theme-value');
                this.setTheme(theme);
            });
        });

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            const storedTheme = localStorage.getItem('theme');
            if (storedTheme === 'auto') {
                this.setTheme('auto');
            }
        });
    }
};

// Toast Notifications
SEIM.Toast = {
    show: function(message, type = 'info', duration = 5000) {
        const toastContainer = this.getContainer();
        const toast = this.createToast(message, type, duration);
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: duration
        });
        
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
        
        return bsToast;
    },

    getContainer: function() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    },

    createToast: function(message, type, duration) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-circle-fill',
            info: 'bi-info-circle-fill'
        };

        const colors = {
            success: 'text-bg-success',
            error: 'text-bg-danger',
            warning: 'text-bg-warning',
            info: 'text-bg-info'
        };

        const toast = document.createElement('div');
        toast.className = 'toast border-0 shadow';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-body ${colors[type] || colors.info} d-flex align-items-center">
                <i class="bi ${icons[type] || icons.info} me-2"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="toast"></button>
            </div>
        `;
        return toast;
    },

    success: function(message, duration) {
        return this.show(message, 'success', duration);
    },

    error: function(message, duration) {
        return this.show(message, 'error', duration);
    },

    warning: function(message, duration) {
        return this.show(message, 'warning', duration);
    },

    info: function(message, duration) {
        return this.show(message, 'info', duration);
    }
};

// Loading States
SEIM.Loading = {
    show: function(element, text = 'Loading...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;
        
        element.classList.add('loading');
        element.disabled = true;
        
        // Store original content
        element.dataset.originalContent = element.innerHTML;
        
        // Add loading content
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            ${text}
        `;
    },

    hide: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;
        
        element.classList.remove('loading');
        element.disabled = false;
        
        // Restore original content
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }
    }
};

// Form Utilities
SEIM.Form = {
    init: function() {
        this.initFloatingLabels();
        this.initValidation();
        this.initAutoSave();
    },

    initFloatingLabels: function() {
        document.querySelectorAll('.form-floating input, .form-floating textarea').forEach(input => {
            // Add focused class on focus
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            // Remove focused class on blur if empty
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement.classList.remove('focused');
                }
            });
            
            // Check initial state
            if (input.value) {
                input.parentElement.classList.add('focused');
            }
        });
    },

    initValidation: function() {
        document.querySelectorAll('.needs-validation').forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Focus first invalid field
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                }
                form.classList.add('was-validated');
            });
        });
    },

    initAutoSave: function() {
        let autoSaveTimeout;
        
        document.querySelectorAll('form[data-auto-save]').forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    clearTimeout(autoSaveTimeout);
                    autoSaveTimeout = setTimeout(() => {
                        this.autoSave(form);
                    }, 3000); // Auto-save after 3 seconds of inactivity
                });
            });
        });
    },

    autoSave: function(form) {
        const formData = new FormData(form);
        const url = form.dataset.autoSaveUrl || form.action;
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                SEIM.Toast.show('Draft saved automatically', 'success', 2000);
            }
        })
        .catch(error => {
            console.error('Auto-save error:', error);
        });
    }
};

// Modal Utilities
SEIM.Modal = {
    show: function(modalId, options = {}) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bsModal = new bootstrap.Modal(modal, options);
            bsModal.show();
            return bsModal;
        }
    },

    hide: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    },

    confirm: function(message, callback, options = {}) {
        const modalId = 'confirm-modal-' + Date.now();
        const modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow">
                    <div class="modal-header border-0">
                        <h5 class="modal-title">${options.title || 'Confirm Action'}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="d-flex align-items-center">
                            <div class="avatar me-3 bg-warning bg-opacity-10 text-warning d-flex align-items-center justify-content-center">
                                <i class="bi bi-question-circle fs-4"></i>
                            </div>
                            <div>${message}</div>
                        </div>
                    </div>
                    <div class="modal-footer border-0">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            ${options.cancelText || 'Cancel'}
                        </button>
                        <button type="button" class="btn btn-primary" id="confirm-btn">
                            ${options.confirmText || 'Confirm'}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Handle confirm button
        modal.querySelector('#confirm-btn').addEventListener('click', () => {
            callback();
            bsModal.hide();
        });
        
        // Clean up when modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
        
        return bsModal;
    }
};

// Search and Filter
SEIM.Search = {
    init: function() {
        this.initInstantSearch();
        this.initFilters();
    },

    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    initInstantSearch: function() {
        const searchInputs = document.querySelectorAll('[data-instant-search]');
        
        searchInputs.forEach(input => {
            const debouncedSearch = this.debounce((query) => {
                this.performSearch(input, query);
            }, 300);
            
            input.addEventListener('input', (e) => {
                debouncedSearch(e.target.value);
            });
        });
    },

    performSearch: function(input, query) {
        const url = input.dataset.searchUrl;
        const targetSelector = input.dataset.searchTarget;
        
        if (!url || !targetSelector) return;
        
        const formData = new FormData();
        formData.append('q', query);
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            const target = document.querySelector(targetSelector);
            if (target) {
                target.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Search error:', error);
        });
    },

    initFilters: function() {
        document.querySelectorAll('[data-filter-form]').forEach(form => {
            const inputs = form.querySelectorAll('select, input[type="checkbox"], input[type="radio"]');
            
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    setTimeout(() => {
                        form.submit();
                    }, 100);
                });
            });
        });
    }
};

// Utilities
SEIM.Utils = {
    copyToClipboard: function(text, successMessage = 'Copied to clipboard!') {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                SEIM.Toast.success(successMessage, 2000);
            }).catch(() => {
                this.fallbackCopyToClipboard(text, successMessage);
            });
        } else {
            this.fallbackCopyToClipboard(text, successMessage);
        }
    },

    fallbackCopyToClipboard: function(text, successMessage) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            SEIM.Toast.success(successMessage, 2000);
        } catch (err) {
            SEIM.Toast.error('Failed to copy to clipboard', 3000);
        }
        
        document.body.removeChild(textArea);
    },

    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    animateCounter: function(element, start, end, duration = 1000) {
        const startTime = performance.now();
        const difference = end - start;
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + (difference * easeOut));
            
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize core components
    SEIM.Theme.init();
    SEIM.Form.init();
    SEIM.Search.init();
    
    // Initialize Bootstrap components
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Animate counters on scroll
    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const end = parseInt(element.dataset.counter);
                    SEIM.Utils.animateCounter(element, 0, end);
                    observer.unobserve(element);
                }
            });
        });
        
        counters.forEach(counter => observer.observe(counter));
    }
});

// Export SEIM object globally
window.SEIM = SEIM;