/**
 * SEIM Accessibility Testing Module
 * Provides automated accessibility testing and WCAG compliance checking
 */

import { SEIM_LOGGER } from './logger.js';
import { SEIM_ERROR_HANDLER } from './error-handler.js';

class AccessibilityTester {
    constructor() {
        this.results = {
            passed: [],
            failed: [],
            warnings: [],
            summary: {}
        };
        
        this.wcagRules = {
            // WCAG 2.1 AA Level Rules
            '1.1.1': {
                name: 'Non-text Content',
                description: 'All non-text content has a text alternative',
                test: this.testImageAltText
            },
            '1.3.1': {
                name: 'Info and Relationships',
                description: 'Information, structure, and relationships can be programmatically determined',
                test: this.testSemanticStructure
            },
            '1.4.3': {
                name: 'Contrast (Minimum)',
                description: 'Text has sufficient contrast ratio',
                test: this.testColorContrast
            },
            '2.1.1': {
                name: 'Keyboard',
                description: 'All functionality is available from a keyboard',
                test: this.testKeyboardAccessibility
            },
            '2.1.2': {
                name: 'No Keyboard Trap',
                description: 'Keyboard focus is not trapped',
                test: this.testKeyboardTraps
            },
            '2.4.1': {
                name: 'Bypass Blocks',
                description: 'A mechanism is available to bypass repeated blocks',
                test: this.testSkipLinks
            },
            '2.4.2': {
                name: 'Page Titled',
                description: 'Pages have descriptive titles',
                test: this.testPageTitles
            },
            '2.4.3': {
                name: 'Focus Order',
                description: 'Focus order is logical and intuitive',
                test: this.testFocusOrder
            },
            '2.4.4': {
                name: 'Link Purpose (In Context)',
                description: 'Purpose of each link can be determined from link text alone',
                test: this.testLinkPurpose
            },
            '3.2.1': {
                name: 'On Focus',
                description: 'Changing focus does not automatically trigger changes',
                test: this.testFocusChanges
            },
            '3.2.2': {
                name: 'On Input',
                description: 'Changing input does not automatically trigger changes',
                test: this.testInputChanges
            },
            '4.1.1': {
                name: 'Parsing',
                description: 'Content can be parsed by user agents',
                test: this.testHTMLParsing
            },
            '4.1.2': {
                name: 'Name, Role, Value',
                description: 'User interface components have accessible names',
                test: this.testComponentNames
            }
        };
        
        this.init();
    }
    
    init() {
        SEIM_LOGGER.info('Accessibility Tester initialized');
    }
    
    /**
     * Run comprehensive accessibility test
     */
    async runFullTest() {
        SEIM_LOGGER.info('Starting comprehensive accessibility test');
        
        this.results = {
            passed: [],
            failed: [],
            warnings: [],
            summary: {}
        };
        
        const startTime = performance.now();
        
        // Run all WCAG tests
        for (const [ruleId, rule] of Object.entries(this.wcagRules)) {
            try {
                const result = await rule.test.call(this);
                this.addResult(ruleId, rule.name, result);
            } catch (error) {
                SEIM_ERROR_HANDLER.handleError(error, { context: 'Accessibility Test', ruleId });
                this.addResult(ruleId, rule.name, { passed: false, issues: [error.message] });
            }
        }
        
        // Generate summary
        this.generateSummary();
        
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        SEIM_LOGGER.info(`Accessibility test completed in ${duration.toFixed(2)}ms`);
        
        return this.results;
    }
    
    /**
     * Add test result
     */
    addResult(ruleId, ruleName, result) {
        const testResult = {
            ruleId,
            ruleName,
            passed: result.passed,
            issues: result.issues || [],
            elements: result.elements || [],
            timestamp: new Date().toISOString()
        };
        
        if (result.passed) {
            this.results.passed.push(testResult);
        } else if (result.warning) {
            this.results.warnings.push(testResult);
        } else {
            this.results.failed.push(testResult);
        }
    }
    
