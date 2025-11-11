import * as api from '../../../../static/js/modules/api.js';

// Mocks
jest.mock('../../../../static/js/modules/auth.js', () => ({
  getAccessToken: jest.fn(() => 'mock-token'),
  getRefreshToken: jest.fn(() => 'mock-refresh-token'),
}));
jest.mock('../../../../static/js/modules/notifications.js', () => ({
  showErrorAlert: jest.fn(),
}));
jest.mock('../../../../static/js/modules/performance.js', () => ({
  trackApiCall: jest.fn(),
}));
jest.mock('../../../../static/js/modules/logger.js', () => ({
  logger: { error: jest.fn() },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleApiError: jest.fn() },
}));

describe('api.js', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear cache
    if (api.cache && api.cache.api) api.cache.api.clear();
  });

  it('caches GET responses and returns cached data', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ foo: 'bar' }),
      clone() { return this; },
      status: 200,
      url: '/api/test',
    });
    const url = '/api/test';
    const data1 = await api.apiRequest(url);
    expect(data1).toEqual({ foo: 'bar' });
    // Second call should hit cache, not fetch
    global.fetch.mockClear();
    const data2 = await api.apiRequest(url);
    expect(data2).toEqual({ foo: 'bar' });
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('handles non-GET requests and sets CSRF token', async () => {
    document.body.innerHTML = '<meta name="csrf-token" content="csrf123">';
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ success: true }),
      status: 200,
      url: '/api/post',
    });
    const data = await api.apiRequest('/api/post', { method: 'POST' });
    expect(data).toEqual({ success: true });
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/post',
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRFToken': 'csrf123',
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('handles API errors and calls error handler', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
      json: () => Promise.resolve({ message: 'fail' }),
      url: '/api/fail',
    });
    await expect(api.apiRequest('/api/fail')).rejects.toThrow('fail');
    // errorHandler and logger should be called
    expect(require('../../../static/js/modules/error-handler.js').errorHandler.handleApiError).toHaveBeenCalled();
    expect(require('../../../static/js/modules/logger.js').logger.error).toHaveBeenCalled();
  });

  it('refreshes token and retries on 401', async () => {
    // Simulate 401 then success
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation(() => {
      callCount++;
      if (callCount === 1) {
        return Promise.resolve({
          ok: false,
          status: 401,
          statusText: 'Unauthorized',
          json: () => Promise.resolve({}),
          url: '/api/secure',
        });
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ secure: true }),
        url: '/api/secure',
      });
    });
    window.Auth = { refreshToken: jest.fn(() => Promise.resolve(true)) };
    const data = await api.apiRequest('/api/secure');
    expect(window.Auth.refreshToken).toHaveBeenCalled();
    expect(data).toEqual({ secure: true });
  });
}); 