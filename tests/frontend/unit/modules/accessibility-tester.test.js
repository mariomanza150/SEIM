import { AccessibilityTester } from '../../../../static/js/modules/accessibility-tester.js';

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

describe('AccessibilityTester', () => {
  let tester;
  beforeEach(() => {
    mockMatchMedia();
    document.body.innerHTML = '';
    tester = new AccessibilityTester();
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