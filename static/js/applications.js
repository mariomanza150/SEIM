// Import security utilities first to ensure they're available
import './modules/security.js';
import { initializeTooltips, initializeModals } from './modules/ui.js';
import { initializeFileUpload } from './modules/file_upload.js';
import { initApplicationsList } from './modules/applications_list.js';
import './modules/applications_actions.js'; // Import application actions

// Applications page initialization

document.addEventListener('DOMContentLoaded', async () => {
    initializeTooltips();
    initializeModals();
    initializeFileUpload();
    initApplicationsList();
}); 