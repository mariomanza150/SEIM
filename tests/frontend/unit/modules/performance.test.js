import { performanceMonitor } from '../../../../static/js/modules/performance.js';

describe('performance.js', () => {
  test('should track and report API call performance', () => {
    const start = Date.now();
    const end = start + 100;
    const apiCall = performanceMonitor.trackApiCall('/test', 'GET', start, end, 200);
    expect(apiCall).toHaveProperty('url', '/test');
    expect(apiCall).toHaveProperty('method', 'GET');
    expect(apiCall).toHaveProperty('duration', 100);
  });

  test('should track errors', () => {
    performanceMonitor.trackError(new Error('fail'));
    expect(performanceMonitor.metrics.errors.length).toBeGreaterThan(0);
  });
}); 