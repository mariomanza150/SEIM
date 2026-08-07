import dynamicLoader from '../../../../static/js/modules/dynamic-loader.js';

jest.mock('../../../../static/js/modules/logger.js', () => ({
  logger: { info: jest.fn(), warn: jest.fn(), debug: jest.fn(), error: jest.fn() },
  Logger: jest.fn(),
  LOG_LEVELS: { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3, NONE: 4 },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleError: jest.fn(), handleApiError: jest.fn(), showError: jest.fn() },
  ErrorHandler: jest.fn(),
}));
jest.mock('../../../../static/js/modules/performance.js', () => ({
  __esModule: true,
  default: { trackBundleLoad: jest.fn(), recordMetric: jest.fn(), trackApiCall: jest.fn() },
}));

function mockScriptLoad({ error = false } = {}) {
  const originalCreateElement = document.createElement.bind(document);
  document.createElement = jest.fn((tag) => {
    if (tag === 'script') {
      return {
        set src(val) { this._src = val; },
        get src() { return this._src; },
        set type(val) { this._type = val; },
        set async(val) { this._async = val; },
        onload: null,
        onerror: null,
        addEventListener: jest.fn(),
      };
    }
    return originalCreateElement(tag);
  });
  document.head.appendChild = jest.fn((script) => {
    setTimeout(() => {
      if (error && typeof script.onerror === 'function') {
        script.onerror();
      } else if (typeof script.onload === 'function') {
        script.onload();
      }
    }, 10);
  });
}

describe('DynamicLoader', () => {
  let loader;
  beforeEach(() => {
    loader = dynamicLoader;
    loader.clear();
    loader.moduleConfigs.clear();
    loader.setupModuleConfigs();
    // applications/dashboard depend on api/auth which have no configs — mark loaded
    loader.loadedModules.set('api', { api: true });
    loader.loadedModules.set('auth', { auth: true });
    loader.config.retryAttempts = 0;
    loader.config.loadTimeout = 2000;
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('loads a module and caches it', async () => {
    window.SEIM_APPLICATIONS = { foo: 'bar' };
    mockScriptLoad();
    const module = await loader.loadModule('applications', { showLoading: false });
    expect(module).toEqual({ foo: 'bar' });
    expect(loader.loadedModules.has('applications')).toBe(true);
  });

  it('returns cached module if already loaded', async () => {
    loader.loadedModules.set('dashboard', { dash: true });
    const module = await loader.loadModule('dashboard', { showLoading: false });
    expect(module).toEqual({ dash: true });
  });

  it('throws if module config is missing', async () => {
    await expect(loader.loadModule('notamodule')).rejects.toThrow('Module configuration not found');
  });

  it('handles module load error and calls error handler', async () => {
    mockScriptLoad({ error: true });
    await expect(loader.loadModule('applications', { showLoading: false })).rejects.toThrow('Failed to load module');
    expect(require('../../../../static/js/modules/error-handler.js').errorHandler.handleError).toHaveBeenCalled();
  });

  it('loads dependencies before loading module', async () => {
    window.SEIM_APPLICATIONS = { foo: 'bar' };
    mockScriptLoad();
    const module = await loader.loadModule('applications', { showLoading: false });
    expect(module).toEqual({ foo: 'bar' });
  });
});
