import * as authUI from '../../../../../static/js/modules/ui/auth_ui.js';

describe('auth_ui.js', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div class="auth-only" style="display:none"></div>
      <div class="unauth-only" style="display:block"></div>
      <span class="user-username"></span>
      <span class="user-role"></span>
      <span class="user-email"></span>
      <div data-role="student" style="display:none"></div>
      <div data-role="admin" style="display:none"></div>
    `;
  });

  test('updateAuthUI shows auth-only and hides unauth-only', () => {
    authUI.updateAuthUI();
    expect(document.querySelector('.auth-only').style.display).toBe('block');
    expect(document.querySelector('.unauth-only').style.display).toBe('none');
  });

  test('updateUnauthUI hides auth-only and shows unauth-only', () => {
    authUI.updateUnauthUI();
    expect(document.querySelector('.auth-only').style.display).toBe('none');
    expect(document.querySelector('.unauth-only').style.display).toBe('block');
  });

  test('updateUserInterface updates user info and calls updateRoleBasedUI', () => {
    const userData = { username: 'test', role: 'student', email: 'test@example.com' };
    const spy = jest.spyOn(authUI, 'updateRoleBasedUI');
    authUI.updateUserInterface(userData);
    expect(document.querySelector('.user-username').textContent).toBe('test');
    expect(document.querySelector('.user-role').textContent).toBe('student');
    expect(document.querySelector('.user-email').textContent).toBe('test@example.com');
    expect(spy).toHaveBeenCalledWith('student');
  });

  test('updateRoleBasedUI shows only elements for the current role', () => {
    authUI.updateRoleBasedUI('admin');
    expect(document.querySelector('[data-role="admin"]').style.display).toBe('block');
    expect(document.querySelector('[data-role="student"]').style.display).toBe('none');
  });
}); 