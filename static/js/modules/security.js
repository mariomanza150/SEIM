/**
 * SEIM Security Utilities
 * 
 * This module provides security utilities for preventing XSS attacks
 * and safely manipulating HTML content. It includes functions for
 * sanitizing user input, escaping HTML, and safely setting innerHTML.
 */

export class SecurityUtils {
    /**
     * Sanitize HTML content to prevent XSS attacks
     * @param {string} content - The HTML content to sanitize
     * @returns {string} - Sanitized HTML content
     */
    static sanitizeHTML(content) {
        if (typeof content !== 'string') {
            return content;
        }
        
        // Create a temporary div element
        const div = document.createElement('div');
        div.textContent = content;
        return div.innerHTML;
    }
    
    /**
     * Safely set innerHTML with sanitization
     * @param {HTMLElement} element - The element to update
     * @param {string} content - The HTML content to set
     */
    static safeSetInnerHTML(element, content) {
        if (!element || typeof content !== 'string') {
            return;
        }
        
        // For trusted content (like loading spinners, icons), we can be less strict
        if (this.isTrustedContent(content)) {
            element.innerHTML = content;
        } else {
            // For user content, sanitize it
            element.innerHTML = this.sanitizeHTML(content);
        }
    }
    
    /**
     * Safely set text content (preferred over innerHTML for text)
     * @param {HTMLElement} element - The element to update
     * @param {string} content - The text content to set
     */
    static safeSetTextContent(element, content) {
        if (!element) {
            return;
        }
        
        element.textContent = content;
    }
    
    /**
     * Escape HTML entities to prevent XSS
     * @param {string} text - The text to escape
     * @returns {string} - Escaped text
     */
    static escapeHTML(text) {
        if (typeof text !== 'string') {
            return text;
        }
        
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Check if content is trusted (safe to use with innerHTML)
     * @param {string} content - The content to check
     * @returns {boolean} - True if content is trusted
     */
    static isTrustedContent(content) {
        if (typeof content !== 'string') {
            return false;
        }
        
        // Trusted content patterns (loading spinners, icons, etc.)
        const trustedPatterns = [
            /^<span class="spinner-border[^"]*"[^>]*>.*<\/span>.*$/,
            /^<div class="[^"]*spinner[^"]*"[^>]*>.*<\/div>$/,
            /^<i class="[^"]*bi-[^"]*"[^>]*><\/i>$/,
            /^<div class="[^"]*loading[^"]*"[^>]*>.*<\/div>$/,
            /^<div class="[^"]*alert[^"]*"[^>]*>.*<\/div>$/,
            /^<button[^>]*class="[^"]*btn[^"]*"[^>]*>.*<\/button>$/,
            /^<div class="[^"]*text-center[^"]*"[^>]*>.*<\/div>$/,
            /^<div class="[^"]*text-muted[^"]*"[^>]*>.*<\/div>$/
        ];
        
        return trustedPatterns.some(pattern => pattern.test(content.trim()));
    }
    
    /**
     * Sanitize user input to prevent XSS
     * @param {string} input - The user input to sanitize
     * @returns {string} - Sanitized input
     */
    static sanitizeInput(input) {
        if (typeof input !== 'string') {
            return input;
        }
        
        // Remove potentially dangerous characters and patterns
        return input
            .trim()
            .replace(/[<>]/g, '') // Remove < and >
            .replace(/javascript:/gi, '') // Remove javascript: protocol
            .replace(/on\w+=/gi, '') // Remove event handlers
            .replace(/data:/gi, '') // Remove data: protocol
            .replace(/vbscript:/gi, '') // Remove vbscript: protocol
            .replace(/expression\(/gi, '') // Remove CSS expressions
            .replace(/url\(/gi, '') // Remove CSS url functions
            .replace(/import\(/gi, ''); // Remove CSS import functions
    }
    
    /**
     * Validate and sanitize email
     * @param {string} email - The email to validate
     * @returns {string} - Sanitized email
     * @throws {Error} - If email is invalid
     */
    static validateAndSanitizeEmail(email) {
        const sanitized = this.sanitizeInput(email);
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailRegex.test(sanitized)) {
            throw new Error('Please enter a valid email address');
        }
        
        return sanitized;
    }
    
    /**
     * Validate and sanitize username
     * @param {string} username - The username to validate
     * @returns {string} - Sanitized username
     * @throws {Error} - If username is invalid
     */
    static validateAndSanitizeUsername(username) {
        const sanitized = this.sanitizeInput(username);
        
        if (sanitized.length < 3) {
            throw new Error('Username must be at least 3 characters long');
        }
        
        if (sanitized.length > 30) {
            throw new Error('Username must be less than 30 characters');
        }
        
        if (!/^[a-zA-Z0-9_]+$/.test(sanitized)) {
            throw new Error('Username can only contain letters, numbers, and underscores');
        }
        
        return sanitized;
    }
    
    /**
     * Sanitize form data
     * @param {FormData} formData - The form data to sanitize
     * @returns {Object} - Sanitized form data
     */
    static sanitizeFormData(formData) {
        const sanitized = {};
        
        for (const [key, value] of formData.entries()) {
            // Don't sanitize passwords or sensitive fields
            if (key.toLowerCase().includes('password') || 
                key.toLowerCase().includes('token') ||
                key.toLowerCase().includes('csrf')) {
                sanitized[key] = value;
            } else {
                sanitized[key] = this.sanitizeInput(value);
            }
        }
        
        return sanitized;
    }
    
    /**
     * Create safe HTML template with sanitized content
     * @param {string} template - The HTML template
     * @param {Object} data - The data to interpolate
     * @returns {string} - Safe HTML with sanitized content
     */
    static createSafeHTML(template, data = {}) {
        let safeHTML = template;
        
        // Replace placeholders with sanitized content
        for (const [key, value] of Object.entries(data)) {
            const placeholder = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
            const sanitizedValue = this.escapeHTML(String(value));
            safeHTML = safeHTML.replace(placeholder, sanitizedValue);
        }
        
        return safeHTML;
    }
}

export const securityUtils = SecurityUtils;

// Also export individual functions for convenience
window.SEIM_SECURITY_UTILS = {
    sanitizeHTML: SecurityUtils.sanitizeHTML.bind(SecurityUtils),
    safeSetInnerHTML: SecurityUtils.safeSetInnerHTML.bind(SecurityUtils),
    safeSetTextContent: SecurityUtils.safeSetTextContent.bind(SecurityUtils),
    escapeHTML: SecurityUtils.escapeHTML.bind(SecurityUtils),
    sanitizeInput: SecurityUtils.sanitizeInput.bind(SecurityUtils),
    validateAndSanitizeEmail: SecurityUtils.validateAndSanitizeEmail.bind(SecurityUtils),
    validateAndSanitizeUsername: SecurityUtils.validateAndSanitizeUsername.bind(SecurityUtils),
    sanitizeFormData: SecurityUtils.sanitizeFormData.bind(SecurityUtils),
    createSafeHTML: SecurityUtils.createSafeHTML.bind(SecurityUtils)
}; 