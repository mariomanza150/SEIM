import * as applications from '../../../static/js/applications.js';

jest.mock('../../../static/js/modules/ui.js', () => ({
  initializeTooltips: jest.fn(),
  initializeModals: jest.fn()
}));
jest.mock('../../../static/js/modules/file_upload.js', () => ({
  initializeFileUpload: jest.fn()
}));
jest.mock('../../../static/js/modules/applications_list.js', () => ({
  initApplicationsList: jest.fn()
}));

describe('applications.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
  });

  test('should call initialization functions on DOMContentLoaded', () => {
    document.dispatchEvent(new Event('DOMContentLoaded'));
    const { initializeTooltips } = require('../../../static/js/modules/ui.js');
    const { initializeModals } = require('../../../static/js/modules/ui.js');
    const { initializeFileUpload } = require('../../../static/js/modules/file_upload.js');
    const { initApplicationsList } = require('../../../static/js/modules/applications_list.js');
    expect(initializeTooltips).toHaveBeenCalled();
    expect(initializeModals).toHaveBeenCalled();
    expect(initializeFileUpload).toHaveBeenCalled();
    expect(initApplicationsList).toHaveBeenCalled();
  });
}); 