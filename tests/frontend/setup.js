// Jest frontend test setup: includes polyfills and mocks for browser APIs
console.log('Jest frontend setup file is running...');

/**
 * SEIM Frontend Test Setup
 * Global test configuration and utilities
 */

// Polyfill for TextEncoder/TextDecoder
if (typeof global.TextEncoder === 'undefined') {
    const { TextEncoder, TextDecoder } = require('util');
    global.TextEncoder = TextEncoder;
    global.TextDecoder = TextDecoder;
}

// Polyfill for performance.getEntriesByType
if (!global.performance.getEntriesByType) {
    global.performance.getEntriesByType = (type) => {
        if (type === 'navigation') {
            return [{
                entryType: 'navigation',
                startTime: 0,
                duration: 123,
                name: 'http://localhost:8000/',
                type: 'navigate',
                domComplete: 100,
                domContentLoadedEventEnd: 50,
                loadEventEnd: 120
            }];
        } else if (type === 'paint') {
            return [
                { entryType: 'paint', name: 'first-paint', startTime: 50 },
                { entryType: 'paint', name: 'first-contentful-paint', startTime: 75 }
            ];
        }
        return [];
    };
}

// Global test environment
global.TestEnvironment = {
    // Test environment utilities
};

global.TestData = {
    // Test data utilities
};

global.DOMUtils = {
    // DOM utilities
};

global.AsyncUtils = {
    // Async utilities
};

global.MockUtils = {
    // Mock utilities
};

// Setup global mocks
global.fetch = jest.fn();
global.localStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};
global.sessionStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};

// Mock console methods
global.console = {
    log: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
    debug: jest.fn()
};

// Mock performance API
global.performance = {
    now: jest.fn(() => Date.now()),
    mark: jest.fn(),
    measure: jest.fn()
};

// Mock IntersectionObserver
global.IntersectionObserver = class MockIntersectionObserver {
    constructor(callback) {
        this.callback = callback;
        this.observe = jest.fn();
        this.unobserve = jest.fn();
        this.disconnect = jest.fn();
    }
};

// Mock ResizeObserver
global.ResizeObserver = class MockResizeObserver {
    constructor(callback) {
        this.callback = callback;
        this.observe = jest.fn();
        this.unobserve = jest.fn();
        this.disconnect = jest.fn();
    }
};

// Mock SEIM_LOGGER global as a function (constructor) and object
function SEIM_LOGGER() {
    this.history = [];
}
SEIM_LOGGER.prototype.debug = jest.fn();
SEIM_LOGGER.prototype.info = jest.fn();
SEIM_LOGGER.prototype.warn = jest.fn();
SEIM_LOGGER.prototype.error = jest.fn();
SEIM_LOGGER.prototype.log = jest.fn();
SEIM_LOGGER.prototype.setLevel = jest.fn();
SEIM_LOGGER.prototype.getLevel = jest.fn(() => 'debug');
SEIM_LOGGER.prototype.export = jest.fn();
SEIM_LOGGER.prototype.import = jest.fn();
SEIM_LOGGER.prototype.clear = jest.fn();
// Assign methods to the function object as well
SEIM_LOGGER.debug = SEIM_LOGGER.prototype.debug;
SEIM_LOGGER.info = SEIM_LOGGER.prototype.info;
SEIM_LOGGER.warn = SEIM_LOGGER.prototype.warn;
SEIM_LOGGER.error = SEIM_LOGGER.prototype.error;
SEIM_LOGGER.log = SEIM_LOGGER.prototype.log;
SEIM_LOGGER.setLevel = SEIM_LOGGER.prototype.setLevel;
SEIM_LOGGER.getLevel = SEIM_LOGGER.prototype.getLevel;
SEIM_LOGGER.export = SEIM_LOGGER.prototype.export;
SEIM_LOGGER.import = SEIM_LOGGER.prototype.import;
SEIM_LOGGER.clear = SEIM_LOGGER.prototype.clear;
SEIM_LOGGER.history = [];
SEIM_LOGGER.constructor = SEIM_LOGGER;

// Explicitly assign to global
global.SEIM_LOGGER = SEIM_LOGGER;
global.SEIM_LOGGER.constructor = SEIM_LOGGER;
global.SEIM_LOGGER.debug = SEIM_LOGGER.debug;
global.SEIM_LOGGER.info = SEIM_LOGGER.info;
global.SEIM_LOGGER.warn = SEIM_LOGGER.warn;
global.SEIM_LOGGER.error = SEIM_LOGGER.error;
global.SEIM_LOGGER.log = SEIM_LOGGER.log;
global.SEIM_LOGGER.setLevel = SEIM_LOGGER.setLevel;
global.SEIM_LOGGER.getLevel = SEIM_LOGGER.getLevel;
global.SEIM_LOGGER.export = SEIM_LOGGER.export;
global.SEIM_LOGGER.import = SEIM_LOGGER.import;
global.SEIM_LOGGER.clear = SEIM_LOGGER.clear;
global.SEIM_LOGGER.history = [];

console.log('SEIM_LOGGER mock created:', typeof global.SEIM_LOGGER, global.SEIM_LOGGER.constructor === global.SEIM_LOGGER);

// Global test utilities
global.TestUtils = {
    createElement: (tag, attributes = {}, children = []) => {
        const element = document.createElement(tag);
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        children.forEach(child => element.appendChild(child));
        return element;
    },
    
    fireEvent: (element, eventType, options = {}) => {
        const event = new Event(eventType, { bubbles: true, ...options });
        element.dispatchEvent(event);
        return event;
    },
    
    waitFor: async (condition, timeout = 1000) => {
        const startTime = Date.now();
        while (Date.now() - startTime < timeout) {
            if (await condition()) return true;
            await new Promise(resolve => setTimeout(resolve, 10));
        }
        throw new Error(`Condition not met within ${timeout}ms`);
    }
};

// Cleanup after each test
afterEach(() => {
    jest.clearAllMocks();
    if (document.body) {
        document.body.innerHTML = '';
    }
}); 