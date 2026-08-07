/**
 * auth.js has no named exports; side-effect listeners call modules/auth helpers.
 * Verify DOMContentLoaded wiring via those mocked dependencies.
 */
import { getAccessToken, getRefreshToken, showLoginForm, setupAuthForms } from '../../../static/js/modules/auth.js';

jest.mock('../../../static/js/modules/auth.js', () => ({
  getAccessToken: jest.fn(() => null),
  getRefreshToken: jest.fn(() => null),
  validateTokenAndGetUser: jest.fn(),
  showLoginForm: jest.fn(),
  setupAuthForms: jest.fn(),
  apiRequest: jest.fn(),
  storeTokens: jest.fn(),
  getUserInfo: jest.fn()
}));

jest.mock('../../../static/js/modules/ui.js', () => ({
  setLoadingState: jest.fn(),
}));

jest.mock('../../../static/js/modules/notifications.js', () => ({
  showErrorAlert: jest.fn(),
  showSuccessAlert: jest.fn(),
}));

jest.mock('../../../static/js/modules/validators.js', () => ({
  sanitizeInput: jest.fn((v) => v),
  validateAndSanitizeEmail: jest.fn(),
  validateAndSanitizeUsername: jest.fn(),
  validatePassword: jest.fn(),
}));

jest.mock('../../../static/js/modules/logger.js', () => ({
  logger: { info: jest.fn(), warn: jest.fn(), debug: jest.fn(), error: jest.fn() },
  Logger: jest.fn(),
  LOG_LEVELS: { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3, NONE: 4 },
}));

jest.mock('../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleError: jest.fn(), handleApiError: jest.fn(), showError: jest.fn() },
  ErrorHandler: jest.fn(),
}));

describe('auth.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
    getAccessToken.mockReturnValue(null);
    getRefreshToken.mockReturnValue(null);
  });

  test('DOMContentLoaded initializes auth and login page wiring', async () => {
    await import('../../../static/js/auth.js');
    document.dispatchEvent(new Event('DOMContentLoaded'));

    expect(getAccessToken).toHaveBeenCalled();
    expect(getRefreshToken).toHaveBeenCalled();
    expect(showLoginForm).toHaveBeenCalled();
    expect(setupAuthForms).toHaveBeenCalled();
  });
});
