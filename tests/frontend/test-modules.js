/**
 * Test script for new modules
 */

import { logger } from '../static/js/modules/logger.js';
import { errorHandler } from '../static/js/modules/error-handler.js';
import { authManager } from '../static/js/modules/auth-unified.js';

// Test logger
console.log('Testing logger...');
logger.info('Test info message');
logger.warn('Test warning message');
logger.error('Test error message');

// Test error handler
console.log('Testing error handler...');
const apiError = errorHandler.handleApiError(new Error('Test API error'));
const validationError = errorHandler.handleValidationError(['field1', 'field2']);
const authError = errorHandler.handleAuthError(new Error('Test auth error'));

// Test auth manager
console.log('Testing auth manager...');
authManager.init();
console.log('Auth status:', authManager.isUserAuthenticated());

console.log('All tests completed'); 