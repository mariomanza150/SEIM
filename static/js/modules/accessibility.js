/**
 * SEIM Accessibility Module
 * Provides comprehensive accessibility features including ARIA management,
 * keyboard navigation, focus handling, and screen reader support
 */

import { logger } from './logger.js';
import { errorHandler } from './error-handler.js';

class AccessibilityManager {
    constructor() {
        this.focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        this.currentFocusIndex = 0;
        this.focusableElementsList = [];
        this.skipLinks = [];
        this.modalStack = [];
        this.announcements = [];
        
        this.config = {
            enableKeyboardNavigation: true,
            enableSkipLinks: true,
            enableFocusTrapping: true,
            enableAnnouncements: true,
            enableHighContrast: true,
            enableReducedMotion: true,
            announcementDelay: 100
        };
        
        this.init();
    }
    
    init() {
        this.setupKeyboardNavigation();
        this.setupSkipLinks();
        this.setupFocusManagement();
        this.setupAnnouncements();
        this.setupHighContrast();
        this.setupReducedMotion();
        this.setupFormAccessibility();
        
        logger.info('Accessibility Manager initialized');
    }
    
    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        if (!this.config.enableKeyboardNavigation) return;
        
        document.addEventListener('keydown', (event) => {
            this.handleKeyboardNavigation(event);
        });
        
