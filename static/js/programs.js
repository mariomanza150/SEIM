// Import security utilities first to ensure they're available
import './modules/security.js';
import { initializeTooltips, initializeModals } from './modules/ui.js';
import { initProgramsList } from './modules/programs_list.js';

document.addEventListener('DOMContentLoaded', async () => {
    initializeTooltips();
    initializeModals();
    initProgramsList();
}); 