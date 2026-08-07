import { AccessibilityManager } from '../../../../static/js/modules/accessibility.js';

jest.mock('../../../../static/js/modules/logger.js', () => ({
  logger: { info: jest.fn(), warn: jest.fn(), debug: jest.fn(), error: jest.fn() },
  Logger: jest.fn(),
  LOG_LEVELS: { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3, NONE: 4 },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleError: jest.fn(), handleApiError: jest.fn(), showError: jest.fn() },
  ErrorHandler: jest.fn(),
}));

// Plain function — jest resetMocks clears jest.fn() implementations between tests
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

describe('AccessibilityManager', () => {
  let manager;
  beforeEach(() => {
    mockMatchMedia();
    document.body.innerHTML = '';
    manager = new AccessibilityManager();
  });

  it('adds skip links to the DOM', () => {
    expect(document.body.innerHTML).toContain('Skip to main content');
    expect(document.body.innerHTML).toContain('Skip to navigation');
    expect(document.body.innerHTML).toContain('Skip to footer');
  });

  it('returns focusable elements in a container', () => {
    // jsdom leaves offsetParent null; getFocusableElements filters on it
    Object.defineProperty(HTMLElement.prototype, 'offsetParent', {
      configurable: true,
      get() { return this.parentNode; },
    });
    const container = document.createElement('div');
    container.innerHTML = '<button></button><a href="#"></a><input /><div></div>';
    document.body.appendChild(container);
    const focusables = manager.getFocusableElements(container);
    expect(focusables.length).toBe(3);
  });

  it('announces messages for screen readers', () => {
    jest.useFakeTimers();
    manager.announce('Test announcement');
    jest.advanceTimersByTime(manager.config.announcementDelay);
    expect(document.getElementById('announcement-region').textContent).toContain('Test announcement');
    jest.useRealTimers();
  });

  it('handles keyboard navigation for Enter on button', () => {
    const btn = document.createElement('button');
    document.body.appendChild(btn);
    const event = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true });
    btn.dispatchEvent(event);
    // Should not throw, and activateElement is called
  });
}); 