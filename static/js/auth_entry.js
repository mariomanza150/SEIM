// Import security utilities first to ensure they're available
import './modules/security.js';
import { initializeTooltips, initializeModals } from './modules/ui.js';
import * as Auth from './modules/auth.js';

// Auth page initialization

document.addEventListener('DOMContentLoaded', async () => {
    initializeTooltips();
    initializeModals();
    
    // Initialize auth forms and logic
    Auth.setupAuthForms();
    
    // Initialize login page specific functionality
    initializeLoginPage();
});

/**
 * Initialize login page specific functionality
 */
function initializeLoginPage() {
    // Toggle password visibility
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');
    
    if (togglePassword && password) {
        togglePassword.addEventListener('click', function() {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            icon.classList.toggle('bi-eye');
            icon.classList.toggle('bi-eye-slash');
        });
    }
    
    // Auto-focus on username field
    const usernameField = document.getElementById('username');
    if (usernameField) {
        usernameField.focus();
    }
} 