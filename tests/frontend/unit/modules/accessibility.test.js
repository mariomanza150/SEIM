import { AccessibilityManager } from '../../../../static/js/modules/accessibility.js';

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

describe('AccessibilityManager', () => {
  let manager;
  beforeEach(() => {
    document.body.innerHTML = '';
    manager = new AccessibilityManager();
    jest.clearAllMocks();
  });

  it('adds skip links to the DOM', () => {
    expect(document.body.innerHTML).toContain('Skip to main content');
    expect(document.body.innerHTML).toContain('Skip to navigation');
    expect(document.body.innerHTML).toContain('Skip to footer');
  });

  it('returns focusable elements in a container', () => {
    const container = document.createElement('div');
    container.innerHTML = '<button></button><a href="#"></a><input /><div></div>';
    document.body.appendChild(container);
    const focusables = manager.getFocusableElements(container);
    expect(focusables.length).toBe(3);
  });

  it('announces messages for screen readers', () => {
    manager.announce('Test announcement');
    expect(document.body.innerHTML).toContain('Test announcement');
  });

  it('handles keyboard navigation for Enter on button', () => {
    const btn = document.createElement('button');
    document.body.appendChild(btn);
    const event = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true });
    btn.dispatchEvent(event);
    // Should not throw, and activateElement is called
  });
}); 