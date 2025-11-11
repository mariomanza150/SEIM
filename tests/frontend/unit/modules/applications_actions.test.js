import * as actions from '../../../../static/js/modules/applications_actions.js';

jest.mock('../../../../static/js/modules/api.js', () => ({
  apiRequest: jest.fn(() => Promise.resolve({ id: 1, user_name: 'You' }))
}));
jest.mock('../../../../static/js/modules/notifications.js', () => ({
  showConfirmDialog: jest.fn(() => Promise.resolve({ isConfirmed: true })),
  showSuccessAlert: jest.fn(),
  showErrorAlert: jest.fn()
}));
jest.mock('../../../../static/js/modules/logger.js', () => ({ logger: { error: jest.fn() } }));
jest.mock('../../../../static/js/modules/error-handler.js', () => ({ errorHandler: { handleApiError: jest.fn() } }));

describe('applications_actions.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="commentsContainer"></div>';
    jest.clearAllMocks();
  });

  test('submitApplication calls API and shows success', async () => {
    await actions.submitApplication(1);
    expect(require('../../../../../static/js/modules/api.js').apiRequest).toHaveBeenCalled();
    expect(require('../../../../../static/js/modules/notifications.js').showSuccessAlert).toHaveBeenCalled();
  });

  test('withdrawApplication calls API and shows success', async () => {
    await actions.withdrawApplication(1);
    expect(require('../../../../../static/js/modules/api.js').apiRequest).toHaveBeenCalled();
    expect(require('../../../../../static/js/modules/notifications.js').showSuccessAlert).toHaveBeenCalled();
  });

  test('deleteComment calls API and removes comment from DOM', async () => {
    const comment = document.createElement('div');
    comment.setAttribute('data-comment-id', '1');
    document.body.appendChild(comment);
    await actions.deleteComment(1);
    expect(require('../../../../../static/js/modules/api.js').apiRequest).toHaveBeenCalled();
    expect(document.querySelector('[data-comment-id="1"]')).toBeNull();
  });

  test('addComment calls API and adds comment to DOM', async () => {
    const container = document.getElementById('commentsContainer');
    await actions.addComment(1, 'Test comment');
    expect(require('../../../../../static/js/modules/api.js').apiRequest).toHaveBeenCalled();
    expect(container.childNodes.length).toBeGreaterThan(0);
  });
}); 