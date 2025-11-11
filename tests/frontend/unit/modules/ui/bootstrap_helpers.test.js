import * as bootstrapHelpers from '../../../../../static/js/modules/ui/bootstrap_helpers.js';

global.IntersectionObserver = class {
  constructor(cb) { this.cb = cb; }
  observe(el) { this.cb([{ isIntersecting: true, target: el }]); }
  disconnect() {}
};
global.bootstrap = { Tooltip: jest.fn(), Modal: jest.fn() };

describe('bootstrap_helpers.js', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div data-bs-toggle="tooltip"></div>
      <div data-bs-toggle="modal"></div>
    `;
    jest.clearAllMocks();
  });

  test('initializeTooltips attaches tooltips', () => {
    bootstrapHelpers.initializeTooltips();
    expect(global.bootstrap.Tooltip).toHaveBeenCalled();
  });

  test('initializeModals attaches modals', () => {
    bootstrapHelpers.initializeModals();
    expect(global.bootstrap.Modal).toHaveBeenCalled();
  });
}); 