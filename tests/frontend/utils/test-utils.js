/**
 * SEIM Frontend Test Utilities
 * Comprehensive testing utilities for frontend modules and components
 */

/**
 * Test environment setup and teardown utilities
 */
export class TestEnvironment {
    constructor() {
        this.originalDocument = global.document;
        this.originalWindow = global.window;
        this.originalLocation = global.location;
        this.originalFetch = global.fetch;
        this.originalConsole = global.console;
        this.originalLocalStorage = global.localStorage;
        this.originalSessionStorage = global.sessionStorage;
        
        this.mocks = new Map();
        this.spies = new Map();
        this.stubs = new Map();
    }
    
    /**
     * Setup test environment
     */
    setup() {
        // Mock DOM environment
        this.setupDOM();
        
        // Mock browser APIs
        this.setupBrowserAPIs();
        
        // Mock storage
        this.setupStorage();
        
        // Mock console for testing
        this.setupConsole();
        
        // Setup global test utilities
        this.setupGlobalUtils();
    }
    
    /**
     * Teardown test environment
     */
    teardown() {
        // Restore original globals
        global.document = this.originalDocument;
        global.window = this.originalWindow;
        global.location = this.originalLocation;
        global.fetch = this.originalFetch;
        global.console = this.originalConsole;
        global.localStorage = this.originalLocalStorage;
        global.sessionStorage = this.originalSessionStorage;
        
        // Clear mocks
        this.mocks.clear();
        this.spies.clear();
        this.stubs.clear();
        
        // Clear DOM
        if (global.document && global.document.body) {
            global.document.body.innerHTML = '';
        }
    }
    
    /**
     * Setup DOM environment
     */
    setupDOM() {
        const jsdom = require('jsdom');
        const { JSDOM } = jsdom;
        
        const dom = new JSDOM(`
            <!DOCTYPE html>
            <html>
                <head>
                    <title>SEIM Test Environment</title>
                </head>
                <body>
                    <div id="app"></div>
                </body>
            </html>
        `, {
            url: 'http://localhost:8000',
            pretendToBeVisual: true,
            resources: 'usable'
        });
        
        global.document = dom.window.document;
        global.window = dom.window;
        global.location = dom.window.location;
        global.navigator = dom.window.navigator;
        global.HTMLElement = dom.window.HTMLElement;
        global.Element = dom.window.Element;
        global.Node = dom.window.Node;
        global.Event = dom.window.Event;
        global.CustomEvent = dom.window.CustomEvent;
        global.MouseEvent = dom.window.MouseEvent;
        global.KeyboardEvent = dom.window.KeyboardEvent;
        global.FocusEvent = dom.window.FocusEvent;
        global.FormData = dom.window.FormData;
        global.URLSearchParams = dom.window.URLSearchParams;
        global.Headers = dom.window.Headers;
        global.Request = dom.window.Request;
        global.Response = dom.window.Response;
        
        // Add missing browser APIs
        global.window.requestAnimationFrame = (callback) => setTimeout(callback, 16);
        global.window.cancelAnimationFrame = (id) => clearTimeout(id);
        global.window.matchMedia = () => ({
            matches: false,
            addListener: () => {},
            removeListener: () => {},
            addEventListener: () => {},
            removeEventListener: () => {}
        });
        global.window.IntersectionObserver = class MockIntersectionObserver {
            constructor(callback) {
                this.callback = callback;
                this.observe = () => {};
                this.unobserve = () => {};
                this.disconnect = () => {};
            }
        };
        global.window.ResizeObserver = class MockResizeObserver {
            constructor(callback) {
                this.callback = callback;
                this.observe = () => {};
                this.unobserve = () => {};
                this.disconnect = () => {};
            }
        };
    }
    
