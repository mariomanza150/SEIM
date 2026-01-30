/**
 * Notification Center Module
 * 
 * Manages the notification center offcanvas:
 * - Fetch and display notifications
 * - Mark as read/delete
 * - Real-time updates via WebSocket
 * - Pagination
 */

class NotificationCenter {
    constructor() {
        this.notifications = [];
        this.currentPage = 1;
        this.hasMore = false;
        this.filter = 'all'; // 'all' or 'unread'
        this.isLoading = false;
        
        this.initElements();
        this.attachEventListeners();
        this.loadNotifications();
    }
    
    /**
     * Initialize DOM elements
     */
    initElements() {
        this.offcanvas = document.getElementById('notificationCenter');
        this.notificationsList = document.getElementById('notificationsList');
        this.loadingEl = document.getElementById('notificationsLoading');
        this.emptyEl = document.getElementById('notificationsEmpty');
        this.markAllReadBtn = document.getElementById('markAllReadBtn');
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        this.loadMoreContainer = document.getElementById('loadMoreContainer');
        this.filterBtns = document.querySelectorAll('input[name="notificationFilter"]');
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Mark all as read
        if (this.markAllReadBtn) {
            this.markAllReadBtn.addEventListener('click', () => this.markAllAsRead());
        }
        
        // Load more
        if (this.loadMoreBtn) {
            this.loadMoreBtn.addEventListener('click', () => this.loadMore());
        }
        
        // Filter buttons
        this.filterBtns.forEach(btn => {
            btn.addEventListener('change', (e) => {
                this.filter = e.target.value;
                this.refresh();
            });
        });
        
        // Listen for real-time notifications
        document.addEventListener('notification-received', (e) => {
            this.handleNewNotification(e.detail);
        });
        
        // Refresh when offcanvas is shown
        if (this.offcanvas) {
            this.offcanvas.addEventListener('shown.bs.offcanvas', () => {
                this.refresh();
            });
        }
    }
    
    /**
     * Load notifications from API
     */
    async loadNotifications(page = 1) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const token = localStorage.getItem('seim_access_token');
            const params = new URLSearchParams({
                page: page,
                ordering: '-sent_at'
            });
            
            if (this.filter === 'unread') {
                params.append('unread', 'true');
            }
            
            const headers = {};
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            const response = await fetch(`/api/notifications/?${params}`, {
                headers: headers,
                credentials: 'include' // Include session cookies for session-based auth
            });
            
            if (!response.ok) {
                throw new Error('Failed to load notifications');
            }
            
            const data = await response.json();
            
            if (page === 1) {
                this.notifications = data.results || [];
            } else {
                this.notifications = [...this.notifications, ...(data.results || [])];
            }
            
            this.currentPage = page;
            this.hasMore = !!data.next;
            
