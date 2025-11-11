import * as ui from '../../../../static/js/modules/ui.js';
import * as loading from '../../../../static/js/modules/ui/loading.js';
import * as auth_ui from '../../../../static/js/modules/ui/auth_ui.js';
import * as bootstrap_helpers from '../../../../static/js/modules/ui/bootstrap_helpers.js';

describe('ui.js re-exports', () => {
  it('should re-export all from loading, auth_ui, and bootstrap_helpers', () => {
    Object.keys(loading).forEach(key => {
      expect(ui[key]).toBe(loading[key]);
    });
    Object.keys(auth_ui).forEach(key => {
      expect(ui[key]).toBe(auth_ui[key]);
    });
    Object.keys(bootstrap_helpers).forEach(key => {
      expect(ui[key]).toBe(bootstrap_helpers[key]);
    });
  });
}); 