// Authentication logic for SEIM frontend
// Modularized from auth.js and main.js

import { apiRequest } from './api.js';
import { showSuccessAlert, showErrorAlert } from './notifications.js';
import { setLoadingState } from './ui.js';
import { logger } from './logger.js';
import { errorHandler } from './error-handler.js';

let authState = {
    user: null,
    tokenExpiry: null,
    isAuthenticated: false
};

export function getAccessToken() {
    return localStorage.getItem('seim_access_token');
}
export function getRefreshToken() {
    return localStorage.getItem('seim_refresh_token');
}
function storeTokens(access, refresh) {
    localStorage.setItem('seim_access_token', access);
    localStorage.setItem('seim_refresh_token', refresh);
}
function clearTokens() {
    localStorage.removeItem('seim_access_token');
    localStorage.removeItem('seim_refresh_token');
}

/**
 * Handle login form submission
 */
async function handleLogin(event) {
    try {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        
        // Get form values
        const usernameOrEmail = formData.get('username');
        const password = formData.get('password');
        
        // Validate form
        if (!usernameOrEmail || !password) {
            showErrorAlert('Validation Error', 'Please fill in all fields');
            return;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        setLoadingState(submitBtn, true, 'Logging in...');
        
        try {
            const data = await apiRequest(window.API_ENDPOINTS.token, {
                method: 'POST',
                body: JSON.stringify({ login: usernameOrEmail, password })
            });
            
            // Store tokens
            storeTokens(data.access, data.refresh);
            
            // Get user info
            await getUserInfo();
            
            // Show success message and redirect
            await showSuccessAlert('Login Successful', 'Welcome back! Redirecting to dashboard...');
            window.location.href = '/dashboard/';
            
        } catch (error) {
            errorHandler.handleAuthError(error, { action: 'login' });
            logger.error('[ERROR] Login error:', error);
            showErrorAlert('Login Failed', error.message || 'Please check your credentials and try again.');
        } finally {
            // Reset button state
            setLoadingState(submitBtn, false);
        }
    } catch (err) {
        errorHandler.handleAuthError(err, { action: 'login-exception' });
        logger.error('[ERROR] Exception in handleLogin:', err);
        showErrorAlert('Login Error', 'An unexpected error occurred. Please try again.');
    }
}

export async function login(usernameOrEmail, password, submitBtn) {
    setLoadingState(submitBtn, true, 'Logging in...');
    try {
        const data = await apiRequest(window.API_ENDPOINTS.token, {
            method: 'POST',
            body: JSON.stringify({ login: usernameOrEmail, password })
        });
        storeTokens(data.access, data.refresh);
        await getUserInfo();
        await showSuccessAlert('Login Successful', 'Welcome back! Redirecting to dashboard...');
        window.location.href = '/dashboard/';
    } catch (error) {
        showErrorAlert('Login Failed', error.message || 'Please check your credentials and try again.');
    } finally {
        setLoadingState(submitBtn, false);
    }
}

export async function logout() {
    try {
        await apiRequest(window.API_ENDPOINTS.logout, { method: 'POST' });
    } catch (error) {
        // Ignore errors on logout
    } finally {
        clearTokens();
        await showSuccessAlert('Logged Out', 'You have been successfully logged out.');
        window.location.href = '/login/';
    }
}

export async function register(email, username, password, submitBtn) {
    setLoadingState(submitBtn, true, 'Registering...');
    try {
        await apiRequest(window.API_ENDPOINTS.register, {
            method: 'POST',
            body: JSON.stringify({ email, username, password })
        });
        await showSuccessAlert('Registration Successful', 'Please check your email for verification. You will be redirected to login.');
        setTimeout(() => {
            window.location.href = '/login/';
        }, 3000);
    } catch (error) {
        showErrorAlert('Registration Failed', error.message || 'Please try again.');
    } finally {
        setLoadingState(submitBtn, false);
    }
}

export async function resetPassword(email, submitBtn) {
    setLoadingState(submitBtn, true, 'Sending...');
    try {
        await apiRequest(window.API_ENDPOINTS.passwordReset, {
            method: 'POST',
            body: JSON.stringify({ email })
        });
        await showSuccessAlert('Email Sent', 'If an account with this email exists, you will receive password reset instructions.');
    } catch (error) {
        showErrorAlert('Email Send Failed', error.message || 'Please try again.');
    } finally {
        setLoadingState(submitBtn, false);
    }
}

export async function getUserInfo() {
    try {
        const userData = await apiRequest('/api/accounts/profile/');
        authState.user = userData;
        authState.isAuthenticated = true;
        return userData;
    } catch (error) {
        authState.user = null;
        authState.isAuthenticated = false;
        throw error;
    }
}

export function getUser() {
    return authState.user;
}
export function isAuthenticated() {
    return authState.isAuthenticated;
}

export async function refreshToken() {
    const refresh = getRefreshToken();
    if (!refresh) return false;
    try {
        const data = await apiRequest(window.API_ENDPOINTS.tokenRefresh, {
            method: 'POST',
            body: JSON.stringify({ refresh })
        });
        storeTokens(data.access, data.refresh || refresh);
        return true;
    } catch (error) {
        clearTokens();
        return false;
    }
}

/**
 * Handle registration form submission
 */
async function handleRegister(event) {
    try {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        
        // Get form values
        const email = formData.get('email');
        const username = formData.get('username');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        const agreeTerms = formData.get('agree_terms');
        
        // Validate form
        if (!email || !username || !password || !confirmPassword || !agreeTerms) {
            showErrorAlert('Validation Error', 'Please fill in all fields and agree to terms');
            return;
        }
        
        if (password !== confirmPassword) {
            showErrorAlert('Validation Error', 'Passwords do not match');
            return;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        setLoadingState(submitBtn, true, 'Creating account...');
        
        try {
            await apiRequest(window.API_ENDPOINTS.register, {
                method: 'POST',
                body: JSON.stringify({ email, username, password })
            });
            
            // Show success message and redirect
            await showSuccessAlert('Registration Successful', 'Account created successfully! Redirecting to login...');
            setTimeout(() => {
                window.location.href = '/login/';
            }, 2000);
            
        } catch (error) {
            errorHandler.handleAuthError(error, { action: 'register' });
            logger.error('[ERROR] Registration error:', error);
            showErrorAlert('Registration Failed', error.message || 'Please try again.');
        } finally {
            // Reset button state
            setLoadingState(submitBtn, false);
        }
    } catch (err) {
        errorHandler.handleAuthError(err, { action: 'register-exception' });
        logger.error('[ERROR] Exception in handleRegister:', err);
        showErrorAlert('Registration Error', 'An unexpected error occurred. Please try again.');
    }
}

/**
 * Attach event listeners to authentication forms (login, register, etc.)
 */
export function setupAuthForms() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Registration form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
} 