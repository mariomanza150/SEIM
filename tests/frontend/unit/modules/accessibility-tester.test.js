import { AccessibilityTester } from '../../../../static/js/modules/accessibility-tester.js';

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

describe('AccessibilityTester', () => {
  let tester;
  beforeEach(() => {
    document.body.innerHTML = '';
    tester = new AccessibilityTester();
    jest.clearAllMocks();
  });

  it('runs the full accessibility test and returns results', async () => {
    // Add an image without alt text to trigger a failure
    const img = document.createElement('img');
    document.body.appendChild(img);
    const results = await tester.runFullTest();
    expect(results.failed.length).toBeGreaterThan(0);
    expect(results.summary.total).toBeGreaterThan(0);
    expect(results.summary.failed).toBeGreaterThan(0);
    expect(results.summary.passed).toBeGreaterThanOrEqual(0);
  });

  it('adds a passing result', () => {
    tester.addResult('1.1.1', 'Non-text Content', { passed: true });
    expect(tester.results.passed.length).toBe(1);
  });

  it('adds a failing result', () => {
    tester.addResult('1.1.1', 'Non-text Content', { passed: false, issues: ['fail'] });
    expect(tester.results.failed.length).toBe(1);
  });

  it('generates a summary after tests', () => {
    tester.addResult('1.1.1', 'Non-text Content', { passed: true });
    tester.addResult('1.3.1', 'Info and Relationships', { passed: false, issues: ['fail'] });
    tester.generateSummary();
    expect(tester.results.summary.total).toBe(2);
    expect(tester.results.summary.passed).toBe(1);
    expect(tester.results.summary.failed).toBe(1);
  });
}); 