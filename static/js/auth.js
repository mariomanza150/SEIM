/**
 * SEIM - Student Exchange Information Manager
 * Authentication JavaScript File
 */

import * as Auth from './modules/auth.js';
import { setLoadingState } from './modules/ui.js';
import { showErrorAlert, showSuccessAlert } from './modules/notifications.js';
import { sanitizeInput, validateAndSanitizeEmail, validateAndSanitizeUsername, validatePassword } from './modules/validators.js';
import { logger } from './modules/logger.js';
import { errorHandler } from './modules/error-handler.js';

// Authentication state
let authState = {
    user: null,
    tokenExpiry: null,
    permissions: [],
    roles: [],
    primary_role: null,
    is_admin: false,
    is_coordinator: false,
    is_student: false
};

// Initialize authentication when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAuth();
    initializeLoginPage();
});

/**
 * Initialize authentication system
 */
function initializeAuth() {
    // Check for existing tokens
    const accessToken = Auth.getAccessToken();
    const refreshToken = Auth.getRefreshToken();
    
    if (accessToken && refreshToken) {
        // Validate token and get user info
        Auth.validateTokenAndGetUser();
    } else {
        // No tokens, show login form
        Auth.showLoginForm();
    }
    
    // Setup form event listeners
    Auth.setupAuthForms();
}

/**
 * Handle login form submission
 */