    /**
     * Generate test summary
     */
    generateSummary() {
        const total = this.results.passed.length + this.results.failed.length + this.results.warnings.length;
        
        this.results.summary = {
            total,
            passed: this.results.passed.length,
            failed: this.results.failed.length,
            warnings: this.results.warnings.length,
            passRate: total > 0 ? (this.results.passed.length / total * 100).toFixed(1) : 0,
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * Test 1.1.1: Image Alt Text
     */
    async testImageAltText() {
        const images = document.querySelectorAll('img');
        const issues = [];
        const elements = [];
        
        images.forEach(img => {
            const alt = img.getAttribute('alt');
            const ariaLabel = img.getAttribute('aria-label');
            const ariaLabelledby = img.getAttribute('aria-labelledby');
            const role = img.getAttribute('role');
            
            // Check if image is decorative
            const isDecorative = role === 'presentation' || 
                                role === 'none' || 
                                alt === '' ||
                                img.classList.contains('decorative');
            
            if (!isDecorative && !alt && !ariaLabel && !ariaLabelledby) {
                issues.push('Image missing alt text or accessible name');
                elements.push({
                    element: img,
                    selector: this.getElementSelector(img),
                    issue: 'Missing alt text'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 1.3.1: Semantic Structure
     */
    async testSemanticStructure() {
        const issues = [];
        const elements = [];
        
        // Check for proper heading structure
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        let previousLevel = 0;
        
        headings.forEach(heading => {
            const level = parseInt(heading.tagName.charAt(1));
            
            if (level - previousLevel > 1) {
                issues.push(`Heading level skipped: ${heading.tagName} follows ${previousLevel > 0 ? 'h' + previousLevel : 'no heading'}`);
                elements.push({
                    element: heading,
                    selector: this.getElementSelector(heading),
                    issue: 'Heading level skipped'
                });
            }
            
            previousLevel = level;
        });
        
        // Check for proper list structure
        const lists = document.querySelectorAll('ul, ol');
        lists.forEach(list => {
            const listItems = list.querySelectorAll('li');
            if (listItems.length === 0) {
                issues.push('Empty list found');
                elements.push({
                    element: list,
                    selector: this.getElementSelector(list),
                    issue: 'Empty list'
                });
            }
        });
        
        // Check for proper table structure
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            const hasCaption = table.querySelector('caption');
            const hasHeaders = table.querySelectorAll('th').length > 0;
            
            if (!hasCaption && !hasHeaders) {
                issues.push('Table missing caption or headers');
                elements.push({
                    element: table,
                    selector: this.getElementSelector(table),
                    issue: 'Missing caption or headers'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 1.4.3: Color Contrast
     */
    async testColorContrast() {
        const issues = [];
        const elements = [];
        
        // This is a simplified test - in a real implementation, you'd use a library like axe-core
        const textElements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6, a, button, label');
        
        textElements.forEach(element => {
            const style = window.getComputedStyle(element);
            const color = style.color;
            const backgroundColor = style.backgroundColor;
            
            // Check if text has sufficient contrast (simplified)
            if (color === backgroundColor || color === 'transparent') {
                issues.push('Text may not have sufficient contrast');
                elements.push({
                    element: element,
                    selector: this.getElementSelector(element),
                    issue: 'Insufficient contrast'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 2.1.1: Keyboard Accessibility
     */
    async testKeyboardAccessibility() {
        const issues = [];
        const elements = [];
        
        // Check for elements that should be keyboard accessible
        const interactiveElements = document.querySelectorAll('button, a, input, select, textarea, [role="button"], [role="link"]');
        
        interactiveElements.forEach(element => {
            const tabIndex = element.getAttribute('tabindex');
            
            if (tabIndex === '-1' && !element.disabled) {
                issues.push('Interactive element not keyboard accessible');
                elements.push({
                    element: element,
                    selector: this.getElementSelector(element),
                    issue: 'Not keyboard accessible'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 2.1.2: No Keyboard Trap
     */
    async testKeyboardTraps() {
        const issues = [];
        const elements = [];
        
        // Check for potential keyboard traps in modals
        const modals = document.querySelectorAll('[role="dialog"], .modal');
        
        modals.forEach(modal => {
            const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            
            if (focusableElements.length === 0) {
                issues.push('Modal has no focusable elements');
                elements.push({
                    element: modal,
                    selector: this.getElementSelector(modal),
                    issue: 'No focusable elements'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 2.4.1: Skip Links
     */
    async testSkipLinks() {
        const issues = [];
        const elements = [];
        
        const skipLinks = document.querySelectorAll('.skip-link, [href^="#"]');
        
        if (skipLinks.length === 0) {
            issues.push('No skip links found');
        } else {
            skipLinks.forEach(link => {
                const href = link.getAttribute('href');
                const target = document.querySelector(href);
                
                if (!target) {
                    issues.push('Skip link target not found');
                    elements.push({
                        element: link,
                        selector: this.getElementSelector(link),
                        issue: 'Target not found'
                    });
                }
            });
        }
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 2.4.2: Page Titles
     */
    async testPageTitles() {
        const issues = [];
        const elements = [];
        
        const title = document.title;
        
        if (!title || title.trim() === '') {
            issues.push('Page has no title');
        } else if (title.length < 10) {
            issues.push('Page title may be too short');
        } else if (title.length > 60) {
            issues.push('Page title may be too long');
        }
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 2.4.3: Focus Order
     */
    async testFocusOrder() {
        const issues = [];
        const elements = [];
        
        const focusableElements = document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        
        // Check for logical tab order
        for (let i = 0; i < focusableElements.length - 1; i++) {
            const current = focusableElements[i];
            const next = focusableElements[i + 1];
            
            const currentRect = current.getBoundingClientRect();
            const nextRect = next.getBoundingClientRect();
            
            // Check if focus order follows visual layout
            if (currentRect.top > nextRect.top + 50) {
                issues.push('Focus order may not follow visual layout');
                elements.push({
                    element: current,
                    selector: this.getElementSelector(current),
                    issue: 'Focus order issue'
                });
            }
        }
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 2.4.4: Link Purpose
     */
    async testLinkPurpose() {
        const issues = [];
        const elements = [];
        
        const links = document.querySelectorAll('a[href]');
        
        links.forEach(link => {
            const text = link.textContent.trim();
            const ariaLabel = link.getAttribute('aria-label');
            const title = link.getAttribute('title');
            
            if (!text && !ariaLabel && !title) {
                issues.push('Link has no accessible name');
                elements.push({
                    element: link,
                    selector: this.getElementSelector(link),
                    issue: 'No accessible name'
                });
            } else if (text && (text === 'click here' || text === 'read more' || text === 'more')) {
                issues.push('Link text is not descriptive');
                elements.push({
                    element: link,
                    selector: this.getElementSelector(link),
                    issue: 'Non-descriptive link text'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 3.2.1: On Focus
     */
    async testFocusChanges() {
        const issues = [];
        const elements = [];
        
        // Check for focus event handlers that might cause unwanted changes
        const focusableElements = document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        
        focusableElements.forEach(element => {
            const hasFocusHandler = element.onfocus || 
                                  element.getAttribute('onfocus') ||
                                  element.querySelector('[onfocus]');
            
            if (hasFocusHandler) {
                issues.push('Element has focus handler that may cause unwanted changes');
                elements.push({
                    element: element,
                    selector: this.getElementSelector(element),
                    issue: 'Focus handler detected'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 3.2.2: On Input
     */
    async testInputChanges() {
        const issues = [];
        const elements = [];
        
        const inputs = document.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            const hasInputHandler = input.oninput || 
                                  input.getAttribute('oninput') ||
                                  input.querySelector('[oninput]');
            
            if (hasInputHandler) {
                issues.push('Input has input handler that may cause unwanted changes');
                elements.push({
                    element: input,
                    selector: this.getElementSelector(input),
                    issue: 'Input handler detected'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 4.1.1: HTML Parsing
     */
    async testHTMLParsing() {
        const issues = [];
        const elements = [];
        
        // Check for unclosed tags (simplified)
        const html = document.documentElement.outerHTML;
        
        // Check for common parsing issues
        const unclosedTags = html.match(/<([^>]+)(?!.*<\/\1>)/g);
        
        if (unclosedTags) {
            issues.push('Potential unclosed HTML tags detected');
        }
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Test 4.1.2: Component Names
     */
    async testComponentNames() {
        const issues = [];
        const elements = [];
        
        const interactiveElements = document.querySelectorAll('button, input, select, textarea, [role="button"], [role="link"]');
        
        interactiveElements.forEach(element => {
            const accessibleName = this.getAccessibleName(element);
            
            if (!accessibleName) {
                issues.push('Interactive element missing accessible name');
                elements.push({
                    element: element,
                    selector: this.getElementSelector(element),
                    issue: 'Missing accessible name'
                });
            }
        });
        
        return {
            passed: issues.length === 0,
            issues,
            elements
        };
    }
    
    /**
     * Get accessible name for element
     */
    getAccessibleName(element) {
        return element.getAttribute('aria-label') ||
               element.getAttribute('title') ||
               element.textContent?.trim() ||
               element.alt ||
               '';
    }
    
    /**
     * Get element selector for reporting
     */
    getElementSelector(element) {
        if (element.id) {
            return `#${element.id}`;
        }
        
        if (element.className) {
            const classes = element.className.split(' ').filter(c => c.trim());
            if (classes.length > 0) {
                return `.${classes[0]}`;
            }
        }
        
        return element.tagName.toLowerCase();
    }
    
    /**
     * Generate accessibility report
     */
    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            summary: this.results.summary,
            results: this.results,
            recommendations: this.generateRecommendations()
        };
        
        return report;
    }
    
    /**
     * Generate recommendations based on test results
     */
    generateRecommendations() {
        const recommendations = [];
        
        if (this.results.failed.length > 0) {
            recommendations.push('Fix critical accessibility issues before deployment');
        }
        
        if (this.results.warnings.length > 0) {
            recommendations.push('Review and address accessibility warnings');
        }
        
        if (this.results.summary.passRate < 90) {
            recommendations.push('Consider accessibility training for development team');
        }
        
        return recommendations;
    }
    
    /**
     * Export results to JSON
     */
    exportResults() {
        const report = this.generateReport();
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `accessibility-report-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
}

// Create and export singleton instance
const accessibilityTester = new AccessibilityTester();

// Export for use in other modules
window.SEIM_ACCESSIBILITY_TESTER = accessibilityTester;

export default accessibilityTester;
export { AccessibilityTester }; 