import * as auth from '../../../static/js/auth.js';

jest.mock('../../../static/js/modules/auth.js', () => ({
  getAccessToken: jest.fn(),
  getRefreshToken: jest.fn(),
  validateTokenAndGetUser: jest.fn(),
  showLoginForm: jest.fn(),
  setupAuthForms: jest.fn(),
  apiRequest: jest.fn(),
  storeTokens: jest.fn(),
  getUserInfo: jest.fn()
}));

describe('auth.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
  });

  test('should call initializeAuth and initializeLoginPage on DOMContentLoaded', () => {
    const spyInitAuth = jest.spyOn(auth, 'initializeAuth');
    const spyInitLogin = jest.spyOn(auth, 'initializeLoginPage');
    document.dispatchEvent(new Event('DOMContentLoaded'));
    expect(spyInitAuth).toHaveBeenCalled();
    expect(spyInitLogin).toHaveBeenCalled();
  });
}); 