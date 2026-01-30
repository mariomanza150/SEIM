/**
 * Preferences Manager
 * 
 * Manages user preferences for theme, font size, and accessibility options
 */

class PreferencesManager {
    constructor() {
        this.preferences = {
            theme: 'auto',
            fontSize: 'normal',
            highContrast: false,
            reduceMotion: false
        };
        
        this.init();
    }
    
    /**
     * Initialize preferences manager
     */
    init() {
        this.loadPreferences();
        this.applyPreferences();
        this.attachEventListeners();
    }
    
    /**
     * Load preferences from localStorage and API
     */
    async loadPreferences() {
        // Load from localStorage first (immediate)
        const stored = localStorage.getItem('user_preferences');
        if (stored) {
            try {
                this.preferences = JSON.parse(stored);
            } catch (error) {
                console.error('Error parsing stored preferences:', error);
            }
        }
        
        // Then sync with API
        await this.syncWithAPI();
        
        // Update form fields
        this.updateFormFields();
    }
    
    /**
     * Sync preferences with API
     */
    async syncWithAPI() {
        try {
            const token = localStorage.getItem('seim_access_token');
            if (!token) return;
            
            const response = await fetch('/api/user-settings/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) return;
            
            const data = await response.json();
            
            // Map API data to our preferences
            if (data.theme) this.preferences.theme = data.theme;
            if (data.font_size) this.preferences.fontSize = data.font_size;
            if (data.high_contrast !== undefined) this.preferences.highContrast = data.high_contrast;
            if (data.reduce_motion !== undefined) this.preferences.reduceMotion = data.reduce_motion;
            
            // Save to localStorage
            this.saveToLocalStorage();
            
        } catch (error) {
            console.error('Error syncing preferences:', error);
        }
    }
    
    /**
     * Update form fields with current preferences
     */
    updateFormFields() {
        // Theme
        const themeRadio = document.querySelector(`input[name="theme"][value="${this.preferences.theme}"]`);
        if (themeRadio) themeRadio.checked = true;
        
        // Font Size
        const fontRadio = document.querySelector(`input[name="fontSize"][value="${this.preferences.fontSize}"]`);
        if (fontRadio) fontRadio.checked = true;
        
        // High Contrast
        const highContrastCheckbox = document.getElementById('highContrast');
        if (highContrastCheckbox) highContrastCheckbox.checked = this.preferences.highContrast;
        
        // Reduce Motion
        const reduceMotionCheckbox = document.getElementById('reduceMotion');
        if (reduceMotionCheckbox) reduceMotionCheckbox.checked = this.preferences.reduceMotion;
    }
    
    /**
     * Apply preferences to the DOM
     */
    applyPreferences() {
        // Apply theme
        this.applyTheme(this.preferences.theme);
        
        // Apply font size
        this.applyFontSize(this.preferences.fontSize);
        
        // Apply high contrast
        if (this.preferences.highContrast) {
            document.body.setAttribute('data-accessibility', 'high-contrast');
        } else {
            document.body.removeAttribute('data-accessibility');
        }
        
        // Apply reduce motion
        if (this.preferences.reduceMotion) {
            document.body.setAttribute('data-reduce-motion', 'true');
        } else {
            document.body.removeAttribute('data-reduce-motion');
        }
    }
    
    /**
     * Apply theme
     */
    applyTheme(theme) {
        if (theme === 'auto') {
            // Use system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }
        
        // Store for theme manager compatibility
        localStorage.setItem('seim-theme', theme);
    }
    
    /**
     * Apply font size
     */
    applyFontSize(fontSize) {
        // Remove existing font size classes
        document.body.removeAttribute('data-font-size');
        
        if (fontSize !== 'normal') {
            document.body.setAttribute('data-font-size', fontSize);
        }
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Theme radio buttons
        document.querySelectorAll('input[name="theme"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.preferences.theme = e.target.value;
                this.applyTheme(this.preferences.theme);
                this.saveToLocalStorage();
            });
        });
        
        // Font size radio buttons
        document.querySelectorAll('input[name="fontSize"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.preferences.fontSize = e.target.value;
                this.applyFontSize(this.preferences.fontSize);
                this.saveToLocalStorage();
            });
        });
        
        // High contrast checkbox
        const highContrastCheckbox = document.getElementById('highContrast');
        if (highContrastCheckbox) {
            highContrastCheckbox.addEventListener('change', (e) => {
                this.preferences.highContrast = e.target.checked;
                this.applyPreferences();
                this.saveToLocalStorage();
            });
        }
        
        // Reduce motion checkbox
        const reduceMotionCheckbox = document.getElementById('reduceMotion');
        if (reduceMotionCheckbox) {
            reduceMotionCheckbox.addEventListener('change', (e) => {
                this.preferences.reduceMotion = e.target.checked;
                this.applyPreferences();
                this.saveToLocalStorage();
            });
        }
        
        // Save button
        const saveBtn = document.getElementById('saveBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveToAPI());
        }
        
        // Reset button
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetToDefaults());
        }
    }
    
    /**
     * Save to localStorage
     */
    saveToLocalStorage() {
        localStorage.setItem('user_preferences', JSON.stringify(this.preferences));
    }
    
    /**
     * Save to API
     */
    async saveToAPI() {
        try {
            this.showLoading();
            
            const token = localStorage.getItem('seim_access_token');
            if (!token) {
                throw new Error('Not authenticated');
            }
            
            const response = await fetch('/api/user-settings/', {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    theme: this.preferences.theme,
                    font_size: this.preferences.fontSize,
                    high_contrast: this.preferences.highContrast,
                    reduce_motion: this.preferences.reduceMotion
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to save preferences');
            }
            
            this.saveToLocalStorage();
            this.showSuccess('Preferences saved successfully');
            
        } catch (error) {
            console.error('Error saving preferences:', error);
            this.showError('Failed to save preferences');
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * Reset to defaults
     */
    resetToDefaults() {
        if (!confirm('Reset all preferences to defaults?')) {
            return;
        }
        
        this.preferences = {
            theme: 'auto',
            fontSize: 'normal',
            highContrast: false,
            reduceMotion: false
        };
        
        this.updateFormFields();
        this.applyPreferences();
        this.saveToLocalStorage();
        this.saveToAPI();
    }
    
    /**
     * Show loading overlay
     */
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('d-none');
        }
    }
    
    /**
     * Hide loading overlay
     */
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('d-none');
        }
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        if (window.toastNotifications) {
            window.toastNotifications.success('Success', message);
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        if (window.toastNotifications) {
            window.toastNotifications.error('Error', message);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PreferencesManager;
}

// Make available globally
window.PreferencesManager = PreferencesManager;

