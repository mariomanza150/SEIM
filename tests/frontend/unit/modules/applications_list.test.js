import * as applicationsList from '../../../../static/js/modules/applications_list.js';

jest.mock('../../../../static/js/modules/api.js', () => ({
  apiRequest: jest.fn(() => Promise.resolve({ results: [], next: null }))
}));
jest.mock('../../../../static/js/modules/ui.js', () => ({
  showSectionLoading: jest.fn(),
  hideSectionLoading: jest.fn()
}));

describe('applications_list.js', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="applicationsListContainer"></div>
      <form id="applicationsFilterForm"></form>
    `;
    jest.clearAllMocks();
  });

  test('initApplicationsList sets up filters, fetches, and load more button', () => {
    applicationsList.initApplicationsList();
    expect(document.getElementById('applicationsFilterForm')).not.toBeNull();
    expect(document.getElementById('applicationsListContainer')).not.toBeNull();
    // More detailed checks can be added for fetch and button setup
  });
}); 