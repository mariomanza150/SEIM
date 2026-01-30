/**
 * WebSocket Client for Real-time Notifications
 * 
 * Features:
 * - JWT and session authentication
 * - Automatic reconnection with exponential backoff
 * - Event emitter for notification events
 * - Ping/pong keep-alive
 */

class WebSocketClient {
    constructor(url, options = {}) {
        this.url = url;
        this.options = {
            reconnectInterval: 1000, // Start at 1 second
            maxReconnectInterval: 30000, // Max 30 seconds
            reconnectDecay: 1.5, // Exponential backoff multiplier
            maxReconnectAttempts: 10,
            pingInterval: 30000, // Ping every 30 seconds
            ...options
        };
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.reconnectTimeout = null;
        this.pingTimeout = null;
        this.isIntentionallyClosed = false;
        this.listeners = {};
        
        // Bind methods
        this.connect = this.connect.bind(this);
        this.disconnect = this.disconnect.bind(this);
        this.send = this.send.bind(this);
        this.onOpen = this.onOpen.bind(this);
        this.onMessage = this.onMessage.bind(this);
        this.onError = this.onError.bind(this);
        this.onClose = this.onClose.bind(this);
    }
    
    /**
     * Connect to WebSocket server
     */
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            console.log('WebSocket: Already connected');
            return;
        }
        
        this.isIntentionallyClosed = false;
        
        // Get JWT token for authentication
        const token = localStorage.getItem('seim_access_token');
        const wsUrl = token ? `${this.url}?token=${token}` : this.url;
        
        console.log('WebSocket: Connecting to', this.url);
        
        try {
            this.ws = new WebSocket(wsUrl);
            this.ws.onopen = this.onOpen;
            this.ws.onmessage = this.onMessage;
            this.ws.onerror = this.onError;
            this.ws.onclose = this.onClose;
        } catch (error) {
            console.error('WebSocket: Connection error', error);
            this.scheduleReconnect();
        }
    }
    
    /**
     * Disconnect from WebSocket server
     */
    disconnect() {
        console.log('WebSocket: Disconnecting');
        this.isIntentionallyClosed = true;
        
        // Clear reconnect timeout
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        
        // Clear ping timeout
        if (this.pingTimeout) {
            clearInterval(this.pingTimeout);
            this.pingTimeout = null;
        }
        
        // Close WebSocket
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    
    /**
     * Send message to server
     */
    send(data) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket: Not connected, cannot send message');
            return false;
        }
        
        try {
            this.ws.send(JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('WebSocket: Send error', error);
            return false;
        }
    }
    
    /**
     * Handle connection open
     */
    onOpen(event) {
        console.log('WebSocket: Connected');
        this.reconnectAttempts = 0;
        this.emit('connected', event);
        
        // Start ping/pong keep-alive
        this.startPing();
    }
    
    /**
     * Handle incoming message
     */
    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('WebSocket: Message received', data);
            
            // Emit event based on message type
            if (data.type) {
                this.emit(data.type, data);
            }
            
            // Handle specific message types
            switch (data.type) {
                case 'connection_established':
                    this.emit('ready', data);
                    break;
                    
                case 'notification.new':
                    this.emit('notification', data.notification);
                    break;
                    
                case 'notification.read':
                    this.emit('notification_read', data.notification_id);
                    break;
                    
                case 'pong':
                    // Keep-alive response
                    break;
                    
                case 'error':
                    console.error('WebSocket: Server error', data.message);
                    this.emit('error', data);
                    break;
            }
        } catch (error) {
            console.error('WebSocket: Message parse error', error);
        }
    }
    
    /**
     * Handle connection error
     */
    onError(event) {
        console.error('WebSocket: Error', event);
        this.emit('error', event);
    }
    
    /**
     * Handle connection close
     */
    onClose(event) {
        console.log('WebSocket: Closed', event.code, event.reason);
        this.emit('disconnected', event);
        
        // Clear ping timeout
        if (this.pingTimeout) {
            clearInterval(this.pingTimeout);
            this.pingTimeout = null;
        }
        
        // Attempt reconnect if not intentionally closed
        if (!this.isIntentionallyClosed) {
            this.scheduleReconnect();
        }
    }
    
    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
            console.error('WebSocket: Max reconnect attempts reached');
            this.emit('reconnect_failed');
            return;
        }
        
        // Calculate backoff time
        const timeout = Math.min(
            this.options.reconnectInterval * Math.pow(this.options.reconnectDecay, this.reconnectAttempts),
            this.options.maxReconnectInterval
        );
        
        this.reconnectAttempts++;
        console.log(`WebSocket: Reconnecting in ${timeout}ms (attempt ${this.reconnectAttempts})`);
        
        this.reconnectTimeout = setTimeout(() => {
            this.emit('reconnecting', this.reconnectAttempts);
            this.connect();
        }, timeout);
    }
    
    /**
     * Start ping/pong keep-alive
     */
    startPing() {
        if (this.pingTimeout) {
            clearInterval(this.pingTimeout);
        }
        
        this.pingTimeout = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.send({
                    type: 'ping',
                    timestamp: Date.now()
                });
            }
        }, this.options.pingInterval);
    }
    
    /**
     * Mark notification as read via WebSocket
     */
    markNotificationRead(notificationId) {
        return this.send({
            type: 'mark_read',
            notification_id: notificationId
        });
    }
    
    /**
     * Mark all notifications as read via WebSocket
     */
    markAllNotificationsRead() {
        return this.send({
            type: 'mark_all_read'
        });
    }
    
    /**
     * Event emitter: Add event listener
     */
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    /**
     * Event emitter: Remove event listener
     */
    off(event, callback) {
        if (!this.listeners[event]) return;
        
        const index = this.listeners[event].indexOf(callback);
        if (index > -1) {
            this.listeners[event].splice(index, 1);
        }
    }
    
    /**
     * Event emitter: Emit event
     */
    emit(event, ...args) {
        if (!this.listeners[event]) return;
        
        this.listeners[event].forEach(callback => {
            try {
                callback(...args);
            } catch (error) {
                console.error(`WebSocket: Event handler error for '${event}'`, error);
            }
        });
    }
    
    /**
     * Get connection state
     */
    getState() {
        if (!this.ws) return 'CLOSED';
        
        switch (this.ws.readyState) {
            case WebSocket.CONNECTING:
                return 'CONNECTING';
            case WebSocket.OPEN:
                return 'OPEN';
            case WebSocket.CLOSING:
                return 'CLOSING';
            case WebSocket.CLOSED:
                return 'CLOSED';
            default:
                return 'UNKNOWN';
        }
    }
    
    /**
     * Check if connected
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketClient;
}

// Make available globally
window.WebSocketClient = WebSocketClient;

