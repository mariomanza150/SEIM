# SEIM Frontend Troubleshooting Guide

## Table of Contents
1. [Build Issues](#build-issues)
2. [Module Loading Issues](#module-loading-issues)
3. [Performance Problems](#performance-problems)
4. [Testing Issues](#testing-issues)
5. [Code Quality Issues](#code-quality-issues)
6. [Browser Compatibility](#browser-compatibility)
7. [Debugging Techniques](#debugging-techniques)
8. [Common Error Messages](#common-error-messages)

## Build Issues

### Webpack Build Failures

#### Error: Module not found
```
ModuleNotFoundError: Module not found: Error: Can't resolve './modules/logger' in '/path/to/static/js'
```

**Solution:**
1. Check file path and case sensitivity
2. Verify the file exists in the correct location
3. Check import/export syntax
4. Clear webpack cache: `npm run build -- --no-cache`

```bash
# Check if file exists
ls -la static/js/modules/logger.js

# Clear cache and rebuild
rm -rf node_modules/.cache
npm run build
```

#### Error: Unexpected token
```
SyntaxError: Unexpected token (1:1)
```

**Solution:**
1. Check for syntax errors in JavaScript files
2. Verify file encoding (should be UTF-8)
3. Check for missing semicolons or brackets
4. Run ESLint to find syntax issues: `npm run lint`

```bash
# Check syntax with ESLint
npm run lint

# Check specific file
npx eslint static/js/modules/logger.js
```

#### Error: Cannot resolve module
```
Error: Cannot resolve module 'lodash' in '/path/to/static/js'
```

**Solution:**
1. Install missing dependency: `npm install lodash`
2. Check package.json for correct dependency
3. Clear node_modules and reinstall: `rm -rf node_modules && npm install`

```bash
# Install missing dependency
npm install lodash

# Reinstall all dependencies
rm -rf node_modules package-lock.json
npm install
```

### Bundle Size Issues

#### Bundle too large
```
WARNING in asset size limit: The following asset(s) exceed the recommended size limit (244 KiB).
```

**Solution:**
1. Analyze bundle: `npm run build:analyze`
2. Check for duplicate dependencies
3. Use code splitting for large modules
4. Optimize imports

```bash
# Analyze bundle size
npm run build:analyze

# Check for duplicate packages
npm ls lodash
```

## Module Loading Issues

### Module Not Defined

#### Error: SEIM_LOGGER is not defined
```javascript
Uncaught ReferenceError: SEIM_LOGGER is not defined
```

**Solution:**
1. Check if module is included in main.js
2. Verify module initialization order
3. Check for JavaScript errors preventing module loading

```javascript
// Check if module exists
if (typeof SEIM_LOGGER !== 'undefined') {
    console.log('Logger module loaded');
} else {
    console.error('Logger module not found');
}

// Check module initialization
try {
    SEIM_LOGGER.init();
} catch (error) {
    console.error('Logger initialization failed:', error);
}
```

#### Error: Module initialization failed
```javascript
Error: Module initialization failed: Invalid configuration
```

**Solution:**
1. Check module configuration
2. Verify required dependencies
3. Check browser console for detailed errors

```javascript
// Debug module initialization
SEIM_LOGGER.init({
    level: 'debug',
    context: 'debug'
});

// Check module state
console.log('Logger config:', SEIM_LOGGER.config);
console.log('Logger state:', SEIM_LOGGER.state);
```

### Module Communication Issues

#### Events not firing
```javascript
// Event listener not working
document.addEventListener('custom:event', handler);
```

**Solution:**
1. Check event name consistency
2. Verify event is dispatched correctly
3. Check if listener is added before event dispatch

```javascript
// Debug event system
document.addEventListener('custom:event', (event) => {
    console.log('Event received:', event);
    console.log('Event detail:', event.detail);
});

// Dispatch test event
document.dispatchEvent(new CustomEvent('custom:event', {
    detail: { test: true }
}));
```

## Performance Problems

### Slow Page Load

#### Large bundle size
**Symptoms:** Slow initial page load, large network requests

**Solution:**
1. Enable code splitting
2. Use lazy loading for non-critical modules
3. Optimize bundle size

```javascript
// Enable dynamic loading
SEIM_DYNAMIC_LOADER.init({
    enabled: true,
    preload: false
});

// Lazy load non-critical modules
SEIM_DYNAMIC_LOADER.loadModule('heavy-module').then(() => {
    console.log('Heavy module loaded');
});
```

#### Memory leaks
**Symptoms:** Increasing memory usage, slow performance over time

**Solution:**
1. Check for event listener leaks
2. Clear intervals and timeouts
3. Use performance monitoring

```javascript
// Monitor memory usage
SEIM_PERFORMANCE.init({
    enabled: true,
    monitorMemory: true
});

// Check for memory leaks
setInterval(() => {
    const memory = performance.memory;
    console.log('Memory usage:', {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit
    });
}, 5000);
```

### API Performance Issues

#### Slow API responses
**Symptoms:** Long loading times, timeout errors

**Solution:**
1. Enable API caching
2. Use request deduplication
3. Implement retry logic

```javascript
// Enable API optimization
SEIM_API.init({
    cache: true,
    deduplication: true,
    retry: 3,
    timeout: 10000
});

// Monitor API performance
SEIM_API.get('/api/data', {
    measure: true
}).then(response => {
    console.log('API response time:', response.metadata.duration);
});
```

## Testing Issues

### Jest Test Failures

#### Module not found in tests
```
Cannot resolve module 'SEIM_LOGGER' from 'test-file.test.js'
```

**Solution:**
1. Check Jest configuration
2. Mock global modules
3. Update test setup

```javascript
// Mock global modules in test setup
global.SEIM_LOGGER = {
    init: jest.fn(),
    info: jest.fn(),
    error: jest.fn()
};

global.SEIM_API = {
    init: jest.fn(),
    get: jest.fn(),
    post: jest.fn()
};
```

#### DOM testing issues
```
Error: document is not defined
```

**Solution:**
1. Use jsdom environment
2. Setup DOM in tests
3. Use testing utilities

```javascript
// Setup DOM for tests
import { TestEnvironment } from '../utils/test-utils.js';

beforeEach(() => {
    TestEnvironment.setup();
});

afterEach(() => {
    TestEnvironment.cleanup();
});
```

### Coverage Issues

#### Low test coverage
**Solution:**
1. Add more test cases
2. Test edge cases and error conditions
3. Use coverage reports to identify gaps

```bash
# Generate coverage report
npm run test:coverage

# Check specific module coverage
npm run test:coverage -- --collectCoverageFrom="static/js/modules/logger.js"
```

## Code Quality Issues

### ESLint Errors

#### Too many linting errors
**Solution:**
1. Fix errors incrementally
2. Use auto-fix: `npm run lint:fix`
3. Disable rules temporarily if needed

```bash
# Auto-fix linting issues
npm run lint:fix

# Check specific file
npx eslint static/js/modules/logger.js --fix
```

#### Prettier conflicts
**Solution:**
1. Run Prettier: `npm run format`
2. Check Prettier configuration
3. Resolve conflicts between ESLint and Prettier

```bash
# Format code with Prettier
npm run format

# Check formatting
npm run format:check
```

### Quality Gate Failures

#### Coverage below threshold
**Solution:**
1. Add more tests
2. Improve test coverage
3. Adjust coverage thresholds if appropriate

```bash
# Check coverage
npm run test:coverage

# Run quality analysis
npm run quality
```

#### Complexity too high
**Solution:**
1. Refactor complex functions
2. Break down large functions
3. Extract helper functions

```javascript
// Refactor complex function
// Before
function complexFunction(data) {
    // 50+ lines of complex logic
}

// After
function complexFunction(data) {
    const processedData = preprocessData(data);
    const result = processData(processedData);
    return postprocessResult(result);
}
```

## Browser Compatibility

### IE11 Issues

#### ES6+ features not working
**Solution:**
1. Use Babel to transpile ES6+ code
2. Add polyfills for missing features
3. Check browser support

```javascript
// Check browser support
if (!window.Promise) {
    console.error('Promise not supported');
}

// Use polyfills
import 'core-js/stable';
import 'regenerator-runtime/runtime';
```

### Mobile Browser Issues

#### Touch events not working
**Solution:**
1. Add touch event handlers
2. Use pointer events for cross-platform support
3. Test on actual mobile devices

```javascript
// Handle both mouse and touch events
element.addEventListener('pointerdown', handlePointerDown);
element.addEventListener('touchstart', handleTouchStart);
```

## Debugging Techniques

### Console Debugging

#### Enable debug mode
```javascript
// Enable debug logging
SEIM_LOGGER.init({ level: 'debug' });

// Enable API debugging
SEIM_API.init({ debug: true });

// Enable performance monitoring
SEIM_PERFORMANCE.init({ enabled: true });
```

#### Debug specific modules
```javascript
// Debug logger module
console.log('Logger config:', SEIM_LOGGER.config);
console.log('Logger state:', SEIM_LOGGER.state);

// Debug API module
console.log('API cache:', SEIM_API.cache);
console.log('API pending requests:', SEIM_API.pendingRequests);
```

### Browser DevTools

#### Network debugging
1. Open DevTools → Network tab
2. Check for failed requests
3. Monitor bundle loading
4. Check API response times

#### Performance debugging
1. Open DevTools → Performance tab
2. Record page load
3. Analyze performance bottlenecks
4. Check memory usage

### Error Tracking

#### Capture errors
```javascript
// Global error handler
window.addEventListener('error', (event) => {
    SEIM_LOGGER.error('Global error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
    });
});

// Promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
    SEIM_LOGGER.error('Unhandled promise rejection', {
        reason: event.reason
    });
});
```

## Common Error Messages

### JavaScript Errors

#### TypeError: Cannot read property 'x' of undefined
**Cause:** Trying to access property of undefined object
**Solution:** Add null checks

```javascript
// Before
const value = object.property.subproperty;

// After
const value = object?.property?.subproperty;
```

#### ReferenceError: x is not defined
**Cause:** Using variable before declaration
**Solution:** Check variable scope and declaration

```javascript
// Check if variable exists
if (typeof variable !== 'undefined') {
    // Use variable
}
```

### Webpack Errors

#### Module parse failed
**Cause:** Webpack cannot parse file
**Solution:** Check file syntax and loader configuration

```bash
# Check file syntax
npx eslint static/js/modules/problematic-file.js

# Check webpack configuration
cat webpack.config.js
```

#### Entry module not found
**Cause:** Entry point file missing
**Solution:** Check webpack entry configuration

```javascript
// Check entry points in webpack.config.js
entry: {
    main: './static/js/main.js',
    dashboard: './static/js/dashboard.js'
}
```

### API Errors

#### 404 Not Found
**Cause:** API endpoint doesn't exist
**Solution:** Check API URL and backend configuration

```javascript
// Check API URL
console.log('API URL:', SEIM_API.baseURL);

// Test API endpoint
fetch('/api/test').then(response => {
    console.log('API response:', response.status);
});
```

#### 500 Internal Server Error
**Cause:** Server-side error
**Solution:** Check server logs and API implementation

```javascript
// Add error handling
SEIM_API.get('/api/data').catch(error => {
    SEIM_LOGGER.error('API error', { error });
    SEIM_UI.showError('Server error occurred');
});
```

## Quick Fixes

### Common Solutions

```bash
# Clear all caches and rebuild
rm -rf node_modules package-lock.json
rm -rf .cache dist
npm install
npm run build

# Fix linting issues
npm run lint:fix
npm run format

# Run quality checks
npm run quality:all

# Test everything
npm test
npm run test:coverage
```

### Emergency Debug Mode

```javascript
// Enable all debugging
SEIM_LOGGER.init({ level: 'debug' });
SEIM_API.init({ debug: true });
SEIM_PERFORMANCE.init({ enabled: true });

// Log everything
console.log('All modules:', {
    logger: typeof SEIM_LOGGER,
    api: typeof SEIM_API,
    ui: typeof SEIM_UI
});
```

This troubleshooting guide covers the most common issues you'll encounter when working with the SEIM frontend. For issues not covered here, check the browser console, server logs, and create an issue in the project repository. 