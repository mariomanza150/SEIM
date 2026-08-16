# SEIM Frontend API Reference

## Table of Contents
1. [Logger Module](#logger-module)
2. [API Module](#api-module)
3. [Auth Module](#auth-module)
4. [UI Module](#ui-module)
5. [Accessibility Module](#accessibility-module)
6. [UI Enhanced Module](#ui-enhanced-module)
7. [Performance Module](#performance-module)
8. [Dynamic Loader Module](#dynamic-loader-module)
9. [Utils Module](#utils-module)

## Logger Module

The Logger module provides structured logging with levels, context, and performance tracking.

### Global Access
```javascript
window.SEIM_LOGGER
```

### Configuration
```javascript
const config = {
    level: 'info',           // Log level: 'debug', 'info', 'warn', 'error'
    context: 'default',      // Context for log messages
    enableConsole: true,     // Enable console output
    enablePerformance: true, // Enable performance tracking
    maxLogs: 1000           // Maximum logs to keep in memory
};
```

### Methods

#### `init(options = {})`
Initialize the logger module.

**Parameters:**
- `options` (Object): Configuration options
  - `level` (string): Log level
  - `context` (string): Context for log messages
  - `enableConsole` (boolean): Enable console output
  - `enablePerformance` (boolean): Enable performance tracking
  - `maxLogs` (number): Maximum logs to keep in memory

**Example:**
```javascript
SEIM_LOGGER.init({
    level: 'debug',
    context: 'applications',
    enablePerformance: true
});
```

#### `debug(message, data = {})`
Log a debug message.

**Parameters:**
- `message` (string): Log message
- `data` (Object): Additional data to log

**Example:**
```javascript
SEIM_LOGGER.debug('User clicked button', { buttonId: 'submit', userId: 123 });
```

#### `info(message, data = {})`
Log an info message.

**Parameters:**
- `message` (string): Log message
- `data` (Object): Additional data to log

**Example:**
```javascript
SEIM_LOGGER.info('Application loaded successfully', { loadTime: 1500 });
```

#### `warn(message, data = {})`
Log a warning message.

**Parameters:**
- `message` (string): Log message
- `data` (Object): Additional data to log

**Example:**
```javascript
SEIM_LOGGER.warn('API response slow', { endpoint: '/api/data', duration: 5000 });
```

#### `error(message, data = {})`
Log an error message.

**Parameters:**
- `message` (string): Log message
- `data` (Object): Additional data to log

**Example:**
```javascript
SEIM_LOGGER.error('API request failed', { 
    endpoint: '/api/data', 
    error: error.message,
    status: 500 
});
```

#### `measure(label, fn)`
Measure the performance of a function.

**Parameters:**
- `label` (string): Label for the measurement
- `fn` (Function): Function to measure

**Returns:** Promise with the result of the function

**Example:**
```javascript
const result = await SEIM_LOGGER.measure('data-processing', async () => {
    return await processData(largeDataset);
});
```

#### `getLogs(level = null, limit = 100)`
Get logged messages.

**Parameters:**
- `level` (string, optional): Filter by log level
- `limit` (number): Maximum number of logs to return

**Returns:** Array of log entries

**Example:**
```javascript
const errors = SEIM_LOGGER.getLogs('error', 10);
const allLogs = SEIM_LOGGER.getLogs();
```

## API Module

The API module provides an enhanced HTTP client with caching, retry logic, and request deduplication.

### Global Access
```javascript
window.SEIM_API
```

### Configuration
```javascript
const config = {
    baseURL: '/api',         // Base URL for API requests
    timeout: 10000,          // Request timeout in milliseconds
    retry: 3,               // Number of retry attempts
    cache: true,            // Enable response caching
    deduplication: true,    // Enable request deduplication
    debug: false            // Enable debug mode
};
```

### Methods

#### `init(options = {})`
Initialize the API module.

**Parameters:**
- `options` (Object): Configuration options

**Example:**
```javascript
SEIM_API.init({
    baseURL: '/api/v1',
    timeout: 15000,
    retry: 5,
    cache: true
});
```

#### `get(url, options = {})`
Make a GET request.

**Parameters:**
- `url` (string): API endpoint
- `options` (Object): Request options
  - `params` (Object): Query parameters
  - `headers` (Object): Request headers
  - `cache` (boolean): Enable caching for this request
  - `measure` (boolean): Measure request performance
  - `retry` (number): Retry attempts for this request

**Returns:** Promise with response data

**Example:**
```javascript
// Simple GET request
const data = await SEIM_API.get('/applications');

// GET request with parameters
const applications = await SEIM_API.get('/applications', {
    params: { status: 'pending', limit: 10 },
    cache: true,
    measure: true
});
```

#### `post(url, data = {}, options = {})`
Make a POST request.

**Parameters:**
- `url` (string): API endpoint
- `data` (Object): Request body
- `options` (Object): Request options
  - `headers` (Object): Request headers
  - `measure` (boolean): Measure request performance
  - `retry` (number): Retry attempts for this request

**Returns:** Promise with response data

**Example:**
```javascript
const newApplication = await SEIM_API.post('/applications', {
    program_id: 123,
    student_id: 456,
    documents: ['doc1.pdf', 'doc2.pdf']
}, {
    measure: true
});
```

#### `put(url, data = {}, options = {})`
Make a PUT request.

**Parameters:**
- `url` (string): API endpoint
- `data` (Object): Request body
- `options` (Object): Request options

**Returns:** Promise with response data

**Example:**
```javascript
const updatedApplication = await SEIM_API.put('/applications/123', {
    status: 'approved',
    notes: 'Application approved'
});
```

#### `delete(url, options = {})`
Make a DELETE request.

**Parameters:**
- `url` (string): API endpoint
- `options` (Object): Request options

**Returns:** Promise with response data

**Example:**
```javascript
await SEIM_API.delete('/applications/123');
```

#### `clearCache(pattern = null)`
Clear the API cache.

**Parameters:**
- `pattern` (string, optional): Pattern to match cached requests

**Example:**
```javascript
// Clear all cache
SEIM_API.clearCache();

// Clear specific endpoint cache
SEIM_API.clearCache('/applications');
```

#### `getPendingRequests()`
Get currently pending requests.

**Returns:** Array of pending request objects

**Example:**
```javascript
const pending = SEIM_API.getPendingRequests();
console.log('Pending requests:', pending.length);
```

## Auth Module

The Auth module manages authentication state, token handling, and session validation.

### Global Access
```javascript
window.SEIM_AUTH
```

### Configuration
```javascript
const config = {
    tokenKey: 'auth_token',      // Local storage key for token
    refreshKey: 'refresh_token', // Local storage key for refresh token
    autoRefresh: true,          // Auto-refresh expired tokens
    checkInterval: 60000        // Token check interval in milliseconds
};
```

### Methods

#### `init(options = {})`
Initialize the auth module.

**Parameters:**
- `options` (Object): Configuration options

**Example:**
```javascript
SEIM_AUTH.init({
    autoRefresh: true,
    checkInterval: 30000
});
```

#### `login(credentials)`
Authenticate user with credentials.

**Parameters:**
- `credentials` (Object): Login credentials
  - `username` (string): Username
  - `password` (string): Password

**Returns:** Promise with authentication result

**Example:**
```javascript
try {
    const result = await SEIM_AUTH.login({
        username: 'student@example.com',
        password: 'password123'
    });
    
    if (result.success) {
        SEIM_UI.showNotification('Login successful', 'success');
        window.location.href = '/dashboard';
    }
} catch (error) {
    SEIM_UI.showError('Login failed: ' + error.message);
}
```

#### `logout()`
Logout the current user.

**Returns:** Promise

**Example:**
```javascript
await SEIM_AUTH.logout();
window.location.href = '/login';
```

#### `isAuthenticated()`
Check if user is authenticated.

**Returns:** boolean

**Example:**
```javascript
if (SEIM_AUTH.isAuthenticated()) {
    // User is logged in
    loadUserData();
} else {
    // Redirect to login
    window.location.href = '/login';
}
```

#### `getToken()`
Get the current authentication token.

**Returns:** string or null

**Example:**
```javascript
const token = SEIM_AUTH.getToken();
if (token) {
    // Use token for API requests
    SEIM_API.setAuthHeader(token);
}
```

#### `refreshToken()`
Refresh the authentication token.

**Returns:** Promise with new token

**Example:**
```javascript
try {
    const newToken = await SEIM_AUTH.refreshToken();
    SEIM_LOGGER.info('Token refreshed successfully');
} catch (error) {
    SEIM_LOGGER.error('Token refresh failed', { error });
    // Redirect to login
    window.location.href = '/login';
}
```

#### `getUser()`
Get current user information.

**Returns:** Object with user data or null

**Example:**
```javascript
const user = SEIM_AUTH.getUser();
if (user) {
    console.log('Current user:', user.name);
    updateUserInterface(user);
}
```

## UI Module

The UI module provides Bootstrap integration, form handling, and common UI patterns.

### Global Access
```javascript
window.SEIM_UI
```

### Configuration
```javascript
const config = {
    notificationDuration: 5000,  // Notification display duration
    confirmDefaults: {           // Default confirmation dialog settings
        title: 'Confirm Action',
        type: 'warning'
    },
    loadingDefaults: {           // Default loading settings
        text: 'Loading...',
        backdrop: true
    }
};
```

### Methods

#### `init(options = {})`
Initialize the UI module.

**Parameters:**
- `options` (Object): Configuration options

**Example:**
```javascript
SEIM_UI.init({
    notificationDuration: 3000,
    confirmDefaults: {
        title: 'Confirm',
        type: 'question'
    }
});
```

#### `showNotification(message, type = 'info', duration = null)`
Show a notification message.

**Parameters:**
- `message` (string): Notification message
- `type` (string): Notification type ('success', 'info', 'warning', 'error')
- `duration` (number, optional): Display duration in milliseconds

**Example:**
```javascript
SEIM_UI.showNotification('Data saved successfully', 'success');
SEIM_UI.showNotification('Please check your input', 'warning', 10000);
```

#### `showError(message, title = 'Error')`
Show an error notification.

**Parameters:**
- `message` (string): Error message
- `title` (string): Error title

**Example:**
```javascript
SEIM_UI.showError('Failed to load data', 'Network Error');
```

#### `showSuccess(message, title = 'Success')`
Show a success notification.

**Parameters:**
- `message` (string): Success message
- `title` (string): Success title

**Example:**
```javascript
SEIM_UI.showSuccess('Application submitted successfully');
```

#### `confirm(message, options = {})`
Show a confirmation dialog.

**Parameters:**
- `message` (string): Confirmation message
- `options` (Object): Dialog options
  - `title` (string): Dialog title
  - `type` (string): Dialog type
  - `confirmText` (string): Confirm button text
  - `cancelText` (string): Cancel button text

**Returns:** Promise that resolves to boolean

**Example:**
```javascript
const confirmed = await SEIM_UI.confirm('Are you sure you want to delete this application?', {
    title: 'Delete Application',
    type: 'warning',
    confirmText: 'Delete',
    cancelText: 'Cancel'
});

if (confirmed) {
    await deleteApplication(id);
}
```

#### `showLoading(text = null, backdrop = true)`
Show a loading indicator.

**Parameters:**
- `text` (string, optional): Loading text
- `backdrop` (boolean): Show backdrop

**Example:**
```javascript
SEIM_UI.showLoading('Saving application...');
// ... perform operation
SEIM_UI.hideLoading();
```

#### `hideLoading()`
Hide the loading indicator.

**Example:**
```javascript
SEIM_UI.hideLoading();
```

#### `renderTable(data, columns, options = {})`
Render a data table.

**Parameters:**
- `data` (Array): Table data
- `columns` (Array): Column definitions
- `options` (Object): Table options
  - `container` (string): Container selector
  - `sortable` (boolean): Enable sorting
  - `searchable` (boolean): Enable search
  - `pagination` (boolean): Enable pagination

**Example:**
```javascript
const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
    { key: 'status', label: 'Status' },
    { key: 'actions', label: 'Actions', render: (value, row) => `
        <button onclick="editApplication(${row.id})">Edit</button>
    `}
];

SEIM_UI.renderTable(applications, columns, {
    container: '#applications-table',
    sortable: true,
    searchable: true,
    pagination: true
});
```

#### `setupForm(formSelector, options = {})`
Setup form handling and validation.

**Parameters:**
- `formSelector` (string): Form selector
- `options` (Object): Form options
  - `validation` (Object): Validation rules
  - `submitHandler` (Function): Submit handler
  - `resetHandler` (Function): Reset handler

**Example:**
```javascript
SEIM_UI.setupForm('#application-form', {
    validation: {
        'program_id': { required: true },
        'documents': { required: true, minFiles: 1 }
    },
    submitHandler: async (formData) => {
        try {
            await SEIM_API.post('/applications', formData);
            SEIM_UI.showSuccess('Application submitted');
        } catch (error) {
            SEIM_UI.showError('Submission failed');
        }
    }
});
```

## Accessibility Module

The Accessibility module provides ARIA management, keyboard navigation, and screen reader support.

### Global Access
```javascript
window.SEIM_ACCESSIBILITY
```

### Configuration
```javascript
const config = {
    enableKeyboardNav: true,    // Enable keyboard navigation
    enableScreenReader: true,   // Enable screen reader support
    enableFocusManagement: true, // Enable focus management
    enableARIA: true,          // Enable ARIA attributes
    announceChanges: true      // Announce dynamic content changes
};
```

### Methods

#### `init(options = {})`
Initialize the accessibility module.

**Parameters:**
- `options` (Object): Configuration options

**Example:**
```javascript
SEIM_ACCESSIBILITY.init({
    enableKeyboardNav: true,
    enableScreenReader: true
});
```

#### `setupKeyboardNavigation(container = document)`
Setup keyboard navigation for a container.

**Parameters:**
- `container` (Element): Container element

**Example:**
```javascript
SEIM_ACCESSIBILITY.setupKeyboardNavigation('#main-content');
```

#### `announce(message, priority = 'polite')`
Announce a message to screen readers.

**Parameters:**
- `message` (string): Message to announce
- `priority` (string): Announcement priority ('polite', 'assertive')

**Example:**
```javascript
SEIM_ACCESSIBILITY.announce('New data loaded', 'polite');
SEIM_ACCESSIBILITY.announce('Error occurred', 'assertive');
```

#### `setFocus(element)`
Set focus to an element with proper management.

**Parameters:**
- `element` (Element): Element to focus

**Example:**
```javascript
const button = document.querySelector('#submit-button');
SEIM_ACCESSIBILITY.setFocus(button);
```

#### `trapFocus(container)`
Trap focus within a container (for modals).

**Parameters:**
- `container` (Element): Container element

**Example:**
```javascript
const modal = document.querySelector('#modal');
SEIM_ACCESSIBILITY.trapFocus(modal);
```

#### `releaseFocus()`
Release focus trap.

**Example:**
```javascript
SEIM_ACCESSIBILITY.releaseFocus();
```

#### `addARIA(element, attributes)`
Add ARIA attributes to an element.

**Parameters:**
- `element` (Element): Target element
- `attributes` (Object): ARIA attributes

**Example:**
```javascript
const button = document.querySelector('#menu-button');
SEIM_ACCESSIBILITY.addARIA(button, {
    'aria-expanded': 'false',
    'aria-controls': 'menu',
    'aria-label': 'Toggle navigation menu'
});
```

#### `validateAccessibility(container = document)`
Validate accessibility of a container.

**Parameters:**
- `container` (Element): Container to validate

**Returns:** Object with validation results

**Example:**
```javascript
const results = SEIM_ACCESSIBILITY.validateAccessibility('#main-content');
console.log('Accessibility issues:', results.issues);
```

## UI Enhanced Module

The UI Enhanced module provides skeleton loading, progressive loading, and error recovery.

### Global Access
```javascript
window.SEIM_UI_ENHANCED
```

### Configuration
```javascript
const config = {
    enableSkeletonLoading: true,  // Enable skeleton loading
    enableProgressiveLoading: true, // Enable progressive loading
    enableErrorRecovery: true,    // Enable error recovery
    skeletonDuration: 2000,      // Skeleton display duration
    retryAttempts: 3             // Error recovery retry attempts
};
```

### Methods

#### `init(options = {})`
Initialize the UI enhanced module.

**Parameters:**
- `options` (Object): Configuration options

**Example:**
```javascript
SEIM_UI_ENHANCED.init({
    enableSkeletonLoading: true,
    enableErrorRecovery: true
});
```

#### `showSkeleton(container, template = 'default')`
Show skeleton loading in a container.

**Parameters:**
- `container` (string): Container selector
- `template` (string): Skeleton template

**Example:**
```javascript
SEIM_UI_ENHANCED.showSkeleton('#applications-list', 'table');
```

#### `hideSkeleton(container)`
Hide skeleton loading.

**Parameters:**
- `container` (string): Container selector

**Example:**
```javascript
SEIM_UI_ENHANCED.hideSkeleton('#applications-list');
```

#### `loadProgressive(container, dataLoader, options = {})`
Load content progressively.

**Parameters:**
- `container` (string): Container selector
- `dataLoader` (Function): Data loading function
- `options` (Object): Loading options
  - `skeleton` (boolean): Show skeleton while loading
  - `retry` (boolean): Enable retry on failure
  - `onProgress` (Function): Progress callback

**Returns:** Promise

**Example:**
```javascript
await SEIM_UI_ENHANCED.loadProgressive('#applications-list', async () => {
    return await SEIM_API.get('/applications');
}, {
    skeleton: true,
    retry: true,
    onProgress: (progress) => {
        console.log('Loading progress:', progress);
    }
});
```

#### `handleError(error, container, retryFunction = null)`
Handle errors with recovery options.

**Parameters:**
- `error` (Error): Error object
- `container` (string): Container selector
- `retryFunction` (Function, optional): Function to retry

**Example:**
```javascript
SEIM_UI_ENHANCED.handleError(error, '#applications-list', async () => {
    return await SEIM_API.get('/applications');
});
```

#### `createSkeletonTemplate(type, options = {})`
Create a custom skeleton template.

**Parameters:**
- `type` (string): Template type
- `options` (Object): Template options

**Returns:** HTML string

**Example:**
```javascript
const customTemplate = SEIM_UI_ENHANCED.createSkeletonTemplate('card', {
    count: 6,
    height: '200px'
});
```

## Performance Module

The Performance module provides real-time monitoring, metrics collection, and performance alerts.

### Global Access
```javascript
window.SEIM_PERFORMANCE
```

### Configuration
```javascript
const config = {
    enabled: true,              // Enable performance monitoring
    logMetrics: false,          // Log metrics to console
    monitorMemory: true,        // Monitor memory usage
    monitorNetwork: true,       // Monitor network performance
    alertThresholds: {          // Performance alert thresholds
        pageLoad: 3000,         // Page load time threshold
        memoryUsage: 0.8,       // Memory usage threshold
        apiResponse: 5000       // API response time threshold
    }
};
```

### Methods

#### `init(options = {})`
Initialize the performance module.

**Parameters:**
- `options` (Object): Configuration options

**Example:**
```javascript
SEIM_PERFORMANCE.init({
    enabled: true,
    monitorMemory: true,
    alertThresholds: {
        pageLoad: 2000,
        apiResponse: 3000
    }
});
```

#### `measurePageLoad()`
Measure page load performance.

**Returns:** Object with page load metrics

**Example:**
```javascript
const metrics = SEIM_PERFORMANCE.measurePageLoad();
console.log('Page load time:', metrics.loadTime);
console.log('DOM ready time:', metrics.domReadyTime);
```

#### `measureInteraction(label, fn)`
Measure user interaction performance.

**Parameters:**
- `label` (string): Interaction label
- `fn` (Function): Function to measure

**Returns:** Promise with measurement result

**Example:**
```javascript
const result = await SEIM_PERFORMANCE.measureInteraction('button-click', async () => {
    await handleButtonClick();
});
```

#### `getMemoryUsage()`
Get current memory usage.

**Returns:** Object with memory metrics

**Example:**
```javascript
const memory = SEIM_PERFORMANCE.getMemoryUsage();
console.log('Memory usage:', memory.usedJSHeapSize);
console.log('Memory limit:', memory.jsHeapSizeLimit);
```

#### `getNetworkMetrics()`
Get network performance metrics.

**Returns:** Object with network metrics

**Example:**
```javascript
const network = SEIM_PERFORMANCE.getNetworkMetrics();
console.log('Network type:', network.effectiveType);
console.log('Downlink:', network.downlink);
```

#### `setAlertThreshold(type, value)`
Set performance alert threshold.

**Parameters:**
- `type` (string): Alert type
- `value` (number): Threshold value

**Example:**
```javascript
SEIM_PERFORMANCE.setAlertThreshold('pageLoad', 2000);
SEIM_PERFORMANCE.setAlertThreshold('apiResponse', 3000);
```

#### `getMetrics()`
Get all performance metrics.

**Returns:** Object with all metrics

**Example:**
```javascript
const metrics = SEIM_PERFORMANCE.getMetrics();
console.log('All metrics:', metrics);
```

## Dynamic Loader Module

The Dynamic Loader module provides code splitting and lazy loading for optimal performance.

### Global Access
```javascript
window.SEIM_DYNAMIC_LOADER
```

### Configuration
```javascript
const config = {
    enabled: true,              // Enable dynamic loading
    preload: false,             // Preload modules
    cache: true,               // Cache loaded modules
    timeout: 10000,            // Loading timeout
    retryAttempts: 3           // Retry attempts on failure
};
```

### Methods

#### `init(options = {})`
Initialize the dynamic loader module.

**Parameters:**
- `options` (Object): Configuration options

**Example:**
```javascript
SEIM_DYNAMIC_LOADER.init({
    enabled: true,
    preload: false,
    cache: true
});
```

#### `loadModule(moduleName, options = {})`
Load a module dynamically.

**Parameters:**
- `moduleName` (string): Module name
- `options` (Object): Loading options
  - `force` (boolean): Force reload even if cached
  - `timeout` (number): Loading timeout
  - `onProgress` (Function): Progress callback

**Returns:** Promise with loaded module

**Example:**
```javascript
try {
    const module = await SEIM_DYNAMIC_LOADER.loadModule('heavy-module', {
        timeout: 15000,
        onProgress: (progress) => {
            console.log('Loading progress:', progress);
        }
    });
    
    // Use the loaded module
    module.init();
} catch (error) {
    SEIM_LOGGER.error('Failed to load module', { module: 'heavy-module', error });
}
```

#### `preloadModule(moduleName)`
Preload a module for faster access.

**Parameters:**
- `moduleName` (string): Module name

**Returns:** Promise

**Example:**
```javascript
// Preload module in background
SEIM_DYNAMIC_LOADER.preloadModule('chart-module');
```

#### `isModuleLoaded(moduleName)`
Check if a module is loaded.

**Parameters:**
- `moduleName` (string): Module name

**Returns:** boolean

**Example:**
```javascript
if (SEIM_DYNAMIC_LOADER.isModuleLoaded('chart-module')) {
    // Module is already loaded
    initializeCharts();
} else {
    // Load module first
    await SEIM_DYNAMIC_LOADER.loadModule('chart-module');
    initializeCharts();
}
```

#### `unloadModule(moduleName)`
Unload a module to free memory.

**Parameters:**
- `moduleName` (string): Module name

**Returns:** Promise

**Example:**
```javascript
await SEIM_DYNAMIC_LOADER.unloadModule('unused-module');
```

#### `getLoadedModules()`
Get list of loaded modules.

**Returns:** Array of loaded module names

**Example:**
```javascript
const loadedModules = SEIM_DYNAMIC_LOADER.getLoadedModules();
console.log('Loaded modules:', loadedModules);
```

## Utils Module

The Utils module provides common utility functions used across the application.

### Global Access
```javascript
window.SEIM_UTILS
```

### Methods

#### `debounce(func, wait)`
Create a debounced function.

**Parameters:**
- `func` (Function): Function to debounce
- `wait` (number): Debounce delay in milliseconds

**Returns:** Debounced function

**Example:**
```javascript
const debouncedSearch = SEIM_UTILS.debounce(async (query) => {
    const results = await SEIM_API.get('/search', { params: { q: query } });
    displayResults(results);
}, 300);

// Use debounced function
searchInput.addEventListener('input', (e) => {
    debouncedSearch(e.target.value);
});
```

#### `throttle(func, limit)`
Create a throttled function.

**Parameters:**
- `func` (Function): Function to throttle
- `limit` (number): Throttle limit in milliseconds

**Returns:** Throttled function

**Example:**
```javascript
const throttledScroll = SEIM_UTILS.throttle(() => {
    updateScrollPosition();
}, 100);

window.addEventListener('scroll', throttledScroll);
```

#### `formatDate(date, format = 'YYYY-MM-DD')`
Format a date.

**Parameters:**
- `date` (Date|string): Date to format
- `format` (string): Date format

**Returns:** Formatted date string

**Example:**
```javascript
const formattedDate = SEIM_UTILS.formatDate(new Date(), 'MM/DD/YYYY');
const isoDate = SEIM_UTILS.formatDate('2023-12-01', 'YYYY-MM-DD');
```

#### `formatCurrency(amount, currency = 'USD')`
Format a currency amount.

**Parameters:**
- `amount` (number): Amount to format
- `currency` (string): Currency code

**Returns:** Formatted currency string

**Example:**
```javascript
const formattedAmount = SEIM_UTILS.formatCurrency(1234.56, 'USD');
// Returns: "$1,234.56"
```

#### `validateEmail(email)`
Validate an email address.

**Parameters:**
- `email` (string): Email to validate

**Returns:** boolean

**Example:**
```javascript
if (SEIM_UTILS.validateEmail('user@example.com')) {
    // Email is valid
} else {
    // Email is invalid
}
```

#### `generateId(length = 8)`
Generate a random ID.

**Parameters:**
- `length` (number): ID length

**Returns:** Random ID string

**Example:**
```javascript
const id = SEIM_UTILS.generateId(12);
// Returns: "a1b2c3d4e5f6"
```

#### `deepClone(obj)`
Create a deep clone of an object.

**Parameters:**
- `obj` (Object): Object to clone

**Returns:** Cloned object

**Example:**
```javascript
const original = { user: { name: 'John', settings: { theme: 'dark' } } };
const cloned = SEIM_UTILS.deepClone(original);
```

#### `isEmpty(value)`
Check if a value is empty.

**Parameters:**
- `value` (any): Value to check

**Returns:** boolean

**Example:**
```javascript
SEIM_UTILS.isEmpty('');        // true
SEIM_UTILS.isEmpty([]);        // true
SEIM_UTILS.isEmpty({});        // true
SEIM_UTILS.isEmpty(null);      // true
SEIM_UTILS.isEmpty(undefined); // true
SEIM_UTILS.isEmpty('hello');   // false
```

#### `getQueryParams()`
Get URL query parameters.

**Returns:** Object with query parameters

**Example:**
```javascript
// URL: /page?id=123&status=pending
const params = SEIM_UTILS.getQueryParams();
// Returns: { id: '123', status: 'pending' }
```

#### `setQueryParams(params)`
Set URL query parameters.

**Parameters:**
- `params` (Object): Query parameters to set

**Example:**
```javascript
SEIM_UTILS.setQueryParams({ 
    page: 2, 
    status: 'approved' 
});
// Updates URL to: /page?page=2&status=approved
```

This API reference provides comprehensive documentation for all frontend modules and their methods. Each module is designed to work independently while providing seamless integration with other modules through the global SEIM namespace. 