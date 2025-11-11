import * as loading from '../../../../../static/js/modules/ui/loading.js';

describe('loading.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '<button id="btn">Click</button><div id="section"></div>';
  });

  test('setLoadingState disables and changes text', () => {
    const btn = document.getElementById('btn');
    loading.setLoadingState(btn, true, 'Loading...');
    expect(btn.disabled).toBe(true);
    expect(btn.textContent).toBe('Loading...');
    loading.setLoadingState(btn, false);
    expect(btn.disabled).toBe(false);
    expect(btn.textContent).toBe('Click');
  });

  test('setLoadingStates applies to multiple elements', () => {
    const btn = document.getElementById('btn');
    const btn2 = document.createElement('button');
    document.body.appendChild(btn2);
    loading.setLoadingStates([btn, btn2], true, 'Wait');
    expect(btn.disabled).toBe(true);
    expect(btn2.disabled).toBe(true);
    expect(btn.textContent).toBe('Wait');
    expect(btn2.textContent).toBe('Wait');
  });

  test('showPageLoading and hidePageLoading manipulate overlay', () => {
    loading.showPageLoading('Please wait');
    const overlay = document.getElementById('page-loading-overlay');
    expect(overlay).not.toBeNull();
    expect(overlay.style.display).toBe('flex');
    loading.hidePageLoading();
    expect(overlay.style.display).toBe('none');
  });

  test('showSectionLoading and hideSectionLoading manipulate section spinner', () => {
    const section = document.getElementById('section');
    loading.showSectionLoading('#section', 'Loading section');
    const spinner = section.querySelector('.section-loading-spinner');
    expect(spinner).not.toBeNull();
    expect(spinner.style.display).toBe('flex');
    loading.hideSectionLoading('#section');
    expect(spinner.style.display).toBe('none');
  });
}); 