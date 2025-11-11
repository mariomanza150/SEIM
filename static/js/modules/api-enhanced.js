/**
 * SEIM Enhanced API Module
 * Features: Request deduplication, queuing, intelligent caching, and performance monitoring
 */

import { logger as SEIM_LOGGER } from './logger.js';
import { errorHandler as SEIM_ERROR_HANDLER } from './error-handler.js';
import SEIM_PERFORMANCE from './performance.js';

class EnhancedAPI {
    constructor() {
        this.cache = new Map();
        this.pendingRequests = new Map();
        this.requestQueue = [];
        this.isProcessingQueue = false;
        
        this.config = {
            cacheExpiry: 5 * 60 * 1000, // 5 minutes
            maxCacheSize: 100,
            maxConcurrentRequests: 6,
            maxQueueSize: 50, // Increased from 10 to 50
            requestTimeout: 30000, // 30 seconds
            retryAttempts: 3,
            retryDelay: 1000,
            authToken: null,
            csrfToken: null,
            baseURL: '/',
            enableLogging: true,
            enableMetrics: true
        };
        
        this.metrics = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            cacheHits: 0,
            cacheMisses: 0,
            averageResponseTime: 0
        };
        
        this.initialize();
    }
    
    initialize() {
        // Load tokens from localStorage
        this.config.authToken = localStorage.getItem('seim_access_token');
        this.config.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        // Set up token refresh
        this.setupTokenRefresh();
        
        // Set up performance monitoring
        if (this.config.enableMetrics) {
            this.setupMetrics();
        }
        
        if (this.config.enableLogging) {
            SEIM_LOGGER.info('EnhancedAPI initialized', { config: this.config });
        }
    }
    
    setupTokenRefresh() {
        // Check token expiry every 5 minutes
        setInterval(() => {
            const token = localStorage.getItem('seim_access_token');
            if (token && this.isTokenExpired(token)) {
                this.refreshToken();
            }
        }, 5 * 60 * 1000);
    }
    
    setupMetrics() {
        // Report metrics every minute
        setInterval(() => {
            if (this.metrics.totalRequests > 0) {
                SEIM_PERFORMANCE.recordMetric('api_requests', this.metrics);
                this.resetMetrics();
            }
        }, 60 * 1000);
    }
    
    isTokenExpired(token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 < Date.now();
        } catch (error) {
            return true;
        }
    }
    
    async refreshToken() {
        try {
            const refreshToken = localStorage.getItem('seim_refresh_token');
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }
            
            const response = await fetch('/api/auth/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh: refreshToken })
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('seim_access_token', data.access);
                this.config.authToken = data.access;
                
                if (this.config.enableLogging) {
                    SEIM_LOGGER.info('Token refreshed successfully');
                }
            } else {
                throw new Error('Token refresh failed');
            }
        } catch (error) {
            if (this.config.enableLogging) {
                SEIM_LOGGER.error('Token refresh failed', { error: error.message });
            }
            
            // Clear tokens and redirect to login
            localStorage.removeItem('seim_access_token');
            localStorage.removeItem('seim_refresh_token');
            window.location.href = '/login/';
        }
    }
    
    generateCacheKey(url, options = {}) {
        const method = options.method || 'GET';
        const body = options.body ? JSON.stringify(options.body) : '';
        return `${method}:${url}:${body}`;
    }
    
    getCachedResponse(cacheKey) {
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() < cached.expiry) {
            this.metrics.cacheHits++;
            return cached.data;
        }
        
        if (cached) {
            this.cache.delete(cacheKey);
        }
        
        this.metrics.cacheMisses++;
        return null;
    }
    
    setCachedResponse(cacheKey, data) {
        if (this.cache.size >= this.config.maxCacheSize) {
            // Remove oldest entry
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        
        this.cache.set(cacheKey, {
            data,
            expiry: Date.now() + this.config.cacheExpiry
        });
    }
    
    async queueRequest(requestFn) {
        return new Promise((resolve, reject) => {
            const queueItem = { requestFn, resolve, reject };
            
            if (this.requestQueue.length >= this.config.maxQueueSize) {
                // Remove oldest item from queue
                const oldestItem = this.requestQueue.shift();
                oldestItem.reject(new Error('Queue limit exceeded'));
            }
            
            this.requestQueue.push(queueItem);
            this.processQueue();
        });
    }
    
    async processQueue() {
        if (this.isProcessingQueue || this.requestQueue.length === 0) {
            return;
        }
        
        this.isProcessingQueue = true;
        
        while (this.requestQueue.length > 0 && this.pendingRequests.size < this.config.maxConcurrentRequests) {
            const item = this.requestQueue.shift();
            
            try {
                const result = await item.requestFn();
                item.resolve(result);
            } catch (error) {
                item.reject(error);
            }
        }
        
        this.isProcessingQueue = false;
        
        // Continue processing if there are more items
        if (this.requestQueue.length > 0) {
            setTimeout(() => this.processQueue(), 100);
        }
    }
    
    async makeRequest(url, options = {}) {
        const startTime = performance.now();
        const cacheKey = this.generateCacheKey(url, options);
        
        // Check cache for GET requests
        if (options.method === 'GET' || !options.method) {
            const cached = this.getCachedResponse(cacheKey);
            if (cached) {
                return cached;
            }
        }
        
        // Check for pending identical requests
        if (this.pendingRequests.has(cacheKey)) {
            return this.pendingRequests.get(cacheKey);
        }
        
        const requestPromise = this.executeRequest(url, options, startTime, cacheKey);
        this.pendingRequests.set(cacheKey, requestPromise);
        
        try {
            const result = await requestPromise;
            
            // Cache successful GET responses
            if (options.method === 'GET' || !options.method) {
                this.setCachedResponse(cacheKey, result);
            } else {
                // Invalidate cache for non-GET requests
                this.invalidateCacheForUrl(url);
            }
            
            return result;
        } finally {
            this.pendingRequests.delete(cacheKey);
        }
    }
    
    async executeRequest(url, options, startTime, cacheKey) {
        const fullUrl = url.startsWith('http') ? url : this.config.baseURL + url.replace(/^\//, '');
        
        const headers = {
            'Content-Type': 'application/json',
            'X-Request-ID': this.generateRequestId(),
            ...options.headers
        };
        
        // Add auth token
        if (this.config.authToken) {
            headers['Authorization'] = `Bearer ${this.config.authToken}`;
        }
        
        // Add CSRF token for non-GET requests
        if (options.method && options.method !== 'GET' && this.config.csrfToken) {
            headers['X-CSRFToken'] = this.config.csrfToken;
        }
        
        let requestOptions = {
            ...options,
            headers
        };
        
        // Apply request interceptors
        if (this.requestInterceptors) {
            for (const interceptor of this.requestInterceptors) {
                requestOptions = await interceptor(requestOptions, fullUrl);
            }
        }
        
        // Add timeout signal if AbortSignal.timeout is available (not in Node.js test environment)
        if (typeof AbortSignal !== 'undefined' && AbortSignal.timeout) {
            requestOptions.signal = AbortSignal.timeout(this.config.requestTimeout);
        } else {
            // In test environment, create a proper AbortController signal
            const controller = new AbortController();
            requestOptions.signal = controller.signal;
        }
        
        let lastError;
        let fetchError;
        
        for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
            let response;
            
            try {
                response = await fetch(fullUrl, requestOptions);
            } catch (error) {
                // Network error: fetch threw, response is undefined
                fetchError = error;
                const responseTime = performance.now() - startTime;
                this.updateMetrics(false, responseTime);
                
                if (this.config.enableLogging && typeof SEIM_LOGGER !== 'undefined') {
                    SEIM_LOGGER.error('API request failed', {
                        url: fullUrl,
                        method: options.method || 'GET',
                        attempt,
                        error: error.message
                    });
                }
                
                // Don't retry on certain errors
                if (error.name === 'AbortError') {
                    lastError = error;
                    break;
                }
                
                // Wait before retry
                if (attempt < this.config.retryAttempts) {
                    await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * attempt));
                }
                continue;
            }
            
            // Only process response if fetch succeeded
            if (response) {
                const responseTime = performance.now() - startTime;
                this.updateMetrics(response.ok, responseTime);
                
                if (this.config.enableLogging && typeof SEIM_LOGGER !== 'undefined') {
                    SEIM_LOGGER.info('API request completed', {
                        url: fullUrl,
                        method: options.method || 'GET',
                        status: response.status,
                        responseTime,
                        attempt
                    });
                }
                
                if (!response.ok) {
                    let errorData = {};
                    try {
                        errorData = await response.json();
                    } catch (e) {
                        // If JSON parsing fails, use statusText
                    }
                    let errorMessage;
                    if (response.status === 401) {
                        errorMessage = 'HTTP 401: Unauthorized';
                    } else if (response.status === 404) {
                        errorMessage = 'HTTP 404: Not found';
                    } else if (errorData && errorData.message) {
                        errorMessage = `HTTP ${response.status}: ${errorData.message}`;
                    } else {
                        errorMessage = `HTTP ${response.status}: ${response.statusText || 'Unknown error'}`;
                    }
                    lastError = new Error(errorMessage);
                    
                    // Don't retry on certain errors
                    if (response.status === 401 || response.status === 403) {
                        break;
                    }
                    
                    // Wait before retry
                    if (attempt < this.config.retryAttempts) {
                        await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * attempt));
                    }
                    continue;
                }
                
                let data;
                try {
                    data = await response.json();
                } catch (e) {
                    lastError = new Error(e.message || 'Invalid JSON');
                    
                    // Wait before retry
                    if (attempt < this.config.retryAttempts) {
                        await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * attempt));
                    }
                    continue;
                }
                
                // Apply response interceptors
                if (this.responseInterceptors) {
                    for (const interceptor of this.responseInterceptors) {
                        data = await interceptor(data, response, fullUrl);
                    }
                }
                
                // Extract data property if it exists (for API response format)
                if (data && typeof data === 'object' && 'data' in data) {
                    return data.data;
                }
                
                return data;
            }
        }
        
        // Handle final error
        this.handleRequestError(lastError || fetchError, fullUrl);
        throw lastError || fetchError;
    }
    
    updateMetrics(success, responseTime) {
        this.metrics.totalRequests++;
        
        if (success) {
            this.metrics.successfulRequests++;
        } else {
            this.metrics.failedRequests++;
        }
        
        // Update average response time
        const totalTime = this.metrics.averageResponseTime * (this.metrics.totalRequests - 1) + responseTime;
        this.metrics.averageResponseTime = totalTime / this.metrics.totalRequests;
    }
    
    resetMetrics() {
        this.metrics = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            cacheHits: 0,
            cacheMisses: 0,
            averageResponseTime: 0
        };
    }
    
    handleRequestError(error, url) {
        // Handle specific error types
        if (error.message.includes('401')) {
            // Unauthorized - redirect to login
            if (typeof localStorage !== 'undefined') {
                localStorage.removeItem('seim_access_token');
                localStorage.removeItem('seim_refresh_token');
            }
            if (typeof window !== 'undefined' && window.location) {
                window.location.href = '/login/';
            }
        } else if (error.message.includes('403')) {
            // Forbidden - show access denied
            if (typeof SEIM_ERROR_HANDLER !== 'undefined' && SEIM_ERROR_HANDLER.showError) {
                SEIM_ERROR_HANDLER.showError('Access Denied', 'You do not have permission to perform this action.');
            }
        } else if (error.name === 'AbortError') {
            // Timeout
            if (typeof SEIM_ERROR_HANDLER !== 'undefined' && SEIM_ERROR_HANDLER.showError) {
                SEIM_ERROR_HANDLER.showError('Request Timeout', 'The request took too long to complete. Please try again.');
            }
        } else {
            // Generic error
            if (typeof SEIM_ERROR_HANDLER !== 'undefined' && SEIM_ERROR_HANDLER.showError) {
                SEIM_ERROR_HANDLER.showError('Request Failed', error.message || 'An unexpected error occurred.');
            }
        }
    }
    
    // Convenience methods
    async get(url, options = {}) {
        return this.queueRequest(() => this.makeRequest(url, { ...options, method: 'GET' }));
    }
    
    async post(url, data = null, options = {}) {
        return this.queueRequest(() => this.makeRequest(url, {
            ...options,
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined
        }));
    }
    
    async put(url, data = null, options = {}) {
        return this.queueRequest(() => this.makeRequest(url, {
            ...options,
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined
        }));
    }
    
    async patch(url, data = null, options = {}) {
        return this.queueRequest(() => this.makeRequest(url, {
            ...options,
            method: 'PATCH',
            body: data ? JSON.stringify(data) : undefined
        }));
    }
    
    async delete(url, options = {}) {
        return this.queueRequest(() => this.makeRequest(url, { ...options, method: 'DELETE' }));
    }
    
    // Utility methods
    clearCache() {
        this.cache.clear();
        if (this.config.enableLogging && typeof SEIM_LOGGER !== 'undefined') {
            SEIM_LOGGER.info('API cache cleared');
        }
    }
    
    getMetrics() {
        return { ...this.metrics };
    }
    
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        if (this.config.enableLogging && typeof SEIM_LOGGER !== 'undefined') {
            SEIM_LOGGER.info('API config updated', { config: this.config });
        }
    }
    
    // Test compatibility methods
    setCacheTTL(ttl) {
        this.config.cacheExpiry = ttl;
    }
    
    setRetryConfig(config) {
        this.config.retryAttempts = config.maxRetries || this.config.retryAttempts;
        this.config.retryDelay = config.retryDelay || this.config.retryDelay;
    }
    
    setAuthToken(token) {
        this.config.authToken = token;
    }
    
    setConcurrencyLimit(limit) {
        this.config.maxConcurrentRequests = limit;
    }
    
    setQueueLimit(limit) {
        this.config.maxQueueSize = limit;
    }
    
    addRequestInterceptor(interceptor) {
        if (!this.requestInterceptors) {
            this.requestInterceptors = [];
        }
        this.requestInterceptors.push(interceptor);
    }
    
    addResponseInterceptor(interceptor) {
        if (!this.responseInterceptors) {
            this.responseInterceptors = [];
        }
        this.responseInterceptors.push(interceptor);
    }
    
    getPerformanceMetrics() {
        return {
            totalRequests: this.metrics.totalRequests,
            successfulRequests: this.metrics.successfulRequests,
            failedRequests: this.metrics.failedRequests,
            errorRate: this.metrics.totalRequests > 0 ? this.metrics.failedRequests / this.metrics.totalRequests : 0,
            averageResponseTime: this.metrics.averageResponseTime,
            cacheHits: this.metrics.cacheHits,
            cacheMisses: this.metrics.cacheMisses
        };
    }
    
    clearCacheByPattern(pattern) {
        const regex = new RegExp(pattern);
        for (const key of this.cache.keys()) {
            if (regex.test(key)) {
                this.cache.delete(key);
            }
        }
    }
    
    clearCacheEntry(url) {
        // Generate the cache key for the URL and clear it
        const cacheKey = this.generateCacheKey(url, { method: 'GET' });
        this.cache.delete(cacheKey);
    }
    
    generateRequestId() {
        return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    invalidateCacheForUrl(url) {
        // Clear all GET requests for the same base URL
        const baseUrl = url.split('?')[0]; // Remove query parameters
        for (const key of this.cache.keys()) {
            if (key.startsWith('GET:') && key.includes(baseUrl)) {
                this.cache.delete(key);
            }
        }
    }
}

// Create singleton instance
const enhancedAPI = new EnhancedAPI();

// Export both the instance and the class
export default enhancedAPI;
export { EnhancedAPI }; 