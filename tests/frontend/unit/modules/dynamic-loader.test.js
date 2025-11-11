import DynamicLoader from '../../../../static/js/modules/dynamic-loader.js';

jest.mock('../../../../static/js/modules/logger.js', () => ({
  SEIM_LOGGER: { info: jest.fn(), warn: jest.fn(), debug: jest.fn(), error: jest.fn() },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  SEIM_ERROR_HANDLER: { handleError: jest.fn() },
}));
jest.mock('../../../../static/js/modules/performance.js', () => ({
  default: { trackBundleLoad: jest.fn() },
}));

describe('DynamicLoader', () => {
  let loader;
  beforeEach(() => {
    loader = new DynamicLoader();
    jest.clearAllMocks();
    loader.loadedModules.clear();
    loader.loadingModules.clear();
    loader.moduleConfigs.clear();
    loader.setupModuleConfigs();
  });

  it('loads a module and caches it', async () => {
    // Mock global for script loading
    window.SEIM_APPLICATIONS = { foo: 'bar' };
    document.createElement = jest.fn(() => ({
      set src(val) { this._src = val; },
      set type(val) { this._type = val; },
      set async(val) { this._async = val; },
      addEventListener: jest.fn(),
    }));
    document.head.appendChild = jest.fn((script) => {
      setTimeout(() => script.onload(), 10);
    });
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
    document.createElement = jest.fn(() => ({
      set src(val) { this._src = val; },
      set type(val) { this._type = val; },
      set async(val) { this._async = val; },
      addEventListener: jest.fn(),
    }));
    document.head.appendChild = jest.fn((script) => {
      setTimeout(() => script.onerror(), 10);
    });
    await expect(loader.loadModule('applications', { showLoading: false })).rejects.toThrow('Failed to load module');
    expect(require('../../../static/js/modules/error-handler.js').SEIM_ERROR_HANDLER.handleError).toHaveBeenCalled();
  });

  it('loads dependencies before loading module', async () => {
    loader.loadedModules.set('api', { api: true });
    loader.loadedModules.set('auth', { auth: true });
    window.SEIM_APPLICATIONS = { foo: 'bar' };
    document.createElement = jest.fn(() => ({
      set src(val) { this._src = val; },
      set type(val) { this._type = val; },
      set async(val) { this._async = val; },
      addEventListener: jest.fn(),
    }));
    document.head.appendChild = jest.fn((script) => {
      setTimeout(() => script.onload(), 10);
    });
    const module = await loader.loadModule('applications', { showLoading: false });
    expect(module).toEqual({ foo: 'bar' });
  });
}); 