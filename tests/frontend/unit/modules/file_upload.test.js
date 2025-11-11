import * as fileUpload from '../../../../static/js/modules/file_upload.js';

describe('file_upload.js', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div class="file-upload-area">
        <input type="file" />
        <div class="file-display"></div>
      </div>
    `;
  });

  test('initializeFileUpload sets up event listeners', () => {
    fileUpload.initializeFileUpload();
    const area = document.querySelector('.file-upload-area');
    expect(area).not.toBeNull();
    // More detailed event simulation can be added
  });

  test('updateFileUploadDisplay shows file info', () => {
    const area = document.querySelector('.file-upload-area');
    const files = [{ name: 'test.txt', size: 123 }];
    fileUpload.updateFileUploadDisplay(area, files);
    expect(area.querySelector('.file-display').textContent).toMatch(/test.txt/);
  });
}); 