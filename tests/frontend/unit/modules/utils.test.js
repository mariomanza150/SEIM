import * as utils from '../../../../static/js/modules/utils.js';

describe('utils.js', () => {
  test('should format file size', () => {
    expect(utils.formatFileSize(0)).toBe('0 Bytes');
    expect(utils.formatFileSize(1024)).toBe('1 KB');
  });

  test('should format date', () => {
    const date = '2024-01-01T00:00:00Z';
    expect(typeof utils.formatDate(date)).toBe('string');
  });

  test('should format currency', () => {
    expect(utils.formatCurrency(100)).toMatch(/\$/);
  });
}); 