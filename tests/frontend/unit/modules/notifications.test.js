import * as notifications from '../../../../static/js/modules/notifications.js';

jest.mock('sweetalert2', () => {
  const fire = jest.fn((opts) => {
    if (opts && typeof opts.didOpen === 'function') {
      opts.didOpen();
    }
    return Promise.resolve();
  });
  return {
    __esModule: true,
    default: {
      fire,
      showLoading: jest.fn(),
      close: jest.fn(),
    },
  };
});

jest.mock('../../../../static/js/modules/logger.js', () => ({
  logger: { info: jest.fn(), error: jest.fn() },
}));

jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleApiError: jest.fn() },
}));

describe('notifications.js', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('showAlert calls Swal.fire', () => {
    notifications.showAlert('msg');
    expect(require('sweetalert2').default.fire).toHaveBeenCalled();
  });

  test('showSuccessAlert calls Swal.fire with success', () => {
    notifications.showSuccessAlert('title', 'msg');
    expect(require('sweetalert2').default.fire).toHaveBeenCalledWith(
      expect.objectContaining({ text: 'msg', icon: 'success', title: 'title' })
    );
  });

  test('showErrorAlert calls Swal.fire with error', () => {
    notifications.showErrorAlert('title', 'msg');
    expect(require('sweetalert2').default.fire).toHaveBeenCalledWith(
      expect.objectContaining({ text: 'msg', icon: 'error', title: 'title' })
    );
  });

  test('showWarningAlert calls Swal.fire with warning', () => {
    notifications.showWarningAlert('title', 'msg');
    expect(require('sweetalert2').default.fire).toHaveBeenCalledWith(
      expect.objectContaining({ text: 'msg', icon: 'warning', title: 'title' })
    );
  });

  test('showConfirmDialog calls Swal.fire', () => {
    notifications.showConfirmDialog('title', 'text');
    expect(require('sweetalert2').default.fire).toHaveBeenCalled();
  });

  test('showLoadingAlert calls Swal.fire', () => {
    notifications.showLoadingAlert('Loading...');
    expect(require('sweetalert2').default.fire).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Loading...', allowOutsideClick: false })
    );
  });

  test('closeAlert calls Swal.close', () => {
    notifications.closeAlert();
    expect(require('sweetalert2').default.close).toHaveBeenCalled();
  });
});
