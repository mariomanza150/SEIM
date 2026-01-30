/**
 * Toast Notifications Module
 * 
 * Displays Bootstrap Toast notifications for real-time updates
 */

class ToastNotifications {
    constructor(options = {}) {
        this.options = {
            position: 'bottom-right', // top-left, top-right, bottom-left, bottom-right
            autoHide: true,
            delay: 5000, // 5 seconds
            maxToasts: 5,
            ...options
        };
        
        this.toastContainer = null;
        this.toasts = [];
        
        this.init();
    }
    
    /**
     * Initialize toast container
     */
    init() {
        // Create container if it doesn't exist
        this.toastContainer = document.getElementById('toast-container');
        
        if (!this.toastContainer) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toast-container';
            this.toastContainer.className = `toast-container position-fixed p-3 ${this.getPositionClass()}`;
            this.toastContainer.setAttribute('aria-live', 'polite');
            this.toastContainer.setAttribute('aria-atomic', 'true');
            document.body.appendChild(this.toastContainer);
        }
    }
    
    /**
     * Get Bootstrap position class
     */
    getPositionClass() {
        const positions = {
            'top-left': 'top-0 start-0',
            'top-right': 'top-0 end-0',
            'bottom-left': 'bottom-0 start-0',
            'bottom-right': 'bottom-0 end-0'
        };
        return positions[this.options.position] || positions['bottom-right'];
    }
    
    /**
     * Show notification toast
     */
    show(notification) {
        // Limit number of toasts
        if (this.toasts.length >= this.options.maxToasts) {
            this.removeOldest();
        }
        
        const toast = this.createToast(notification);
        this.toastContainer.appendChild(toast);
        this.toasts.push(toast);
        
        // Initialize Bootstrap toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: this.options.autoHide,
            delay: this.options.delay
        });
        
        // Remove from array when hidden
        toast.addEventListener('hidden.bs.toast', () => {
            const index = this.toasts.indexOf(toast);
            if (index > -1) {
                this.toasts.splice(index, 1);
            }
            toast.remove();
        });
        
        bsToast.show();
        
        return toast;
    }
    
    /**
     * Create toast element
     */
    createToast(notification) {
        const {
            id,
            title,
            message,
            category = 'info',
            action_url,
            action_text = 'View',
            timestamp
        } = notification;
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast notification-toast notification-${category}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.dataset.notificationId = id;
        
        // Get icon based on category
        const icon = this.getCategoryIcon(category);
        const bgClass = this.getCategoryColor(category);
        
        // Format timestamp
        const timeStr = timestamp ? this.formatTime(timestamp) : 'Just now';
        
        // Build toast HTML
        toast.innerHTML = `
            <div class="toast-header ${bgClass} text-white">
                <i class="${icon} me-2"></i>
                <strong class="me-auto">${this.escapeHtml(title)}</strong>
                <small>${timeStr}</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                <p class="mb-2">${this.escapeHtml(message)}</p>
                ${action_url ? `
                    <div class="mt-2">
                        <a href="${this.escapeHtml(action_url)}" class="btn btn-sm btn-primary">
                            ${this.escapeHtml(action_text)}
                        </a>
                    </div>
                ` : ''}
            </div>
        `;
        
        return toast;
    }
    
    /**
     * Get icon class for category
     */
    getCategoryIcon(category) {
        const icons = {
            'info': 'bi bi-info-circle',
            'success': 'bi bi-check-circle',
            'warning': 'bi bi-exclamation-triangle',
            'error': 'bi bi-x-circle'
        };
        return icons[category] || icons['info'];
    }
    
    /**
     * Get background color class for category
     */
    getCategoryColor(category) {
        const colors = {
            'info': 'bg-info',
            'success': 'bg-success',
            'warning': 'bg-warning',
            'error': 'bg-danger'
        };
        return colors[category] || colors['info'];
    }
    
    /**
     * Format timestamp
     */
    formatTime(timestamp) {
        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;
            
            // Less than 1 minute
            if (diff < 60000) {
                return 'Just now';
            }
            
            // Less than 1 hour
            if (diff < 3600000) {
                const minutes = Math.floor(diff / 60000);
                return `${minutes}m ago`;
            }
            
            // Less than 1 day
            if (diff < 86400000) {
                const hours = Math.floor(diff / 3600000);
                return `${hours}h ago`;
            }
            
            // Format as date
            return date.toLocaleDateString();
        } catch (error) {
            return '';
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Remove oldest toast
     */
    removeOldest() {
        if (this.toasts.length > 0) {
            const oldest = this.toasts[0];
            const bsToast = bootstrap.Toast.getInstance(oldest);
            if (bsToast) {
                bsToast.hide();
            } else {
                oldest.remove();
                this.toasts.shift();
            }
        }
    }
    
    /**
     * Clear all toasts
     */
    clearAll() {
        this.toasts.forEach(toast => {
            const bsToast = bootstrap.Toast.getInstance(toast);
            if (bsToast) {
                bsToast.hide();
            } else {
                toast.remove();
            }
        });
        this.toasts = [];
    }
    
    /**
     * Show simple notification (convenience method)
     */
    notify(title, message, category = 'info', options = {}) {
        return this.show({
            id: Date.now().toString(),
            title,
            message,
            category,
            ...options
        });
    }
    
    /**
     * Show success notification
     */
    success(title, message, options = {}) {
        return this.notify(title, message, 'success', options);
    }
    
    /**
     * Show error notification
     */
    error(title, message, options = {}) {
        return this.notify(title, message, 'error', options);
    }
    
    /**
     * Show warning notification
     */
    warning(title, message, options = {}) {
        return this.notify(title, message, 'warning', options);
    }
    
    /**
     * Show info notification
     */
    info(title, message, options = {}) {
        return this.notify(title, message, 'info', options);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ToastNotifications;
}

// Make available globally
window.ToastNotifications = ToastNotifications;

// Create global instance
window.toastNotifications = new ToastNotifications();

