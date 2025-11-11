import AuthManager from '../../../../static/js/modules/auth-unified.js';

jest.mock('../../../../static/js/modules/logger.js', () => ({
  logger: { info: jest.fn(), error: jest.fn() },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleAuthError: jest.fn((err) => err.message) },
}));

describe('AuthManager', () => {
  let auth;
  beforeEach(() => {
    localStorage.clear();
    document.body.innerHTML = '<div class="auth-only"></div><div class="unauth-only"></div>';
    auth = new AuthManager();
    jest.clearAllMocks();
  });

  it('sets and clears tokens', () => {
    auth.setAccessToken('abc');
    auth.setRefreshToken('def');
    expect(localStorage.getItem('seim_access_token')).toBe('abc');
    expect(localStorage.getItem('seim_refresh_token')).toBe('def');
    auth.clearTokens();
    expect(localStorage.getItem('seim_access_token')).toBeNull();
    expect(localStorage.getItem('seim_refresh_token')).toBeNull();
    expect(auth.isAuthenticated).toBe(false);
  });

  it('updates UI for auth and unauth states', () => {
    auth.updateAuthUI();
    expect(document.querySelector('.auth-only').style.display).toBe('block');
    expect(document.querySelector('.unauth-only').style.display).toBe('none');
    auth.updateUnauthUI();
    expect(document.querySelector('.auth-only').style.display).toBe('none');
    expect(document.querySelector('.unauth-only').style.display).toBe('block');
  });

  it('handles login success and failure', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access: 'abc', refresh: 'def', user: { id: 1 } }),
    });
    const result = await auth.login({ username: 'a', password: 'b' });
    expect(result.success).toBe(true);
    expect(auth.isAuthenticated).toBe(true);
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ message: 'fail' }),
    });
    const fail = await auth.login({ username: 'a', password: 'b' });
    expect(fail.success).toBe(false);
  });

  it('handles logout', async () => {
    auth.setAccessToken('abc');
    global.fetch = jest.fn().mockResolvedValue({ ok: true });
    const result = await auth.logout();
    expect(result.success).toBe(true);
    expect(auth.isAuthenticated).toBe(false);
  });

  it('refreshes token successfully and on failure', async () => {
    auth.setRefreshToken('def');
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access: 'newtoken' }),
    });
    const ok = await auth.refreshToken();
    expect(ok).toBe(true);
    global.fetch = jest.fn().mockResolvedValue({ ok: false });
    const fail = await auth.refreshToken();
    expect(fail).toBe(false);
  });
}); 