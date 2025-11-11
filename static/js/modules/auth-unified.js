/**
 * SEIM Unified Authentication Module
 * Consolidates all authentication functionality
 */

import { logger } from './logger.js';
import { errorHandler } from './error-handler.js';

class AuthManager {
    constructor() {
        this.isAuthenticated = false;
        this.currentUser = null;
        this.tokenRefreshTimer = null;
        this.tokenRefreshInterval = 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Initialize authentication
     */
    init() {
        this.checkAuthStatus();
        this.setupTokenRefresh();
        logger.info('Authentication manager initialized');
    }

    /**
     * Check current authentication status
     */
    checkAuthStatus() {
        const token = this.getAccessToken();
        this.isAuthenticated = token !== null;
        
        if (this.isAuthenticated) {
            this.updateAuthUI();
        } else {
            this.updateUnauthUI();
        }

        return this.isAuthenticated;
    }

    /**
     * Get access token from localStorage
     */
    getAccessToken() {
        return localStorage.getItem('seim_access_token');
    }

    /**
     * Get refresh token from localStorage
     */
    getRefreshToken() {
        return localStorage.getItem('seim_refresh_token');
    }

    /**
     * Set access token
     */
    setAccessToken(token) {
        localStorage.setItem('seim_access_token', token);
        this.isAuthenticated = true;
    }

    /**
     * Set refresh token
     */
    setRefreshToken(token) {
        localStorage.setItem('seim_refresh_token', token);
    }

    /**
     * Clear all tokens
     */
    clearTokens() {
        localStorage.removeItem('seim_access_token');
        localStorage.removeItem('seim_refresh_token');
        this.isAuthenticated = false;
        this.currentUser = null;
    }

    /**
     * Login user
     */
    async login(credentials) {
        try {
            logger.info('Attempting login');
            
            const response = await fetch('/api/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(credentials)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Login failed');
            }

            const data = await response.json();
            
            this.setAccessToken(data.access);
            this.setRefreshToken(data.refresh);
            this.currentUser = data.user;
            this.isAuthenticated = true;
            
            this.updateAuthUI();
            this.setupTokenRefresh();
            
            logger.info('Login successful');
            return { success: true, user: data.user };
            
        } catch (error) {
            const errorInfo = errorHandler.handleAuthError(error, { action: 'login' });
            logger.error('Login failed', error);
            return { success: false, error: errorInfo };
        }
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            logger.info('Attempting logout');
            
            const token = this.getAccessToken();
            if (token) {
                await fetch('/api/auth/logout/', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
            }
            
            this.clearTokens();
            this.updateUnauthUI();
            this.clearTokenRefresh();
            
            logger.info('Logout successful');
            return { success: true };
            
        } catch (error) {
            const errorInfo = errorHandler.handleAuthError(error, { action: 'logout' });
            logger.error('Logout failed', error);
            return { success: false, error: errorInfo };
        }
    }

    /**
     * Refresh access token
     */
    async refreshToken() {
        try {
            const refreshToken = this.getRefreshToken();
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

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            this.setAccessToken(data.access);
            
            logger.info('Token refreshed successfully');
            return true;
            
        } catch (error) {
            const errorInfo = errorHandler.handleAuthError(error, { action: 'refresh' });
            logger.error('Token refresh failed', error);
            this.clearTokens();
            this.updateUnauthUI();
            return false;
        }
    }

    /**
     * Setup automatic token refresh
     */
    setupTokenRefresh() {
        this.clearTokenRefresh();
        
        const token = this.getAccessToken();
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                const expiryTime = payload.exp * 1000;
                const currentTime = Date.now();
                const timeUntilRefresh = expiryTime - currentTime - this.tokenRefreshInterval;
                
                if (timeUntilRefresh > 0) {
                    this.tokenRefreshTimer = setTimeout(() => {
                        this.refreshToken();
                    }, timeUntilRefresh);
                } else {
                    this.refreshToken();
                }
            } catch (error) {
                logger.error('Failed to parse token for refresh setup', error);
            }
        }
    }

    /**
     * Clear token refresh timer
     */
    clearTokenRefresh() {
        if (this.tokenRefreshTimer) {
            clearTimeout(this.tokenRefreshTimer);
            this.tokenRefreshTimer = null;
        }
    }

    /**
     * Update UI for authenticated users
     */
    updateAuthUI() {
        const authElements = document.querySelectorAll('.auth-only');
        const unauthElements = document.querySelectorAll('.unauth-only');
        
        authElements.forEach(el => el.style.display = 'block');
        unauthElements.forEach(el => el.style.display = 'none');
    }

    /**
     * Update UI for non-authenticated users
     */
    updateUnauthUI() {
        const authElements = document.querySelectorAll('.auth-only');
        const unauthElements = document.querySelectorAll('.unauth-only');
        
        authElements.forEach(el => el.style.display = 'none');
        unauthElements.forEach(el => el.style.display = 'block');
    }

    /**
     * Get CSRF token from meta tag
     */
    getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    }

    /**
     * Get current user info
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * Check if user is authenticated
     */
    isUserAuthenticated() {
        return this.isAuthenticated;
    }
}

// Create singleton instance
const authManager = new AuthManager();

// Export for use in other modules
export { authManager, AuthManager }; 