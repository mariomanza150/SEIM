import { errorHandler } from '../../../../static/js/modules/error-handler.js';

describe('error-handler.js', () => {
  test('should handle API errors gracefully', () => {
    const error = new Error('API error');
    const result = errorHandler.handleApiError(error, { url: '/api' });
    expect(result).toHaveProperty('type', 'API_ERROR');
    expect(result).toHaveProperty('message', 'API error');
  });

  test('should handle validation errors', () => {
    const result = errorHandler.handleValidationError(['Missing field'], { field: 'name' });
    expect(result).toHaveProperty('type', 'VALIDATION_ERROR');
    expect(result.errors).toContain('Missing field');
  });

  test('should handle authentication errors', () => {
    const error = new Error('Auth error');
    const result = errorHandler.handleAuthError(error);
    expect(result).toHaveProperty('type', 'AUTH_ERROR');
    expect(result).toHaveProperty('message', 'Auth error');
  });
}); 