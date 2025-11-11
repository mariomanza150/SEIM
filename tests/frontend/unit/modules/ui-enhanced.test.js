import { EnhancedUI } from '../../../../static/js/modules/ui-enhanced.js';

jest.mock('../../../../static/js/modules/logger.js', () => ({
  SEIM_LOGGER: { info: jest.fn(), warn: jest.fn(), debug: jest.fn(), error: jest.fn() },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  SEIM_ERROR_HANDLER: { handleError: jest.fn() },
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('EnhancedUI', () => {
  let ui;
  beforeEach(() => {
    document.body.innerHTML = '';
    global.innerWidth = 1024;
    ui = new EnhancedUI();
    jest.clearAllMocks();
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
    expect(document.body.innerHTML).toContain('skeleton-table');
    ui.hideSkeleton(skeletonId);
    expect(document.body.innerHTML).not.toContain('skeleton-table');
  });

  it('shows error state in an element', () => {
    const el = document.createElement('div');
    document.body.appendChild(el);
    ui.showErrorState(el, 'Test Error', new Error('fail'));
    expect(el.innerHTML).toContain('Test Error');
    expect(el.innerHTML).toContain('fail');
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