async function handleLogin(event) {
    try {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        
        // Get and sanitize form values
        const usernameOrEmail = sanitizeInput(formData.get('username'));
        const password = formData.get('password'); // Don't sanitize passwords
        
        // Validate form
        if (!usernameOrEmail || !password) {
            showErrorAlert('Validation Error', 'Please fill in all fields');
            return;
        }
        
        // Always use 'login' key for both username and email
        let payload = { login: usernameOrEmail, password: password };
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        setLoadingState(submitBtn, true, 'Logging in...');
        
        try {
            const data = await Auth.apiRequest(window.API_ENDPOINTS.token, {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            
            // Store tokens
            Auth.storeTokens(data.access, data.refresh);
            
            // Get user info
            await Auth.getUserInfo();
            
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

/**
 * Handle registration form submission
 */
async function handleRegistration(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Get and sanitize form values
    const email = sanitizeInput(formData.get('email'));
    const username = sanitizeInput(formData.get('username'));
    const password = formData.get('password'); // Don't sanitize passwords
    const confirmPassword = formData.get('confirm_password');
    
    // Validate form
    if (!email || !username || !password || !confirmPassword) {
        showErrorAlert('Validation Error', 'Please fill in all fields');
        return;
    }
    
    if (password !== confirmPassword) {
        showErrorAlert('Password Mismatch', 'Passwords do not match');
        return;
    }
    
    // Validate and sanitize email
    try {
        validateAndSanitizeEmail(email);
    } catch (error) {
        showErrorAlert('Invalid Email', error.message);
        return;
    }
    
    // Validate username
    try {
        validateAndSanitizeUsername(username);
    } catch (error) {
        showErrorAlert('Invalid Username', error.message);
        return;
    }
    
    // Validate password strength
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
        showErrorAlert('Weak Password', passwordValidation.errors.join('\n'));
        return;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    setLoadingState(submitBtn, true, 'Registering...');
    
    try {
        const data = await Auth.apiRequest(window.API_ENDPOINTS.register, {
            method: 'POST',
            body: JSON.stringify({
                email: email,
                username: username,
                password: password
            })
        });
        
        await showSuccessAlert('Registration Successful', 'Please check your email for verification. You will be redirected to login.');
        
        // Redirect to login page
        setTimeout(() => {
            window.location.href = '/login/';
        }, 3000);
        
    } catch (error) {
        errorHandler.handleAuthError(error, { action: 'register' });
        logger.error('Registration error:', error);
        showErrorAlert('Registration Failed', error.message || 'Please try again.');
    } finally {
        // Reset button state
        setLoadingState(submitBtn, false);
    }
}

/**
 * Handle password reset form submission
 */
async function handlePasswordReset(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Get and sanitize form values
    const email = sanitizeInput(formData.get('email'));
    
    // Validate form
    if (!email) {
        showErrorAlert('Validation Error', 'Please enter your email address');
        return;
    }
    
    // Validate and sanitize email
    try {
        validateAndSanitizeEmail(email);
    } catch (error) {
        showErrorAlert('Invalid Email', error.message);
        return;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    setLoadingState(submitBtn, true, 'Sending...');
    
    try {
        const data = await Auth.apiRequest(window.API_ENDPOINTS.passwordReset, {
            method: 'POST',
            body: JSON.stringify({
                email: email
            })
        });
        
        await showSuccessAlert('Email Sent', 'If an account with this email exists, you will receive password reset instructions.');
        form.reset();
        
    } catch (error) {
        errorHandler.handleAuthError(error, { action: 'password-reset' });
        logger.error('Password reset error:', error);
        showErrorAlert('Email Send Failed', error.message || 'Please try again.');
    } finally {
        // Reset button state
        setLoadingState(submitBtn, false);
    }
}

/**
 * Handle logout
 */
async function handleLogout(event) {
    event.preventDefault();
    
    try {
        // Call logout endpoint
        await Auth.apiRequest(window.API_ENDPOINTS.logout, {
            method: 'POST'
        });
    } catch (error) {
        errorHandler.handleAuthError(error, { action: 'logout' });
        logger.error('Logout error:', error);
        // Continue with logout even if API call fails
    } finally {
        // Clear tokens and redirect
        Auth.clearTokens();
        await showSuccessAlert('Logged Out', 'You have been successfully logged out.');
        window.location.href = '/login/';
    }
}

/**
 * Validate token and get user information
 */
async function validateTokenAndGetUser() {
    try {
        const response = await Auth.apiRequest('/api/accounts/profile/');
        
        if (response.ok) {
            const userData = await response.json();
            authState.user = userData;
            authState.isAuthenticated = true;
            
            // Update UI
            updateUserInterface(userData);
            
            // Start token refresh timer
            startTokenRefreshTimer();
        } else {
            // Token is invalid, clear and redirect to login
            Auth.clearTokens();
            window.location.href = '/login/';
        }
    } catch (error) {
        errorHandler.handleAuthError(error, { action: 'token-validation' });
        logger.error('Token validation error:', error);
        Auth.clearTokens();
        window.location.href = '/login/';
    }
}

/**
 * Get user information
 */
async function getUserInfo() {
    try {
        const response = await Auth.apiRequest('/api/accounts/profile/');
        
        if (response.ok) {
            const userData = await response.json();
            authState.user = userData;
            authState.isAuthenticated = true;
            
            // Fetch user permissions
            await fetchUserPermissions();
            
            // Update UI
            updateUserInterface(userData);
            
            return userData;
        }
    } catch (error) {
        errorHandler.handleAuthError(error, { action: 'get-user-info' });
        logger.error('Get user info error:', error);
        throw error;
    }
}

/**
 * Update user interface with user data
 */
function updateUserInterface(userData) {
    // Update username in navigation
    const usernameElements = document.querySelectorAll('.user-username');
    usernameElements.forEach(el => {
        el.textContent = userData.username;
    });
    
    // Update user role
    const roleElements = document.querySelectorAll('.user-role');
    roleElements.forEach(el => {
        el.textContent = userData.role;
    });
    
    // Update email
    const emailElements = document.querySelectorAll('.user-email');
    emailElements.forEach(el => {
        el.textContent = userData.email;
    });
    
    // Show/hide role-based elements
    updateRoleBasedUI(userData.role);
}

/**
 * Update UI based on user role
 */
function updateRoleBasedUI(role) {
    // Hide all role-specific elements first
    const roleElements = document.querySelectorAll('[data-role]');
    roleElements.forEach(el => {
        el.style.display = 'none';
    });
    
    // Show elements for current role
    const currentRoleElements = document.querySelectorAll(`[data-role="${role}"]`);
    currentRoleElements.forEach(el => {
        el.style.display = 'block';
    });
    
    // Show admin elements for admin users
    if (role === 'admin') {
        const adminElements = document.querySelectorAll('[data-role="admin"]');
        adminElements.forEach(el => {
            el.style.display = 'block';
        });
    }
}

/**
 * Show login form
 */
function showLoginForm() {
    authState.isAuthenticated = false;
    authState.user = null;
    
    // Update UI for non-authenticated users
    updateUnauthUI();
}

/**
 * Fetch user permissions from backend
 * Called after successful login/token validation
 */
async function fetchUserPermissions() {
    try {
        const response = await Auth.apiRequest('/api/accounts/permissions/');
        
        if (response.ok) {
            const permData = await response.json();
            // Update authState with permissions from backend
            authState.permissions = permData.permissions || [];
            authState.roles = permData.roles || [];
            authState.primary_role = permData.primary_role || 'student';
            authState.is_admin = permData.is_admin || false;
            authState.is_coordinator = permData.is_coordinator || false;
            authState.is_student = permData.is_student || false;
            
            logger.info('[AUTH] Permissions loaded:', authState.permissions.length);
            return true;
        } else {
            logger.warn('[AUTH] Failed to fetch permissions');
            return false;
        }
    } catch (error) {
        logger.error('[AUTH] Error fetching permissions:', error);
        return false;
    }
}

/**
 * Check if user has permission
 * Now uses permissions fetched from backend instead of hardcoded list
 */
function hasPermission(permission) {
    if (!authState.isAuthenticated || !authState.user) {
        return false;
    }
    
    // Check if permissions are loaded
    if (!authState.permissions || authState.permissions.length === 0) {
        logger.warn('[AUTH] Permissions not loaded yet');
        return false;
    }
    
    // Check if user has the specific permission
    return authState.permissions.includes(permission);
}

/**
 * Check if user has any of the specified roles
 */
function hasAnyRole(roleNames) {
    if (!authState.isAuthenticated || !authState.roles) {
        return false;
    }
    
    if (typeof roleNames === 'string') {
        roleNames = [roleNames];
    }
    
    return roleNames.some(role => authState.roles.includes(role));
}

/**
 * Check if user has specific role
 */
function hasRole(roleName) {
    return authState.roles && authState.roles.includes(roleName);
}

/**
 * Require authentication for protected routes
 */
function requireAuth() {
    if (!authState.isAuthenticated) {
        window.location.href = '/login/';
        return false;
    }
    return true;
}

/**
 * Require specific permission
 */
function requirePermission(permission) {
    if (!requireAuth()) {
        return false;
    }
    
    if (!hasPermission(permission)) {
        showErrorAlert('Access Denied', 'You do not have permission to access this resource');
        return false;
    }
    
    return true;
}

/**
 * Initialize login page specific functionality
 */
function initializeLoginPage() {
    // Toggle password visibility
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');
    
    if (togglePassword && password) {
        togglePassword.addEventListener('click', function() {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            icon.classList.toggle('bi-eye');
            icon.classList.toggle('bi-eye-slash');
        });
    }
    
    // Auto-focus on username field
    const usernameField = document.getElementById('username');
    if (usernameField) {
        usernameField.focus();
    }
}

/**
 * Attach event listeners to authentication forms (login, register, etc.)
 */
function setupAuthForms() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    // (Optional: Add similar handlers for register, password reset forms if needed)
}

// Export authentication functions
window.Auth = {
    login: handleLogin,
    register: handleRegistration,
    logout: handleLogout,
    resetPassword: handlePasswordReset,
    getUserInfo,
    fetchUserPermissions,
    hasPermission,
    hasRole,
    hasAnyRole,
    requireAuth,
    requirePermission,
    isAuthenticated: () => authState.isAuthenticated,
    getUser: () => authState.user,
    getPermissions: () => authState.permissions,
    getRoles: () => authState.roles,
    getPrimaryRole: () => authState.primary_role,
    isAdmin: () => authState.is_admin,
    isCoordinator: () => authState.is_coordinator,
    isStudent: () => authState.is_student,
    setupAuthForms
}; 