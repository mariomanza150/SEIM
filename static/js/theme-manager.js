/**
 * SEIM Theme Manager
 * Handles dark mode toggle and theme persistence
 */

class ThemeManager {
    constructor() {
        this.themeKey = 'seim-theme';
        this.themeToggle = null;
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        
        // Add debugging
        console.log('ThemeManager: Constructor called');
        console.log('ThemeManager: Stored theme:', this.getStoredTheme());
        console.log('ThemeManager: System theme:', this.getSystemTheme());
        console.log('ThemeManager: Current theme:', this.currentTheme);
        
        this.init();
    }
    
    /**
     * Initialize the theme manager
     */
    init() {
        console.log('ThemeManager: Initializing...');
        this.applyTheme(this.currentTheme);
        this.createThemeToggle();
        this.setupEventListeners();
        this.updateToggleState();
        console.log('ThemeManager: Initialization complete');
    }
    
    /**
     * Get stored theme from localStorage
     */
    getStoredTheme() {
        try {
            const stored = localStorage.getItem(this.themeKey);
            console.log('ThemeManager: Retrieved from localStorage:', stored);
            return stored;
        } catch (error) {
            console.warn('Could not access localStorage:', error);
            return null;
        }
    }
    
    /**
     * Get system theme preference
     */
    getSystemTheme() {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        console.log('ThemeManager: System prefers dark mode:', isDark);
        return isDark ? 'dark' : 'light';
    }
    
    /**
     * Store theme preference
     */
    storeTheme(theme) {
        try {
            localStorage.setItem(this.themeKey, theme);
            console.log('ThemeManager: Stored theme in localStorage:', theme);
        } catch (error) {
            console.warn('Could not store theme preference:', error);
        }
    }
    
