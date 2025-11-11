import * as notifications from '../../../../static/js/modules/notifications.js';

jest.mock('sweetalert2', () => ({
  fire: jest.fn(() => Promise.resolve()),
  showLoading: jest.fn(),
  close: jest.fn()
}));

describe('notifications.js', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('showAlert calls Swal.fire', () => {
    notifications.showAlert('msg');
    expect(require('sweetalert2').fire).toHaveBeenCalled();
  });

  test('showSuccessAlert calls showAlert with success', () => {
    const spy = jest.spyOn(notifications, 'showAlert');
    notifications.showSuccessAlert('title', 'msg');
    expect(spy).toHaveBeenCalledWith('msg', 'success', 'title');
  });

  test('showErrorAlert calls showAlert with error', () => {
    const spy = jest.spyOn(notifications, 'showAlert');
    notifications.showErrorAlert('title', 'msg');
    expect(spy).toHaveBeenCalledWith('msg', 'error', 'title');
  });

  test('showWarningAlert calls showAlert with warning', () => {
    const spy = jest.spyOn(notifications, 'showAlert');
    notifications.showWarningAlert('title', 'msg');
    expect(spy).toHaveBeenCalledWith('msg', 'warning', 'title');
  });

  test('showConfirmDialog calls Swal.fire', () => {
    notifications.showConfirmDialog('title', 'text');
    expect(require('sweetalert2').fire).toHaveBeenCalled();
  });

  test('showLoadingAlert calls Swal.fire and showLoading', () => {
    notifications.showLoadingAlert('Loading...');
    expect(require('sweetalert2').fire).toHaveBeenCalled();
    expect(require('sweetalert2').showLoading).toHaveBeenCalled();
  });

  test('closeAlert calls Swal.close', () => {
    notifications.closeAlert();
    expect(require('sweetalert2').close).toHaveBeenCalled();
  });
}); 