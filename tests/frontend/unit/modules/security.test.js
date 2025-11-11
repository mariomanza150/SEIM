import { SecurityUtils } from '../../../../static/js/modules/security.js';

describe('security.js', () => {
  test('should sanitize input', () => {
    const dirty = '<script>alert(1)</script>';
    const clean = SecurityUtils.sanitizeInput(dirty);
    expect(clean).not.toMatch(/<script>/);
  });

  test('should validate and sanitize email', () => {
    expect(() => SecurityUtils.validateAndSanitizeEmail('bad')).toThrow();
    expect(SecurityUtils.validateAndSanitizeEmail('test@example.com')).toBe('test@example.com');
  });
}); 