    /**
     * Setup browser APIs
     */
    setupBrowserAPIs() {
        // Mock fetch
        global.fetch = jest.fn();
        
        // Mock performance API
        global.performance = {
            now: jest.fn(() => Date.now()),
            mark: jest.fn(),
            measure: jest.fn(),
            getEntriesByType: jest.fn(() => []),
            getEntriesByName: jest.fn(() => [])
        };
        
        // Mock localStorage
        global.localStorage = {
            getItem: jest.fn(),
            setItem: jest.fn(),
            removeItem: jest.fn(),
            clear: jest.fn(),
            key: jest.fn(),
            length: 0
        };
        
        // Mock sessionStorage
        global.sessionStorage = {
            getItem: jest.fn(),
            setItem: jest.fn(),
            removeItem: jest.fn(),
            clear: jest.fn(),
            key: jest.fn(),
            length: 0
        };
        
        // Mock URL API
        global.URL = {
            createObjectURL: jest.fn(() => 'blob:mock-url'),
            revokeObjectURL: jest.fn()
        };
    }
    
    /**
     * Setup storage mocks
     */
    setupStorage() {
        const storage = new Map();
        
        const createStorageMock = () => ({
            getItem: jest.fn((key) => storage.get(key) || null),
            setItem: jest.fn((key, value) => storage.set(key, value)),
            removeItem: jest.fn((key) => storage.delete(key)),
            clear: jest.fn(() => storage.clear()),
            key: jest.fn((index) => Array.from(storage.keys())[index] || null),
            get length() { return storage.size; }
        });
        
        global.localStorage = createStorageMock();
        global.sessionStorage = createStorageMock();
    }
    
    /**
     * Setup console mocks
     */
    setupConsole() {
        global.console = {
            log: jest.fn(),
            warn: jest.fn(),
            error: jest.fn(),
            info: jest.fn(),
            debug: jest.fn(),
            group: jest.fn(),
            groupEnd: jest.fn(),
            time: jest.fn(),
            timeEnd: jest.fn()
        };
    }
    
    /**
     * Setup global test utilities
     */
    setupGlobalUtils() {
        global.TestUtils = {
            createElement: this.createElement.bind(this),
            createEvent: this.createEvent.bind(this),
            fireEvent: this.fireEvent.bind(this),
            waitFor: this.waitFor.bind(this),
            waitForElement: this.waitForElement.bind(this),
            mockAPI: this.mockAPI.bind(this),
            mockStorage: this.mockStorage.bind(this),
            cleanup: this.cleanup.bind(this)
        };
    }
    
    /**
     * Create DOM element
     */
    createElement(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);
        
        // Set attributes
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'textContent') {
                element.textContent = value;
            } else if (key === 'innerHTML') {
                element.innerHTML = value;
            } else {
                element.setAttribute(key, value);
            }
        });
        
        // Add children
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else {
                element.appendChild(child);
            }
        });
        
        return element;
    }
    
    /**
     * Create and dispatch event
     */
    createEvent(type, options = {}) {
        const event = new Event(type, {
            bubbles: true,
            cancelable: true,
            ...options
        });
        return event;
    }
    
    /**
     * Fire event on element
     */
    fireEvent(element, eventType, options = {}) {
        const event = this.createEvent(eventType, options);
        element.dispatchEvent(event);
        return event;
    }
    
    /**
     * Wait for condition
     */
    async waitFor(condition, timeout = 1000, interval = 10) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            if (await condition()) {
                return true;
            }
            await new Promise(resolve => setTimeout(resolve, interval));
        }
        
        throw new Error(`Condition not met within ${timeout}ms`);
    }
    
    /**
     * Wait for element to appear
     */
    async waitForElement(selector, timeout = 1000) {
        return this.waitFor(() => {
            const element = document.querySelector(selector);
            return element !== null;
        }, timeout);
    }
    
    /**
     * Mock API response
     */
    mockAPI(url, response, options = {}) {
        const mockResponse = {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => response,
            text: async () => JSON.stringify(response),
            headers: new Headers(options.headers || {}),
            ...options
        };
        
        global.fetch.mockImplementation((requestUrl) => {
            if (requestUrl === url || requestUrl.includes(url)) {
                return Promise.resolve(mockResponse);
            }
            return Promise.reject(new Error(`No mock found for ${requestUrl}`));
        });
        
        return mockResponse;
    }
    
    /**
     * Mock storage
     */
    mockStorage(type, data) {
        const storage = type === 'local' ? global.localStorage : global.sessionStorage;
        
        Object.entries(data).forEach(([key, value]) => {
            storage.getItem.mockImplementation((requestedKey) => {
                return requestedKey === key ? value : null;
            });
        });
    }
    
    /**
     * Cleanup DOM
     */
    cleanup() {
        if (document.body) {
            document.body.innerHTML = '';
        }
    }
}