            this.render();
            
        } catch (error) {
            console.error('Error loading notifications:', error);
            this.showError('Failed to load notifications');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    /**
     * Refresh notifications list
     */
    refresh() {
        this.notifications = [];
        this.currentPage = 1;
        this.loadNotifications(1);
    }
    
    /**
     * Load more notifications
     */
    loadMore() {
        this.loadNotifications(this.currentPage + 1);
    }
    
    /**
     * Render notifications list
     */
    render() {
        if (!this.notificationsList) return;
        
        // Clear previous notifications (except loading and empty states)
        const items = this.notificationsList.querySelectorAll('.notification-item');
        items.forEach(item => item.remove());
        
        // Show empty state if no notifications
        if (this.notifications.length === 0) {
            this.showEmpty();
            return;
        }
        
        this.hideEmpty();
        
        // Group notifications by date
        const grouped = this.groupByDate(this.notifications);
        
        // Render each group
        Object.keys(grouped).forEach(date => {
            // Add date header
            const header = document.createElement('div');
            header.className = 'list-group-item bg-light border-0 py-2 px-3 fw-bold small text-muted';
            header.textContent = date;
            this.notificationsList.appendChild(header);
            
            // Add notifications for this date
            grouped[date].forEach(notification => {
                const item = this.createNotificationItem(notification);
                this.notificationsList.appendChild(item);
            });
        });
        
        // Show/hide load more button
        if (this.hasMore) {
            this.loadMoreContainer?.classList.remove('d-none');
        } else {
            this.loadMoreContainer?.classList.add('d-none');
        }
    }
    
    /**
     * Create notification list item
     */
    createNotificationItem(notification) {
        const item = document.createElement('div');
        item.className = `list-group-item notification-item ${notification.is_read ? '' : 'unread'}`;
        item.dataset.notificationId = notification.id;
        item.setAttribute('role', 'listitem');
        
        const icon = this.getCategoryIcon(notification.category || 'info');
        const iconClass = notification.category || 'info';
        const timeAgo = this.getTimeAgo(notification.sent_at);
        
        item.innerHTML = `
            <div class="d-flex gap-3 py-2">
                <div class="notification-icon ${iconClass}">
                    <i class="${icon}"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-start">
                        <h6 class="mb-1 ${notification.is_read ? 'fw-normal' : 'fw-bold'}">${this.escapeHtml(notification.title)}</h6>
                        <span class="notification-time">${timeAgo}</span>
                    </div>
                    <p class="mb-1 text-muted small">${this.escapeHtml(notification.message)}</p>
                    ${notification.action_url ? `
                        <a href="${this.escapeHtml(notification.action_url)}" class="btn btn-sm btn-link p-0">
                            ${this.escapeHtml(notification.action_text || 'View')} <i class="bi bi-arrow-right"></i>
                        </a>
                    ` : ''}
                </div>
                <div class="notification-actions d-flex gap-1">
                    ${!notification.is_read ? `
                        <button type="button" class="btn btn-sm btn-outline-primary mark-read-btn" title="Mark as read" aria-label="Mark as read">
                            <i class="bi bi-check"></i>
                        </button>
                    ` : ''}
                    <button type="button" class="btn btn-sm btn-outline-danger delete-btn" title="Delete" aria-label="Delete notification">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Attach event listeners
        const markReadBtn = item.querySelector('.mark-read-btn');
        if (markReadBtn) {
            markReadBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.markAsRead(notification.id);
            });
        }
        
        const deleteBtn = item.querySelector('.delete-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteNotification(notification.id);
            });
        }
        
        // Click to navigate or mark as read
        item.addEventListener('click', () => {
            if (!notification.is_read) {
                this.markAsRead(notification.id);
            }
            if (notification.action_url) {
                window.location.href = notification.action_url;
            }
        });
        
        return item;
    }
    
    /**
     * Group notifications by date
     */
    groupByDate(notifications) {
        const grouped = {};
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        notifications.forEach(notification => {
            const date = new Date(notification.sent_at);
            date.setHours(0, 0, 0, 0);
            
            let label;
            if (date.getTime() === today.getTime()) {
                label = 'Today';
            } else if (date.getTime() === yesterday.getTime()) {
                label = 'Yesterday';
            } else {
                label = date.toLocaleDateString();
            }
            
            if (!grouped[label]) {
                grouped[label] = [];
            }
            grouped[label].push(notification);
        });
        
        return grouped;
    }
    
    /**
     * Get category icon
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
     * Get time ago string
     */
    getTimeAgo(timestamp) {
        const now = new Date();
        const date = new Date(timestamp);
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        
        return date.toLocaleDateString();
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
     * Mark notification as read
     */
    async markAsRead(notificationId) {
        try {
            // Try to use WebSocket first if available
            if (window.wsClient && window.wsClient.isConnected()) {
                const sent = window.wsClient.markNotificationRead(notificationId);
                if (sent) {
                    // Update local state immediately for better UX
                    const notification = this.notifications.find(n => n.id === notificationId);
                    if (notification) {
                        notification.is_read = true;
                    }
                    
                    // Re-render
                    this.render();
                    
                    // Update badge
                    if (window.updateNotificationBadge) {
                        window.updateNotificationBadge();
                    }
                    
                    return;
                }
            }
            
            // Fallback to API call if WebSocket not available
            const token = localStorage.getItem('seim_access_token');
            const headers = {
                'Content-Type': 'application/json'
            };
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            const response = await fetch(`/api/notifications/${notificationId}/mark_read/`, {
                method: 'POST',
                headers: headers,
                credentials: 'include' // Include session cookies
            });
            
            if (!response.ok) {
                throw new Error('Failed to mark notification as read');
            }
            
            // Update local state
            const notification = this.notifications.find(n => n.id === notificationId);
            if (notification) {
                notification.is_read = true;
            }
            
            // Re-render
            this.render();
            
            // Update badge
            if (window.updateNotificationBadge) {
                window.updateNotificationBadge();
            }
            
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }
    
    /**
     * Mark all notifications as read
     */
    async markAllAsRead() {
        try {
            // Try to use WebSocket first if available
            if (window.wsClient && window.wsClient.isConnected()) {
                const sent = window.wsClient.markAllNotificationsRead();
                if (sent) {
                    // Update local state immediately for better UX
                    this.notifications.forEach(n => n.is_read = true);
                    
                    // Re-render
                    this.render();
                    
                    // Update badge
                    if (window.updateNotificationBadge) {
                        window.updateNotificationBadge();
                    }
                    
                    // Show success message
                    if (window.toastNotifications) {
                        window.toastNotifications.success('Success', 'All notifications marked as read');
                    }
                    
                    return;
                }
            }
            
            // Fallback to API call if WebSocket not available
            const token = localStorage.getItem('seim_access_token');
            const headers = {
                'Content-Type': 'application/json'
            };
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            const response = await fetch('/api/notifications/mark_all_read/', {
                method: 'POST',
                headers: headers,
                credentials: 'include' // Include session cookies
            });
            
            if (!response.ok) {
                throw new Error('Failed to mark all as read');
            }
            
            // Update local state
            this.notifications.forEach(n => n.is_read = true);
            
            // Re-render
            this.render();
            
            // Update badge
            if (window.updateNotificationBadge) {
                window.updateNotificationBadge();
            }
            
            // Show success message
            if (window.toastNotifications) {
                window.toastNotifications.success('Success', 'All notifications marked as read');
            }
            
        } catch (error) {
            console.error('Error marking all as read:', error);
            if (window.toastNotifications) {
                window.toastNotifications.error('Error', 'Failed to mark all as read');
            }
        }
    }
    
    /**
     * Delete notification
     */
    async deleteNotification(notificationId) {
        try {
            const token = localStorage.getItem('seim_access_token');
            const headers = {};
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            const response = await fetch(`/api/notifications/${notificationId}/`, {
                method: 'DELETE',
                headers: headers,
                credentials: 'include' // Include session cookies
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete notification');
            }
            
            // Remove from local state
            this.notifications = this.notifications.filter(n => n.id !== notificationId);
            
            // Re-render
            this.render();
            
            // Update badge
            if (window.updateNotificationBadge) {
                window.updateNotificationBadge();
            }
            
        } catch (error) {
            console.error('Error deleting notification:', error);
        }
    }
    
    /**
     * Handle new notification from WebSocket
     */
    handleNewNotification(notification) {
        // Add to beginning of list
        this.notifications.unshift(notification);
        
        // Re-render
        this.render();
        
        // Show toast (if not already shown by WebSocket handler)
        // This is a fallback in case the main handler didn't trigger
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        this.loadingEl?.classList.remove('d-none');
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        this.loadingEl?.classList.add('d-none');
    }
    
    /**
     * Show empty state
     */
    showEmpty() {
        this.emptyEl?.classList.remove('d-none');
    }
    
    /**
     * Hide empty state
     */
    hideEmpty() {
        this.emptyEl?.classList.add('d-none');
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
    module.exports = NotificationCenter;
}

// Make available globally
window.NotificationCenter = NotificationCenter;