    /**
     * Apply theme to document
     */
    applyTheme(theme) {
        console.log('ThemeManager: Applying theme:', theme);
        const html = document.documentElement;
        
        // Remove existing theme classes
        html.removeAttribute('data-theme');
        
        // Apply new theme
        if (theme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            console.log('ThemeManager: Applied dark theme');
        } else {
            html.setAttribute('data-theme', 'light');
            console.log('ThemeManager: Applied light theme');
        }
        
        // Store preference
        this.storeTheme(theme);
        this.currentTheme = theme;
        
        // Update toggle button immediately
        this.updateToggleState();
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: theme } 
        }));
        
        // Add visual feedback
        this.showThemeFeedback(theme);
        
        console.log('ThemeManager: Theme application complete');
    }
    
    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        console.log('ThemeManager: Toggling theme from:', this.currentTheme);
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        console.log('ThemeManager: Toggling to:', newTheme);
        this.applyTheme(newTheme);
        this.updateToggleState();
    }
    
    /**
     * Find or create theme toggle button
     */
    createThemeToggle() {
        console.log('ThemeManager: Creating/finding theme toggle button...');
        
        // Check if toggle already exists in the DOM
        this.themeToggle = document.getElementById('theme-toggle');
        
        if (this.themeToggle) {
            console.log('ThemeManager: Found existing theme toggle button');
            // Button already exists in template, just set up event listener
            this.setupToggleEventListeners();
            return;
        }
        
        // Fallback: create button if not found in template
        console.log('ThemeManager: Creating fallback toggle button');
        const toggle = document.createElement('button');
        toggle.id = 'theme-toggle';
        toggle.className = 'btn btn-outline-secondary btn-sm theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle dark mode');
        toggle.setAttribute('title', 'Toggle dark mode');
        toggle.setAttribute('type', 'button');
        
        // Add icon
        const icon = document.createElement('i');
        icon.className = 'bi bi-moon-fill';
        toggle.appendChild(icon);
        
        // Try to add to the right side of the navbar (user menu area)
        const userMenu = document.querySelector('.navbar-nav.ms-auto');
        if (userMenu) {
            console.log('ThemeManager: Adding toggle button to navbar');
            // Insert before the user menu
            const navItem = document.createElement('li');
            navItem.className = 'nav-item me-2';
            navItem.appendChild(toggle);
            userMenu.parentNode.insertBefore(navItem, userMenu);
        } else {
            console.log('ThemeManager: Adding toggle button to body (fallback)');
            // Fallback: add to body if navbar not found
            toggle.style.position = 'fixed';
            toggle.style.top = '20px';
            toggle.style.right = '20px';
            toggle.style.zIndex = '1000';
            document.body.appendChild(toggle);
        }
        
        this.themeToggle = toggle;
        this.setupToggleEventListeners();
    }
    
    /**
     * Update toggle button state
     */
    updateToggleState() {
        if (!this.themeToggle) {
            console.warn('ThemeManager: No toggle button found for state update');
            return;
        }
        
        const icon = this.themeToggle.querySelector('i');
        const isDark = this.currentTheme === 'dark';
        
        console.log('ThemeManager: Updating toggle state, isDark:', isDark);
        
        // Update icon
        icon.className = isDark ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        
        // Update aria-label
        this.themeToggle.setAttribute('aria-label', 
            isDark ? 'Switch to light mode' : 'Switch to dark mode'
        );
        
        // Update title
        this.themeToggle.setAttribute('title', 
            isDark ? 'Switch to light mode' : 'Switch to dark mode'
        );
    }
    
    /**
     * Setup toggle button event listeners
     */
    setupToggleEventListeners() {
        if (this.themeToggle) {
            console.log('ThemeManager: Setting up toggle event listeners');
            this.themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('ThemeManager: Toggle button clicked');
                this.toggleTheme();
            });
        } else {
            console.warn('ThemeManager: No toggle button for event listeners');
        }
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // System theme change
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            // Only apply system theme if no manual preference is stored
            if (!this.getStoredTheme()) {
                const newTheme = e.matches ? 'dark' : 'light';
                console.log('ThemeManager: System theme changed to:', newTheme);
                this.applyTheme(newTheme);
                this.updateToggleState();
            }
        });
        
        // Keyboard shortcut (Ctrl/Cmd + Shift + T)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                console.log('ThemeManager: Keyboard shortcut triggered');
                this.toggleTheme();
            }
        });
    }
    
    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    /**
     * Check if dark mode is active
     */
    isDarkMode() {
        return this.currentTheme === 'dark';
    }
    
    /**
     * Show visual feedback when theme changes
     */
    showThemeFeedback(theme) {
        // Find the existing feedback element in the navbar
        const feedback = document.getElementById('theme-feedback');
        
        if (!feedback) {
            console.warn('ThemeManager: Feedback element not found');
            return;
        }
        
        // Update feedback content
        feedback.textContent = theme === 'dark' ? '🌙 Dark Mode' : '☀️ Light Mode';
        
        // Show feedback with animation
        feedback.style.display = 'block';
        
        // Trigger animation by adding show class
        setTimeout(() => {
            feedback.classList.add('show');
        }, 10);
        
        // Hide feedback after 2 seconds
        setTimeout(() => {
            feedback.classList.remove('show');
            setTimeout(() => {
                feedback.style.display = 'none';
            }, 300);
        }, 2000);
    }
    
    /**
     * Force refresh theme (useful after dynamic content changes)
     */
    refresh() {
        console.log('ThemeManager: Refreshing theme');
        this.applyTheme(this.currentTheme);
    }
    
    /**
     * Reset theme to system preference
     */
    resetToSystem() {
        console.log('ThemeManager: Resetting to system preference');
        localStorage.removeItem(this.themeKey);
        const systemTheme = this.getSystemTheme();
        this.applyTheme(systemTheme);
    }
    
    /**
     * Force light mode
     */
    forceLight() {
        console.log('ThemeManager: Forcing light mode');
        this.applyTheme('light');
    }
    
    /**
     * Force dark mode
     */
    forceDark() {
        console.log('ThemeManager: Forcing dark mode');
        this.applyTheme('dark');
    }
    
    /**
     * Emergency theme reset - clears all theme-related localStorage and forces light mode
     */
    emergencyReset() {
        console.log('ThemeManager: Emergency reset initiated');
        
        try {
            // Clear all theme-related localStorage keys
            const allKeys = Object.keys(localStorage);
            const themeKeys = allKeys.filter(key => key.toLowerCase().includes('theme'));
            
            themeKeys.forEach(key => {
                localStorage.removeItem(key);
                console.log('ThemeManager: Removed localStorage key:', key);
            });
            
            // Force light mode
            this.applyTheme('light');
            
            // Reload page to ensure clean state
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } catch (error) {
            console.error('ThemeManager: Emergency reset failed:', error);
        }
    }
    
    /**
     * Debug theme state
     */
    debug() {
        console.log('=== Theme Manager Debug ===');
        console.log('Current theme:', this.currentTheme);
        console.log('Stored theme:', this.getStoredTheme());
        console.log('System theme:', this.getSystemTheme());
        console.log('Is dark mode:', this.isDarkMode());
        console.log('Toggle button found:', !!this.themeToggle);
        console.log('HTML data-theme:', document.documentElement.getAttribute('data-theme'));
        console.log('localStorage keys:', Object.keys(localStorage).filter(key => key.toLowerCase().includes('theme')));
        console.log('=== End Debug ===');
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('ThemeManager: DOM loaded, initializing...');
    window.themeManager = new ThemeManager();
});

// Add global utility functions
window.SEIMThemeUtils = {
    /**
     * Emergency reset function - can be called from browser console
     */
    emergencyReset: function() {
        if (window.themeManager) {
            window.themeManager.emergencyReset();
        } else {
            console.error('Theme manager not available');
        }
    },
    
    /**
     * Debug function - can be called from browser console
     */
    debug: function() {
        if (window.themeManager) {
            window.themeManager.debug();
        } else {
            console.error('Theme manager not available');
        }
    },
    
    /**
     * Force light mode - can be called from browser console
     */
    forceLight: function() {
        if (window.themeManager) {
            window.themeManager.forceLight();
        } else {
            console.error('Theme manager not available');
        }
    },
    
    /**
     * Force dark mode - can be called from browser console
     */
    forceDark: function() {
        if (window.themeManager) {
            window.themeManager.forceDark();
        } else {
            console.error('Theme manager not available');
        }
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
} 