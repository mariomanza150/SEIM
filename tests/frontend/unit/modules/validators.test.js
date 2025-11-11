import * as validators from '../../../../static/js/modules/validators.js';

describe('validators.js', () => {
  test('should validate required fields', () => {
    const data = { a: 1 };
    const required = ['a', 'b'];
    const result = validators.validateRequiredFields(data, required);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Missing required field: b');
  });

  test('should validate email format', () => {
    expect(validators.validateEmail('test@example.com')).toBe(true);
    expect(validators.validateEmail('invalid')).toBe(false);
  });

  test('should validate password strength', () => {
    const weak = validators.validatePassword('abc');
    expect(weak.isValid).toBe(false);
    const strong = validators.validatePassword('Abcdef1!');
    expect(strong.isValid).toBe(true);
  });
}); 