/**
 * Test data generators
 */
export class TestData {
    /**
     * Generate mock user data
     */
    static createUser(overrides = {}) {
        return {
            id: 1,
            username: 'testuser',
            email: 'test@example.com',
            first_name: 'Test',
            last_name: 'User',
            is_active: true,
            date_joined: '2024-01-01T00:00:00Z',
            ...overrides
        };
    }
    
    /**
     * Generate mock application data
     */
    static createApplication(overrides = {}) {
        return {
            id: 1,
            student: this.createUser(),
            program: this.createProgram(),
            status: 'pending',
            submitted_date: '2024-01-01T00:00:00Z',
            gpa: 3.5,
            documents: [],
            ...overrides
        };
    }
    
    /**
     * Generate mock program data
     */
    static createProgram(overrides = {}) {
        return {
            id: 1,
            name: 'Test Program',
            description: 'A test exchange program',
            country: 'Test Country',
            university: 'Test University',
            duration: '1 semester',
            min_gpa: 3.0,
            max_students: 10,
            is_active: true,
            ...overrides
        };
    }
    
    /**
     * Generate mock document data
     */
    static createDocument(overrides = {}) {
        return {
            id: 1,
            name: 'test-document.pdf',
            file_type: 'application/pdf',
            size: 1024 * 1024, // 1MB
            uploaded_by: this.createUser(),
            uploaded_date: '2024-01-01T00:00:00Z',
            is_required: true,
            ...overrides
        };
    }
    
    /**
     * Generate mock notification data
     */
    static createNotification(overrides = {}) {
        return {
            id: 1,
            user: this.createUser(),
            title: 'Test Notification',
            message: 'This is a test notification',
            type: 'info',
            is_read: false,
            created_date: '2024-01-01T00:00:00Z',
            ...overrides
        };
    }
    
    /**
     * Generate mock form data
     */
    static createFormData(fields = {}) {
        const formData = new FormData();
        Object.entries(fields).forEach(([key, value]) => {
            formData.append(key, value);
        });
        return formData;
    }
    
    /**
     * Generate mock API response
     */
    static createAPIResponse(data, status = 200, message = 'Success') {
        return {
            success: status >= 200 && status < 300,
            data,
            message,
            status,
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * Generate mock error response
     */
    static createErrorResponse(message = 'An error occurred', status = 400) {
        return {
            success: false,
            error: message,
            status,
            timestamp: new Date().toISOString()
        };
    }
}

/**
 * DOM testing utilities
 */
export class DOMUtils {
    /**
     * Query element with retry
     */
    static async queryElement(selector, timeout = 1000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const element = document.querySelector(selector);
            if (element) {
                return element;
            }
            await new Promise(resolve => setTimeout(resolve, 10));
        }
        
        throw new Error(`Element not found: ${selector}`);
    }
    
    /**
     * Query all elements with retry
     */
    static async queryAllElements(selector, timeout = 1000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                return Array.from(elements);
            }
            await new Promise(resolve => setTimeout(resolve, 10));
        }
        
