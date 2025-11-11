/**
 * SEIM Error Handler Module
 * Provides centralized error handling and reporting
 */

import { logger } from './logger.js';

class ErrorHandler {
    constructor() {
        this.errorCount = 0;
        this.maxErrors = 10;
        this.errorTypes = new Map();
    }

    /**
     * Handle API errors
     */
    handleApiError(error, context = {}) {
        this.errorCount++;
        
        const errorInfo = {
            type: 'API_ERROR',
            message: error.message,
            status: error.status,
            url: error.url,
            context,
            timestamp: new Date().toISOString()
        };

        logger.error('API Error occurred', errorInfo);

        // Track error types for analytics
        this.trackErrorType(errorInfo.type);

        // Prevent error spam
        if (this.errorCount > this.maxErrors) {
            logger.warn('Too many errors, stopping error reporting');
            return;
        }

        return errorInfo;
    }

    /**
     * Handle validation errors
     */
    handleValidationError(errors, context = {}) {
        const errorInfo = {
            type: 'VALIDATION_ERROR',
            errors,
            context,
            timestamp: new Date().toISOString()
        };

        logger.warn('Validation error occurred', errorInfo);
        return errorInfo;
    }

    /**
     * Handle authentication errors
     */
    handleAuthError(error, context = {}) {
        const errorInfo = {
            type: 'AUTH_ERROR',
            message: error.message,
            context,
            timestamp: new Date().toISOString()
        };

        logger.error('Authentication error occurred', errorInfo);
        return errorInfo;
    }

    /**
     * Track error types for analytics
     */
    trackErrorType(type) {
        const count = this.errorTypes.get(type) || 0;
        this.errorTypes.set(type, count + 1);
    }

    /**
     * Get error statistics
     */
    getErrorStats() {
        return {
            totalErrors: this.errorCount,
            errorTypes: Object.fromEntries(this.errorTypes),
            maxErrors: this.maxErrors
        };
    }

    /**
     * Reset error counter
     */
    reset() {
        this.errorCount = 0;
        this.errorTypes.clear();
    }
}

// Create singleton instance
const errorHandler = new ErrorHandler();

export { errorHandler, ErrorHandler }; 