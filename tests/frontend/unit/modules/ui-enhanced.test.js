import { EnhancedUI } from '../../../../static/js/modules/ui-enhanced.js';

jest.mock('../../../../static/js/modules/logger.js', () => ({
  logger: { info: jest.fn(), warn: jest.fn(), debug: jest.fn(), error: jest.fn() },
  Logger: jest.fn(),
  LOG_LEVELS: { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3, NONE: 4 },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleError: jest.fn(), handleApiError: jest.fn(), showError: jest.fn() },
  ErrorHandler: jest.fn(),
}));

function mockMatchMedia() {
  window.matchMedia = (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener() {},
    removeListener() {},
    addEventListener() {},
    removeEventListener() {},
    dispatchEvent() { return false; },
  });
}

describe('EnhancedUI', () => {
  let ui;
  beforeEach(() => {
    mockMatchMedia();
    document.body.innerHTML = '';
    global.innerWidth = 1024;
    ui = new EnhancedUI();
  });

  it('detects mobile devices based on width', () => {
    global.innerWidth = 500;
    expect(ui.detectMobile()).toBe(true);
    global.innerWidth = 1200;
    expect(ui.detectMobile()).toBe(false);
  });

  it('shows and hides skeleton loading', () => {
    const container = document.createElement('div');
    document.body.appendChild(container);
    const skeletonId = ui.showSkeleton(container, 'table');
    // Without SEIM_SECURITY_UTILS, fallback uses textContent + skeleton-loading class
    expect(container.classList.contains('skeleton-loading')).toBe(true);
    expect(container.getAttribute('data-skeleton-id')).toBe(skeletonId);
    expect(container.textContent).toContain('Loading...');
    ui.hideSkeleton(skeletonId);
    expect(container.classList.contains('skeleton-loading')).toBe(false);
  });

  it('shows error state in an element', () => {
    const el = document.createElement('div');
    document.body.appendChild(el);
    ui.showErrorState(el, 'Test Error', new Error('fail'));
    expect(el.innerHTML).toContain('error-state');
    expect(el.innerHTML).toContain('Test Error');
  });

  it('shows and hides loading overlay', () => {
    const container = document.createElement('div');
    document.body.appendChild(container);
    const overlay = ui.showLoadingOverlay(container, 'Loading...');
    expect(container.innerHTML).toContain('Loading...');
    ui.hideLoadingOverlay(overlay);
    expect(container.innerHTML).not.toContain('Loading...');
  });
}); 