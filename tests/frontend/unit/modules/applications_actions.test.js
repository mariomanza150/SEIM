import * as actions from '../../../../static/js/modules/applications_actions.js';
import { apiRequest } from '../../../../static/js/modules/api.js';
import {
  showConfirmDialog,
  showSuccessAlert,
} from '../../../../static/js/modules/notifications.js';

jest.mock('../../../../static/js/modules/api.js', () => ({
  apiRequest: jest.fn(() => Promise.resolve({ id: 1, user_name: 'You' }))
}));
jest.mock('../../../../static/js/modules/notifications.js', () => ({
  showConfirmDialog: jest.fn(() => Promise.resolve({ isConfirmed: true })),
  showSuccessAlert: jest.fn(),
  showErrorAlert: jest.fn()
}));
jest.mock('../../../../static/js/modules/logger.js', () => ({
  logger: { info: jest.fn(), warn: jest.fn(), debug: jest.fn(), error: jest.fn() },
  Logger: jest.fn(),
  LOG_LEVELS: { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3, NONE: 4 },
}));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({
  errorHandler: { handleError: jest.fn(), handleApiError: jest.fn(), showError: jest.fn() },
  ErrorHandler: jest.fn(),
}));

describe('applications_actions.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="commentsContainer"></div>';
    jest.clearAllMocks();
    showConfirmDialog.mockResolvedValue({ isConfirmed: true });
    apiRequest.mockResolvedValue({ id: 1, user_name: 'You' });
  });

  test('submitApplication calls API and shows success', async () => {
    await actions.submitApplication(1);
    expect(apiRequest).toHaveBeenCalled();
    expect(showSuccessAlert).toHaveBeenCalled();
  });

  test('withdrawApplication calls API and shows success', async () => {
    await actions.withdrawApplication(1);
    expect(apiRequest).toHaveBeenCalled();
    expect(showSuccessAlert).toHaveBeenCalled();
  });

  test('deleteComment calls API and removes comment from DOM', async () => {
    const comment = document.createElement('div');
    comment.setAttribute('data-comment-id', '1');
    document.body.appendChild(comment);
    await actions.deleteComment(1);
    expect(apiRequest).toHaveBeenCalled();
    expect(document.querySelector('[data-comment-id="1"]')).toBeNull();
  });

  test('addComment calls API and adds comment to DOM', async () => {
    const container = document.getElementById('commentsContainer');
    await actions.addComment(1, 'Test comment');
    expect(apiRequest).toHaveBeenCalled();
    expect(container.childNodes.length).toBeGreaterThan(0);
  });
});
