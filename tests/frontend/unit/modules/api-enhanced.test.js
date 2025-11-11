import { EnhancedAPI } from '../../../../static/js/modules/api-enhanced.js';

jest.mock('../../../../static/js/modules/logger.js', () => ({
  logger: { info: jest.fn(), error: jest.fn() },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleApiError: jest.fn() },
}));
jest.mock('../../../../static/js/modules/performance.js', () => ({
  recordMetric: jest.fn(),
}));

describe('EnhancedAPI', () => {
  let api;
  beforeEach(() => {
    api = new EnhancedAPI();
    jest.clearAllMocks();
    api.clearCache();
    api.pendingRequests.clear();
    api.requestQueue = [];
    api.isProcessingQueue = false;
  });

  it('caches GET responses and returns cached data', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ foo: 'bar' }),
      status: 200,
    });
    const url = '/api/test';
    const data1 = await api.get(url);
    expect(data1).toEqual({ foo: 'bar' });
    // Second call should hit cache, not fetch
    global.fetch.mockClear();
    const data2 = await api.get(url);
    expect(data2).toEqual({ foo: 'bar' });
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('deduplicates identical requests', async () => {
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation(() => {
      callCount++;
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ foo: callCount }),
        status: 200,
      });
    });
    const url = '/api/dup';
    const [res1, res2] = await Promise.all([api.get(url), api.get(url)]);
    expect(res1).toEqual({ foo: 1 });
    expect(res2).toEqual({ foo: 1 });
    expect(callCount).toBe(1);
  });

  it('queues requests when concurrency limit is reached', async () => {
    api.config.maxConcurrentRequests = 1;
    let resolveFetch;
    global.fetch = jest.fn().mockImplementation(() => new Promise(res => { resolveFetch = res; }));
    const p1 = api.get('/api/queue1');
    const p2 = api.get('/api/queue2');
    expect(api.requestQueue.length).toBe(1);
    resolveFetch({ ok: true, json: () => Promise.resolve({ queued: true }), status: 200 });
    await p1;
    // After first resolves, second should process
    resolveFetch({ ok: true, json: () => Promise.resolve({ queued: true }), status: 200 });
    await p2;
  });

  it('invalidates cache for non-GET requests', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ foo: 'bar' }),
      status: 200,
    });
    const url = '/api/post';
    await api.get(url);
    expect(api.cache.size).toBe(1);
    await api.post(url, { data: 1 });
    expect(api.cache.size).toBe(0);
  });

  it('handles request errors and calls error handler', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
      json: () => Promise.resolve({ message: 'fail' }),
    });
    await expect(api.get('/api/fail')).rejects.toThrow('fail');
    expect(require('../../../static/js/modules/error-handler.js').errorHandler.handleApiError).toHaveBeenCalled();
    expect(require('../../../static/js/modules/logger.js').logger.error).toHaveBeenCalled();
  });

  it('refreshes token if expired and retries', async () => {
    // Simulate expired token and successful refresh
    api.isTokenExpired = jest.fn(() => true);
    api.refreshToken = jest.fn(() => Promise.resolve());
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ refreshed: true }),
      status: 200,
    });
    const data = await api.get('/api/refresh');
    expect(api.refreshToken).toHaveBeenCalled();
    expect(data).toEqual({ refreshed: true });
  });
}); 