// Validation and sanitization utilities for SEIM frontend
// Modularized from main.js

/**
 * Sanitize input string
 */
export function sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    return input.replace(/[<>"'`]/g, '');
}

/**
 * Escape HTML
 */
export function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Sanitize FormData
 */
export function sanitizeFormData(formData) {
    const sanitized = {};
    for (const [key, value] of formData.entries()) {
        sanitized[key] = sanitizeInput(value);
    }
    return sanitized;
}

/**
 * Validate and sanitize email
 */
export function validateAndSanitizeEmail(email) {
    if (!validateEmail(email)) {
        throw new Error('Invalid email address');
    }
    return email.trim().toLowerCase();
}

/**
 * Validate and sanitize username
 */
export function validateAndSanitizeUsername(username) {
    if (!username || typeof username !== 'string' || username.length < 3) {
        throw new Error('Username must be at least 3 characters');
    }
    if (!/^[a-zA-Z0-9_.-]+$/.test(username)) {
        throw new Error('Username contains invalid characters');
    }
    return username.trim();
}

/**
 * Validate email
 */
export function validateEmail(email) {
    const re = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
    return re.test(email);
}

/**
 * Validate password strength
 */
export function validatePassword(password) {
    const errors = [];
    if (!password || password.length < 8) {
        errors.push('Password must be at least 8 characters');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('Password must contain an uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
        errors.push('Password must contain a lowercase letter');
    }
    if (!/[0-9]/.test(password)) {
        errors.push('Password must contain a digit');
    }
    if (!/[!@#$%^&*]/.test(password)) {
        errors.push('Password must contain a special character');
    }
    return {
        isValid: errors.length === 0,
        errors
    };
}

/**
 * Validate required fields in response
 */
export function validateRequiredFields(data, requiredFields) {
    const errors = [];
    for (const field of requiredFields) {
        if (data[field] === undefined || data[field] === null) {
            errors.push(`Missing required field: ${field}`);
        }
    }
    return {
        isValid: errors.length === 0,
        errors
    };
}

/**
 * Validate data types in response
 */
export function validateDataTypes(data, typeSchema) {
    const errors = [];
    for (const [field, expectedType] of Object.entries(typeSchema)) {
        if (data[field] !== undefined && data[field] !== null) {
            const actualType = typeof data[field];
            if (actualType !== expectedType) {
                errors.push(`Field ${field} should be ${expectedType}, got ${actualType}`);
            }
        }
    }
    return {
        isValid: errors.length === 0,
        errors
    };
}

/**
 * Create validation schema
 */
export function createValidationSchema(requiredFields = [], typeSchema = {}) {
    return {
        requiredFields,
        typeSchema
    };
} 