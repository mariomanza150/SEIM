// Import security utilities first to ensure they're available
import './modules/security.js';
import { initializeTooltips, initializeModals } from './modules/ui.js';
import { initializeFileUpload } from './modules/file_upload.js';
import { initDocumentsList } from './modules/documents_list.js';

document.addEventListener('DOMContentLoaded', async () => {
    initializeTooltips();
    initializeModals();
    initializeFileUpload();
    initDocumentsList();
}); 