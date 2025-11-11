/**
 * Dynforms Theme Test Module
 * Tests and validates dark mode implementation for dynforms
 */

class DynformsThemeTest {
    constructor() {
        this.testResults = [];
        this.init();
    }
    
    init() {
        console.log('DynformsThemeTest: Initializing...');
        this.runTests();
        this.setupThemeChangeListener();
    }
    
    /**
     * Run comprehensive tests for dynforms theme implementation
     */
    runTests() {
        console.log('DynformsThemeTest: Running tests...');
        
        // Test 1: Check if dynforms elements exist
        this.testElementExistence();
        
        // Test 2: Check CSS variable application
        this.testCSSVariables();
        
        // Test 3: Check contrast ratios
        this.testContrastRatios();
        
        // Test 4: Check theme switching
        this.testThemeSwitching();
        
        // Log results
        this.logResults();
    }
    
    /**
     * Test if dynforms elements exist on the page
     */
    testElementExistence() {
        const elements = [
            '#df-builder',
            '#df-sidebar',
            '#df-preview',
            '.field-type-btn',
            '.preview-frame',
            '.list-group-item'
        ];
        
        const results = elements.map(selector => {
            const element = document.querySelector(selector);
            return {
                selector,
                exists: !!element,
                element: element
            };
        });
        
        this.testResults.push({
            test: 'Element Existence',
            results: results,
            passed: results.every(r => r.exists)
        });
        
        console.log('DynformsThemeTest: Element existence test results:', results);
    }
    
    /**
     * Test if CSS variables are being applied correctly
     */
    testCSSVariables() {
        const testElement = document.querySelector('#df-builder');
        if (!testElement) {
            console.warn('DynformsThemeTest: Cannot test CSS variables - #df-builder not found');
            return;
        }
        
        const computedStyle = window.getComputedStyle(testElement);
        const variables = [
            '--bg-secondary',
            '--text-primary',
            '--border-color'
        ];
        
        const results = variables.map(variable => {
            const value = computedStyle.getPropertyValue(variable);
            return {
                variable,
                value: value.trim(),
                hasValue: value.trim() !== ''
            };
        });
        
        this.testResults.push({
            test: 'CSS Variables',
            results: results,
            passed: results.every(r => r.hasValue)
        });
        
        console.log('DynformsThemeTest: CSS variables test results:', results);
    }
    
    /**
     * Test contrast ratios for accessibility
     */
    testContrastRatios() {
        const testElements = [
            { selector: '.field-type-btn', description: 'Field type buttons' },
            { selector: '.list-group-item', description: 'List group items' },
            { selector: '.preview-frame', description: 'Preview frame' }
        ];
        
        const results = testElements.map(({ selector, description }) => {
            const element = document.querySelector(selector);
            if (!element) {
                return { description, passed: false, reason: 'Element not found' };
            }
            
            const computedStyle = window.getComputedStyle(element);
            const backgroundColor = computedStyle.backgroundColor;
            const color = computedStyle.color;
            
            // Simple contrast check (basic implementation)
            const hasContrast = this.checkBasicContrast(backgroundColor, color);
            
            return {
                description,
                backgroundColor,
                color,
                passed: hasContrast,
                reason: hasContrast ? 'Good contrast' : 'Poor contrast detected'
            };
        });
        
        this.testResults.push({
            test: 'Contrast Ratios',
            results: results,
            passed: results.every(r => r.passed)
        });
        
        console.log('DynformsThemeTest: Contrast test results:', results);
    }
    
    /**
     * Basic contrast check (simplified)
     */
    checkBasicContrast(bgColor, textColor) {
        // This is a simplified check - in production, use a proper contrast ratio calculator
        if (bgColor === 'rgba(0, 0, 0, 0)' || textColor === 'rgba(0, 0, 0, 0)') {
            return false;
        }
        
        // Check if colors are different (basic check)
        return bgColor !== textColor;
    }
    
    /**
     * Test theme switching functionality
     */
    testThemeSwitching() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const themeManager = window.themeManager;
        
        if (!themeManager) {
            this.testResults.push({
                test: 'Theme Switching',
                results: [{ description: 'Theme Manager', passed: false, reason: 'Theme manager not found' }],
                passed: false
            });
            return;
        }
        
        const results = [
            {
                description: 'Theme Manager Available',
                passed: true,
                reason: 'Theme manager found'
            },
            {
                description: 'Current Theme',
                passed: true,
                reason: `Current theme: ${currentTheme}`
            }
        ];
        
        this.testResults.push({
            test: 'Theme Switching',
            results: results,
            passed: results.every(r => r.passed)
        });
        
        console.log('DynformsThemeTest: Theme switching test results:', results);
    }
    
    /**
     * Setup listener for theme changes
     */
    setupThemeChangeListener() {
        window.addEventListener('themeChanged', (event) => {
            console.log('DynformsThemeTest: Theme changed to:', event.detail.theme);
            this.runTests();
        });
    }
    
    /**
     * Log test results
     */
    logResults() {
        console.log('DynformsThemeTest: All test results:', this.testResults);
        
        const passedTests = this.testResults.filter(test => test.passed).length;
        const totalTests = this.testResults.length;
        
        console.log(`DynformsThemeTest: ${passedTests}/${totalTests} tests passed`);
        
        // Show results in UI if on dynforms page
        if (document.querySelector('#df-builder')) {
            this.showResultsInUI();
        }
    }
    
    /**
     * Show test results in the UI
     */
    showResultsInUI() {
        const resultsDiv = document.createElement('div');
        resultsDiv.id = 'dynforms-theme-test-results';
        resultsDiv.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            max-width: 300px;
            z-index: 9999;
            font-size: 12px;
            color: var(--text-primary);
        `;
        
        const passedTests = this.testResults.filter(test => test.passed).length;
        const totalTests = this.testResults.length;
        
        resultsDiv.innerHTML = `
            <h6 style="margin: 0 0 10px 0; color: var(--text-primary);">Dynforms Theme Test</h6>
            <p style="margin: 0 0 10px 0; color: var(--text-primary);">
                ${passedTests}/${totalTests} tests passed
            </p>
            <button onclick="this.parentElement.remove()" 
                    style="background: var(--primary-color); color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                Close
            </button>
        `;
        
        document.body.appendChild(resultsDiv);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (resultsDiv.parentElement) {
                resultsDiv.remove();
            }
        }, 10000);
    }
    
    /**
     * Get test results for external use
     */
    getResults() {
        return this.testResults;
    }
    
    /**
     * Run tests again
     */
    refresh() {
        this.testResults = [];
        this.runTests();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only run on dynforms pages
    if (document.querySelector('#df-builder') || window.location.pathname.includes('dynforms')) {
        window.dynformsThemeTest = new DynformsThemeTest();
        console.log('DynformsThemeTest: Initialized on dynforms page');
    }
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DynformsThemeTest;
} 