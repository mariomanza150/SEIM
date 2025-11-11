// API abstraction for SEIM frontend
// Modularized from main.js

import { getAccessToken, getRefreshToken } from './auth.js';
import { showErrorAlert } from './notifications.js';
import SEIM_PERFORMANCE from './performance.js';
import { logger } from './logger.js';
import { errorHandler } from './error-handler.js';

// Cache for API responses
const cache = {
    api: new Map(),
    maxAge: 5 * 60 * 1000 // 5 minutes
};

function cacheResponse(url, data) {
    cache.api.set(url, {
        data,
        timestamp: Date.now()
    });
    cleanupCache();
}

function getCachedResponse(url) {
    const cached = cache.api.get(url);
    if (!cached) return null;
    if (Date.now() - cached.timestamp > cache.maxAge) {
        cache.api.delete(url);
        return null;
    }
    return cached;
}

function cleanupCache() {
    const now = Date.now();
    for (const [url, data] of cache.api.entries()) {
        if (now - data.timestamp > cache.maxAge) {
            cache.api.delete(url);
        }
    }
}

async function handleApiResponse(response) {
    const startTime = performance.now();
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 401) {
            // Token expired, try to refresh
            const refreshed = await window.Auth.refreshToken();
            if (refreshed) {
                // Retry the original request
                return await retryRequest(response.url, response);
            } else {
                window.location.href = '/login/';
                return;
            }
        }
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    const endTime = performance.now();
    SEIM_PERFORMANCE.trackApiCall(response.url, 'GET', startTime, endTime, response.status);
    return data;
}

async function retryRequest(url, originalResponse) {
    const token = getAccessToken();
    const options = {
        method: originalResponse.method,
        headers: {
            ...originalResponse.headers,
            'Authorization': `Bearer ${token}`
        }
    };
    if (originalResponse.body) {
        options.body = originalResponse.body;
    }
    const newResponse = await fetch(url, options);
    return handleApiResponse(newResponse);
}

export async function apiRequest(url, options = {}) {
            const startTime = performance.now();
    // Add JWT token if available
    const token = getAccessToken();
    options.headers = {
        ...options.headers,
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
    // Add CSRF token for non-GET
    if (options.method && options.method !== 'GET') {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        options.headers['X-CSRFToken'] = csrfToken;
        options.headers['Content-Type'] = 'application/json';
    }
    // Check cache for GET
    if (!options.method || options.method === 'GET') {
        const cached = getCachedResponse(url);
        if (cached) {
            return cached.data;
        }
    }
    try {
        const response = await fetch(url, options);
        if (response.ok && (!options.method || options.method === 'GET')) {
            const data = await response.clone().json();
            cacheResponse(url, data);
        }
        const data = await handleApiResponse(response);
        const endTime = performance.now();
        SEIM_PERFORMANCE.trackApiCall(url, options.method || 'GET', startTime, endTime, response.status);
        return data;
    } catch (error) {
        const endTime = performance.now();
        SEIM_PERFORMANCE.trackApiCall(url, options.method || 'GET', startTime, endTime, 'error', error);
        errorHandler.handleApiError(error, { url, options });
        logger.error('API Request failed', error);
        throw error;
    }
} 