        // Setup tab navigation
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Tab') {
                this.handleTabNavigation(event);
            }
        });
        
        // Setup escape key for modals
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.handleEscapeKey(event);
            }
        });
    }
    
    /**
     * Handle keyboard navigation
     */
    handleKeyboardNavigation(event) {
        const target = event.target;
        const isFormElement = target.matches('input, select, textarea');
        
        // Handle form navigation
        if (isFormElement) {
            this.handleFormNavigation(event);
            return;
        }
        
        // Handle custom keyboard shortcuts
        switch (event.key) {
            case 'Enter':
            case ' ':
                if (target.matches('button, [role="button"], [tabindex]')) {
                    event.preventDefault();
                    this.activateElement(target);
                }
                break;
                
            case 'ArrowUp':
            case 'ArrowDown':
                if (target.matches('[role="listbox"], [role="menu"]')) {
                    event.preventDefault();
                    this.handleListNavigation(event);
                }
                break;
                
            case 'Home':
            case 'End':
                if (target.matches('[role="listbox"], [role="menu"]')) {
                    event.preventDefault();
                    this.handleListNavigation(event);
                }
                break;
        }
    }
    
    /**
     * Handle tab navigation
     */
    handleTabNavigation(event) {
        const focusableElements = this.getFocusableElements();
        
        if (event.shiftKey) {
            // Tab backwards
            if (document.activeElement === focusableElements[0]) {
                event.preventDefault();
                focusableElements[focusableElements.length - 1].focus();
            }
        } else {
            // Tab forwards
            if (document.activeElement === focusableElements[focusableElements.length - 1]) {
                event.preventDefault();
                focusableElements[0].focus();
            }
        }
    }
    
    /**
     * Handle escape key
     */
    handleEscapeKey(event) {
        // Close modals
        const openModals = document.querySelectorAll('[role="dialog"][aria-hidden="false"]');
        if (openModals.length > 0) {
            const lastModal = openModals[openModals.length - 1];
            this.closeModal(lastModal);
            event.preventDefault();
            return;
        }
        
        // Close dropdowns
        const openDropdowns = document.querySelectorAll('[role="menu"][aria-expanded="true"]');
        if (openDropdowns.length > 0) {
            const lastDropdown = openDropdowns[openDropdowns.length - 1];
            this.closeDropdown(lastDropdown);
            event.preventDefault();
        }
    }
    
    /**
     * Handle form navigation
     */
    handleFormNavigation(event) {
        const form = event.target.closest('form');
        if (!form) return;
        
        const formElements = Array.from(form.querySelectorAll(this.focusableElements));
        const currentIndex = formElements.indexOf(event.target);
        
        switch (event.key) {
            case 'Enter':
                if (event.target.type === 'submit') {
                    // Let the default submit happen
                    return;
                }
                // Move to next field
                event.preventDefault();
                if (currentIndex < formElements.length - 1) {
                    formElements[currentIndex + 1].focus();
                }
                break;
                
            case 'ArrowUp':
            case 'ArrowDown':
                if (event.target.type === 'number' || event.target.type === 'range') {
                    // Let the default behavior happen
                    return;
                }
                event.preventDefault();
                const direction = event.key === 'ArrowUp' ? -1 : 1;
                const nextIndex = currentIndex + direction;
                if (nextIndex >= 0 && nextIndex < formElements.length) {
                    formElements[nextIndex].focus();
                }
                break;
        }
    }
    
    /**
     * Handle list navigation
     */
    handleListNavigation(event) {
        const list = event.target;
        const items = Array.from(list.querySelectorAll('[role="option"], [role="menuitem"]'));
        const currentItem = list.querySelector('[aria-selected="true"]') || items[0];
        const currentIndex = items.indexOf(currentItem);
        
        let nextIndex = currentIndex;
        
        switch (event.key) {
            case 'ArrowUp':
                nextIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
                break;
            case 'ArrowDown':
                nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
                break;
            case 'Home':
                nextIndex = 0;
                break;
            case 'End':
                nextIndex = items.length - 1;
                break;
        }
        
        if (items[nextIndex]) {
            this.selectListItem(items[nextIndex], items);
        }
    }
    
    /**
     * Setup skip links
     */
    setupSkipLinks() {
        if (!this.config.enableSkipLinks) return;
        
        // Create skip links
        const skipLinks = [
            { href: '#main-content', text: 'Skip to main content' },
            { href: '#navigation', text: 'Skip to navigation' },
            { href: '#footer', text: 'Skip to footer' }
        ];
        
        const skipLinksContainer = document.createElement('div');
        skipLinksContainer.className = 'skip-links';
        skipLinksContainer.setAttribute('role', 'navigation');
        skipLinksContainer.setAttribute('aria-label', 'Skip links');
        
        skipLinks.forEach(link => {
            const skipLink = document.createElement('a');
            skipLink.href = link.href;
            skipLink.textContent = link.text;
            skipLink.className = 'skip-link';
            skipLink.setAttribute('tabindex', '0');
            
            skipLink.addEventListener('click', (event) => {
                event.preventDefault();
                const target = document.querySelector(link.href);
                if (target) {
                    target.focus();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
            
            skipLinksContainer.appendChild(skipLink);
        });
        
        // Insert at the beginning of the body
        document.body.insertBefore(skipLinksContainer, document.body.firstChild);
        
        // Add CSS for skip links
        this.addSkipLinksCSS();
    }
    
    /**
     * Add CSS for skip links
     */
    addSkipLinksCSS() {
        const style = document.createElement('style');
        style.textContent = `
            .skip-links {
                position: absolute;
                top: -40px;
                left: 6px;
                z-index: 1000;
            }
            
            .skip-link {
                position: absolute;
                top: -40px;
                left: 6px;
                background: #000;
                color: #fff;
                padding: 8px;
                text-decoration: none;
                border-radius: 4px;
                transition: top 0.3s;
            }
            
            .skip-link:focus {
                top: 6px;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Setup focus management
     */
    setupFocusManagement() {
        // Track focus changes
        document.addEventListener('focusin', (event) => {
            this.handleFocusIn(event);
        });
        
        document.addEventListener('focusout', (event) => {
            this.handleFocusOut(event);
        });
        
        // Setup focus trapping for modals
        this.setupFocusTrapping();
    }
    
    /**
     * Handle focus in
     */
    handleFocusIn(event) {
        const target = event.target;
        
        // Add focus indicator
        target.classList.add('focus-visible');
        
        // Announce focus changes for screen readers
        if (this.config.enableAnnouncements) {
            const label = this.getAccessibleName(target);
            if (label) {
                this.announce(`${label} focused`);
            }
        }
    }
    
    /**
     * Handle focus out
     */
    handleFocusOut(event) {
        const target = event.target;
        
        // Remove focus indicator
        target.classList.remove('focus-visible');
    }
    
    /**
     * Setup focus trapping
     */
    setupFocusTrapping() {
        if (!this.config.enableFocusTrapping) return;
        
        // Override modal focus trapping
        const originalShowModal = window.showModal;
        if (originalShowModal) {
            window.showModal = (dialog) => {
                this.trapFocus(dialog);
                return originalShowModal.call(window, dialog);
            };
        }
    }
    
    /**
     * Trap focus within an element
     */
    trapFocus(element) {
        const focusableElements = this.getFocusableElements(element);
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        // Focus first element
        firstElement.focus();
        
        // Handle tab navigation within the trap
        const handleTab = (event) => {
            if (event.key === 'Tab') {
                if (event.shiftKey) {
                    if (document.activeElement === firstElement) {
                        event.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        event.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        };
        
        element.addEventListener('keydown', handleTab);
        
        // Store for cleanup
        this.modalStack.push({ element, handleTab });
    }
    
    /**
     * Release focus trap
     */
    releaseFocusTrap(element) {
        const modal = this.modalStack.find(m => m.element === element);
        if (modal) {
            modal.element.removeEventListener('keydown', modal.handleTab);
            this.modalStack = this.modalStack.filter(m => m !== modal);
        }
    }
    
    /**
     * Setup announcements
     */
    setupAnnouncements() {
        if (!this.config.enableAnnouncements) return;
        
        // Create announcement region
        const announcementRegion = document.createElement('div');
        announcementRegion.id = 'announcement-region';
        announcementRegion.setAttribute('aria-live', 'polite');
        announcementRegion.setAttribute('aria-atomic', 'true');
        announcementRegion.className = 'sr-only';
        document.body.appendChild(announcementRegion);
        
        // Add CSS for screen reader only content
        this.addScreenReaderCSS();
    }
    
    /**
     * Add CSS for screen reader only content
     */
    addScreenReaderCSS() {
        const style = document.createElement('style');
        style.textContent = `
            .sr-only {
                position: absolute !important;
                width: 1px !important;
                height: 1px !important;
                padding: 0 !important;
                margin: -1px !important;
                overflow: hidden !important;
                clip: rect(0, 0, 0, 0) !important;
                white-space: nowrap !important;
                border: 0 !important;
            }
            
            .focus-visible {
                outline: 2px solid #007bff !important;
                outline-offset: 2px !important;
            }
            
            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Announce message to screen readers
     */
    announce(message) {
        const region = document.getElementById('announcement-region');
        if (!region) return;
        
        // Clear previous announcement
        region.textContent = '';
        
        // Add new announcement
        setTimeout(() => {
            region.textContent = message;
        }, this.config.announcementDelay);
    }
    
    /**
     * Setup high contrast mode
     */
    setupHighContrast() {
        if (!this.config.enableHighContrast) return;
        
        // Check for high contrast preference
        const mediaQuery = window.matchMedia('(prefers-contrast: high)');
        
        const handleContrastChange = (event) => {
            if (event.matches) {
                document.documentElement.classList.add('high-contrast');
            } else {
                document.documentElement.classList.remove('high-contrast');
            }
        };
        
        mediaQuery.addEventListener('change', handleContrastChange);
        handleContrastChange(mediaQuery);
        
        // Add high contrast CSS
        this.addHighContrastCSS();
    }
    
    /**
     * Add high contrast CSS
     */
    addHighContrastCSS() {
        const style = document.createElement('style');
        style.textContent = `
            .high-contrast {
                --primary-color: #000000 !important;
                --secondary-color: #ffffff !important;
                --text-color: #000000 !important;
                --background-color: #ffffff !important;
                --border-color: #000000 !important;
            }
            
            .high-contrast * {
                border-color: var(--border-color) !important;
                color: var(--text-color) !important;
                background-color: var(--background-color) !important;
            }
            
            .high-contrast .btn {
                border: 2px solid var(--border-color) !important;
            }
            
            .high-contrast .form-control {
                border: 2px solid var(--border-color) !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Setup reduced motion
     */
    setupReducedMotion() {
        if (!this.config.enableReducedMotion) return;
        
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        
        const handleMotionChange = (event) => {
            if (event.matches) {
                document.documentElement.classList.add('reduced-motion');
            } else {
                document.documentElement.classList.remove('reduced-motion');
            }
        };
        
        mediaQuery.addEventListener('change', handleMotionChange);
        handleMotionChange(mediaQuery);
    }
    
    /**
     * Setup form accessibility
     */
    setupFormAccessibility() {
        // Enhance form labels
        this.enhanceFormLabels();
        
        // Setup error associations
        this.setupErrorAssociations();
        
        // Setup form validation
        this.setupFormValidation();
    }
    
    /**
     * Enhance form labels
     */
    enhanceFormLabels() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                // Ensure proper labeling
                if (!input.id && !input.getAttribute('aria-label')) {
                    const label = input.previousElementSibling;
                    if (label && label.tagName === 'LABEL') {
                        const id = `input-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                        input.id = id;
                        label.setAttribute('for', id);
                    }
                }
                
                // Add required indicator
                if (input.hasAttribute('required')) {
                    const label = input.labels?.[0] || input.previousElementSibling;
                    if (label && label.tagName === 'LABEL') {
                        const requiredSpan = document.createElement('span');
                        requiredSpan.textContent = ' *';
                        requiredSpan.className = 'required-indicator';
                        requiredSpan.setAttribute('aria-label', 'required');
                        label.appendChild(requiredSpan);
                    }
                }
            });
        });
    }
    
    /**
     * Setup error associations
     */
    setupErrorAssociations() {
        // Watch for error messages
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.associateErrors(node);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    /**
     * Associate errors with form controls
     */
    associateErrors(errorElement) {
        if (!errorElement.classList.contains('error-message')) return;
        
        const form = errorElement.closest('form');
        if (!form) return;
        
        // Find the related input
        const inputName = errorElement.getAttribute('data-field');
        if (inputName) {
            const input = form.querySelector(`[name="${inputName}"]`);
            if (input) {
                const errorId = `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                errorElement.id = errorId;
                input.setAttribute('aria-describedby', errorId);
                input.setAttribute('aria-invalid', 'true');
            }
        }
    }
    
    /**
     * Setup form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!this.validateForm(form)) {
                    event.preventDefault();
                }
            });
            
            // Real-time validation
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
            });
        });
    }
    
    /**
     * Validate form
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    /**
     * Validate individual field
     */
    validateField(input) {
        const value = input.value.trim();
        const required = input.hasAttribute('required');
        const type = input.type;
        const pattern = input.pattern;
        
        // Clear previous errors
        this.clearFieldError(input);
        
        // Check required
        if (required && !value) {
            this.showFieldError(input, 'This field is required');
            return false;
        }
        
        // Check pattern
        if (pattern && value && !new RegExp(pattern).test(value)) {
            this.showFieldError(input, 'Please enter a valid value');
            return false;
        }
        
        // Check email
        if (type === 'email' && value && !this.isValidEmail(value)) {
            this.showFieldError(input, 'Please enter a valid email address');
            return false;
        }
        
        // Mark as valid
        input.setAttribute('aria-invalid', 'false');
        return true;
    }
    
    /**
     * Show field error
     */
    showFieldError(input, message) {
        input.setAttribute('aria-invalid', 'true');
        
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        errorElement.setAttribute('role', 'alert');
        
        const errorId = `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        errorElement.id = errorId;
        input.setAttribute('aria-describedby', errorId);
        
        input.parentNode.appendChild(errorElement);
        
        // Announce error
        this.announce(message);
    }
    
    /**
     * Clear field error
     */
    clearFieldError(input) {
        const errorElement = input.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
        input.removeAttribute('aria-describedby');
    }
    
    /**
     * Utility methods
     */
    getFocusableElements(container = document) {
        return Array.from(container.querySelectorAll(this.focusableElements))
            .filter(el => !el.disabled && el.offsetParent !== null);
    }
    
    getAccessibleName(element) {
        return element.getAttribute('aria-label') ||
               element.getAttribute('title') ||
               element.textContent?.trim() ||
               element.alt ||
               '';
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    activateElement(element) {
        if (element.click) {
            element.click();
        } else if (element.dispatchEvent) {
            element.dispatchEvent(new Event('click'));
        }
    }
    
    selectListItem(item, items) {
        items.forEach(i => i.setAttribute('aria-selected', 'false'));
        item.setAttribute('aria-selected', 'true');
        item.focus();
    }
    
    closeModal(modal) {
        modal.setAttribute('aria-hidden', 'true');
        this.releaseFocusTrap(modal);
    }
    
    closeDropdown(dropdown) {
        dropdown.setAttribute('aria-expanded', 'false');
    }
}

// Create and export singleton instance
const accessibilityManager = new AccessibilityManager();

// Export for use in other modules
window.SEIM_ACCESSIBILITY = accessibilityManager;

export default accessibilityManager;
export { AccessibilityManager }; 