        return [];
    }
    
    /**
     * Check if element is visible
     */
    static isVisible(element) {
        if (!element) return false;
        
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               style.opacity !== '0' &&
               element.offsetWidth > 0 &&
               element.offsetHeight > 0;
    }
    
    /**
     * Check if element is in viewport
     */
    static isInViewport(element) {
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        return rect.top >= 0 &&
               rect.left >= 0 &&
               rect.bottom <= window.innerHeight &&
               rect.right <= window.innerWidth;
    }
    
    /**
     * Simulate user interaction
     */
    static simulateUserInteraction(element, eventType = 'click', options = {}) {
        if (!element) return;
        
        const event = new Event(eventType, {
            bubbles: true,
            cancelable: true,
            ...options
        });
        
        element.dispatchEvent(event);
        return event;
    }
    
    /**
     * Simulate keyboard input
     */
    static simulateKeyboardInput(element, text, options = {}) {
        if (!element) return;
        
        // Focus element
        element.focus();
        
        // Simulate keydown for each character
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            const keyEvent = new KeyboardEvent('keydown', {
                key: char,
                code: `Key${char.toUpperCase()}`,
                bubbles: true,
                cancelable: true,
                ...options
            });
            element.dispatchEvent(keyEvent);
        }
        
        // Update value
        element.value = text;
        
        // Simulate input event
        const inputEvent = new Event('input', {
            bubbles: true,
            cancelable: true,
            ...options
        });
        element.dispatchEvent(inputEvent);
        
        // Simulate change event
        const changeEvent = new Event('change', {
            bubbles: true,
            cancelable: true,
            ...options
        });
        element.dispatchEvent(changeEvent);
    }
    
    /**
     * Simulate form submission
     */
    static simulateFormSubmission(form, options = {}) {
        if (!form) return;
        
        const submitEvent = new Event('submit', {
            bubbles: true,
            cancelable: true,
            ...options
        });
        
        form.dispatchEvent(submitEvent);
        return submitEvent;
    }
    
    /**
     * Get computed styles
     */
    static getComputedStyles(element, properties = []) {
        if (!element) return {};
        
        const styles = window.getComputedStyle(element);
        const result = {};
        
        properties.forEach(property => {
            result[property] = styles.getPropertyValue(property);
        });
        
        return result;
    }
    
    /**
     * Check accessibility attributes
     */
    static checkAccessibility(element) {
        if (!element) return {};
        
        return {
            hasRole: element.hasAttribute('role'),
            role: element.getAttribute('role'),
            hasAriaLabel: element.hasAttribute('aria-label'),
            ariaLabel: element.getAttribute('aria-label'),
            hasAriaLabelledby: element.hasAttribute('aria-labelledby'),
            ariaLabelledby: element.getAttribute('aria-labelledby'),
            hasAriaDescribedby: element.hasAttribute('aria-describedby'),
            ariaDescribedby: element.getAttribute('aria-describedby'),
            hasTabindex: element.hasAttribute('tabindex'),
            tabindex: element.getAttribute('tabindex'),
            isFocusable: element.tabIndex >= 0 || element.tagName === 'BUTTON' || element.tagName === 'A' || element.tagName === 'INPUT'
        };
    }
}

/**
 * Async testing utilities
 */
export class AsyncUtils {
    /**
     * Wait for promises to resolve
     */
    static async waitForPromises() {
        await new Promise(resolve => setTimeout(resolve, 0));
    }
    
    /**
     * Wait for specific time
     */
    static async wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Wait for condition with timeout
     */
    static async waitForCondition(condition, timeout = 1000, interval = 10) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            if (await condition()) {
                return true;
            }
            await this.wait(interval);
        }
        
        throw new Error(`Condition not met within ${timeout}ms`);
    }
    
    /**
     * Retry function with exponential backoff
     */
    static async retry(fn, maxAttempts = 3, baseDelay = 100) {
        let lastError;
        
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                return await fn();
            } catch (error) {
                lastError = error;
                
                if (attempt === maxAttempts) {
                    throw error;
                }
                
                const delay = baseDelay * Math.pow(2, attempt - 1);
                await this.wait(delay);
            }
        }
    }
}

/**
 * Mock utilities
 */
export class MockUtils {
    /**
     * Create mock function
     */
    static createMock(implementation = () => {}) {
        return jest.fn(implementation);
    }
    
    /**
     * Create mock object
     */
    static createMockObject(methods = {}) {
        const mock = {};
        
        Object.entries(methods).forEach(([key, implementation]) => {
            mock[key] = jest.fn(implementation);
        });
        
        return mock;
    }
    
    /**
     * Create mock module
     */
    static createMockModule(modulePath, exports = {}) {
        jest.doMock(modulePath, () => exports);
    }
    
    /**
     * Reset all mocks
     */
    static resetAllMocks() {
        jest.clearAllMocks();
        jest.resetAllMocks();
    }
}

// Export default test environment
export default TestEnvironment; 