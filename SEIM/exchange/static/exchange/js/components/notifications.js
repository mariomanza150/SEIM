// Notifications module for SEIM application
const Notifications = {
    // Initialize the module
    init: function() {
        this.checkPermissions();
        this.loadNotifications();
        this.startPolling();
        this.bindEvents();
    },
    
    // Check browser notification permissions
    checkPermissions: function() {
        if ("Notification" in window) {
            if (Notification.permission === "default") {
                // Request permission
                Notification.requestPermission().then(function(permission) {
                    if (permission === "granted") {
                        console.log("Notification permission granted");
                    }
                });
            }
        }
    },
    
    // Load notifications from server
    loadNotifications: function() {
        $.ajax({
            url: '/api/notifications/',
            type: 'GET',
            success: function(data) {
                Notifications.updateBadge(data.unread_count);
                Notifications.updateDropdown(data.notifications);
            },
            error: function(xhr) {
                console.error('Failed to load notifications:', xhr);
            }
        });
    },
    
    // Update notification badge
    updateBadge: function(count) {
        const badge = $('#notificationBadge');
        if (count > 0) {
            badge.text(count).show();
        } else {
            badge.hide();
        }
    },
    
    // Update notification dropdown
    updateDropdown: function(notifications) {
        const dropdown = $('#notificationDropdown');
        dropdown.empty();
        
        if (notifications.length === 0) {
            dropdown.append(`
                <div class="dropdown-item text-center text-muted">
                    <i class="fas fa-bell-slash"></i> No new notifications
                </div>
            `);
            return;
        }
        
        notifications.forEach(notification => {
            const item = $(`
                <a href="#" class="dropdown-item notification-item ${notification.is_read ? '' : 'unread'}" 
                   data-notification-id="${notification.id}">
                    <div class="d-flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-${notification.icon} text-${notification.color}"></i>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="mb-1">${notification.title}</h6>
                            <p class="mb-0 small">${notification.message}</p>
                            <small class="text-muted">${notification.time_ago}</small>
                        </div>
                    </div>
                </a>
            `);
            dropdown.append(item);
        });
        
        // Add view all link
        dropdown.append(`
            <div class="dropdown-divider"></div>
            <a href="/notifications/" class="dropdown-item text-center">
                <i class="fas fa-bell"></i> View All Notifications
            </a>
        `);
    },
    
    // Start polling for new notifications
    startPolling: function() {
        // Poll every 30 seconds for new notifications
        setInterval(function() {
            Notifications.checkForNew();
        }, 30000);
    },
    
    // Check for new notifications
    checkForNew: function() {
        $.ajax({
            url: '/api/notifications/check-new/',
            type: 'GET',
            success: function(data) {
                if (data.has_new) {
                    Notifications.loadNotifications();
                    
                    // Show browser notification if enabled
                    if (data.latest_notification && Notification.permission === "granted") {
                        Notifications.showBrowserNotification(data.latest_notification);
                    }
                }
            },
            error: function(xhr) {
                console.error('Failed to check for new notifications:', xhr);
            }
        });
    },
    
    // Show browser notification
    showBrowserNotification: function(notification) {
        const options = {
            body: notification.message,
            icon: '/static/images/favicon.ico',
            badge: '/static/images/badge.png',
            tag: `notification-${notification.id}`,
            requireInteraction: false,
            data: {
                url: notification.url
            }
        };
        
        const n = new Notification(notification.title, options);
        
        // Handle notification click
        n.onclick = function(event) {
            event.preventDefault();
            window.open(event.target.data.url, '_blank');
            n.close();
        };
        
        // Auto-close after 5 seconds
        setTimeout(n.close.bind(n), 5000);
    },
    
    // Bind event handlers
    bindEvents: function() {
        // Mark notification as read when clicked
        $(document).on('click', '.notification-item', function(e) {
            e.preventDefault();
            const notificationId = $(this).data('notification-id');
            const url = $(this).attr('href');
            
            if (!$(this).hasClass('read')) {
                Notifications.markAsRead(notificationId);
            }
            
            if (url && url !== '#') {
                window.location.href = url;
            }
        });
        
        // Open notification dropdown
        $('#notificationBell').on('click', function(e) {
            e.preventDefault();
            $('#notificationDropdown').toggle();
            
            // Mark all as seen when dropdown is opened
            if ($('#notificationDropdown').is(':visible')) {
                Notifications.markAllAsSeen();
            }
        });
        
        // Close dropdown when clicking outside
        $(document).on('click', function(e) {
            if (!$(e.target).closest('#notificationBell, #notificationDropdown').length) {
                $('#notificationDropdown').hide();
            }
        });
    },
    
    // Mark notification as read
    markAsRead: function(notificationId) {
        $.ajax({
            url: `/api/notifications/${notificationId}/read/`,
            type: 'POST',
            success: function() {
                $(`.notification-item[data-notification-id="${notificationId}"]`).removeClass('unread');
                Notifications.updateBadgeCount();
            },
            error: function(xhr) {
                console.error('Failed to mark notification as read:', xhr);
            }
        });
    },
    
    // Mark all notifications as seen
    markAllAsSeen: function() {
        $.ajax({
            url: '/api/notifications/mark-all-seen/',
            type: 'POST',
            success: function() {
                // Update UI if needed
            },
            error: function(xhr) {
                console.error('Failed to mark notifications as seen:', xhr);
            }
        });
    },
    
    // Update badge count
    updateBadgeCount: function() {
        const unreadCount = $('.notification-item.unread').length;
        this.updateBadge(unreadCount);
    },
    
    // Show in-app notification
    showInApp: function(message, type = 'info', duration = 5000) {
        const notification = $(`
            <div class="alert alert-${type} alert-dismissible fade show notification-toast" role="alert">
                <strong><i class="fas fa-bell"></i> Notification</strong>
                <p class="mb-0">${message}</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);
        
        // Create container if it doesn't exist
        if ($('#notificationToastContainer').length === 0) {
            $('body').append(`
                <div id="notificationToastContainer" 
                     class="position-fixed top-0 end-0 p-3" 
                     style="z-index: 11; margin-top: 70px;">
                </div>
            `);
        }
        
        $('#notificationToastContainer').append(notification);
        
        // Auto-dismiss
        if (duration > 0) {
            setTimeout(function() {
                notification.fadeOut(function() {
                    $(this).remove();
                });
            }, duration);
        }
    }
};

// Initialize when document is ready
$(document).ready(function() {
    Notifications.init();
});

// Export for use in other modules
window.Notifications = Notifications;