/**
 * SEIM Performance Monitoring Module
 * Tracks API calls, bundle loading, and user interactions for optimization
 */

export class PerformanceMonitor {
    constructor() {
        this.metrics = {
            apiCalls: new Map(),
            bundleLoads: new Map(),
            userInteractions: [],
            pageLoads: new Map(),
            errors: []
        };
        
        this.config = {
            maxApiCallHistory: 100,
            maxInteractionHistory: 50,
            enableRealTimeMonitoring: true,
            reportInterval: 30000 // 30 seconds
        };
        
        this.init();
    }
    
    init() {
        this.setupPerformanceObserver();
        this.setupErrorTracking();
        this.setupUserInteractionTracking();
        this.startPeriodicReporting();
        
        // Track initial page load
        this.trackPageLoad();
    }
    
    /**
     * Track API call performance
     */
    trackApiCall(url, method, startTime, endTime, status, error = null) {
        const duration = endTime - startTime;
        const callId = `${method}_${url}_${Date.now()}`;
        
        const apiCall = {
            id: callId,
            url,
            method,
            duration,
            status,
            timestamp: new Date().toISOString(),
            error: error ? error.message : null
        };
        
        this.metrics.apiCalls.set(callId, apiCall);
        
        // Keep only recent calls
        if (this.metrics.apiCalls.size > this.config.maxApiCallHistory) {
            const firstKey = this.metrics.apiCalls.keys().next().value;
            this.metrics.apiCalls.delete(firstKey);
        }
        
        // Log slow API calls
        if (duration > 2000) {
            console.warn(`Slow API call detected: ${method} ${url} took ${duration}ms`);
        }
        
        return apiCall;
    }
    
    /**
     * Track bundle loading performance
     */
    trackBundleLoad(bundleName, startTime, endTime, size) {
        const duration = endTime - startTime;
        const bundleId = `${bundleName}_${Date.now()}`;
        
        const bundleLoad = {
            id: bundleId,
            name: bundleName,
            duration,
            size,
            timestamp: new Date().toISOString()
        };
        
        this.metrics.bundleLoads.set(bundleId, bundleLoad);
        
        // Log slow bundle loads
        if (duration > 1000) {
            console.warn(`Slow bundle load detected: ${bundleName} took ${duration}ms`);
        }
        
        return bundleLoad;
    }
    
    /**
     * Track user interactions
     */
    trackUserInteraction(type, target, duration = 0) {
        const interaction = {
            type,
            target: target?.tagName || target?.className || 'unknown',
            duration,
            timestamp: new Date().toISOString()
        };
        
        this.metrics.userInteractions.push(interaction);
        
        // Keep only recent interactions
        if (this.metrics.userInteractions.length > this.config.maxInteractionHistory) {
            this.metrics.userInteractions.shift();
        }
    }
    
    /**
     * Track page load performance
     */
    trackPageLoad() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const paint = performance.getEntriesByType('paint');
        
        const pageLoad = {
            url: window.location.href,
            timestamp: new Date().toISOString(),
            navigation: {
                domContentLoaded: navigation?.domContentLoadedEventEnd - navigation?.domContentLoadedEventStart,
                loadComplete: navigation?.loadEventEnd - navigation?.loadEventStart,
                total: navigation?.duration
            },
            paint: {
                firstPaint: paint.find(p => p.name === 'first-paint')?.startTime,
                firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime
            }
        };
        
        this.metrics.pageLoads.set(window.location.href, pageLoad);
        
        // Log performance metrics
        console.log('Page Load Performance:', pageLoad);
    }
    
    /**
     * Track errors
     */
    trackError(error, context = {}) {
        const errorRecord = {
            message: error.message,
            stack: error.stack,
            context,
            timestamp: new Date().toISOString()
        };
        
        this.metrics.errors.push(errorRecord);
        
        // Keep only recent errors
        if (this.metrics.errors.length > 20) {
            this.metrics.errors.shift();
        }
    }
    
    /**
     * Setup Performance Observer for automatic tracking
     */
    setupPerformanceObserver() {
        if (!window.PerformanceObserver) return;
        
        // Observe navigation timing
        const navigationObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'navigation') {
                    this.trackPageLoad();
                }
            }
        });
        
        try {
            navigationObserver.observe({ entryTypes: ['navigation'] });
        } catch (e) {
            console.warn('PerformanceObserver not supported:', e);
        }
    }
    
    /**
     * Setup error tracking
     */
    setupErrorTracking() {
        window.addEventListener('error', (event) => {
            this.trackError(event.error, {
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.trackError(new Error(event.reason), {
                type: 'unhandledrejection'
            });
        });
    }
    
    /**
     * Setup user interaction tracking
     */
    setupUserInteractionTracking() {
        const interactionTypes = ['click', 'input', 'submit', 'scroll'];
        
        interactionTypes.forEach(type => {
            document.addEventListener(type, (event) => {
                this.trackUserInteraction(type, event.target);
            }, { passive: true });
        });
    }
    
    /**
     * Start periodic performance reporting
     */
    startPeriodicReporting() {
        if (!this.config.enableRealTimeMonitoring) return;
        
        setInterval(() => {
            this.reportMetrics();
        }, this.config.reportInterval);
    }
    
    /**
     * Report performance metrics
     */
    reportMetrics() {
        const report = {
            timestamp: new Date().toISOString(),
            apiCalls: {
                total: this.metrics.apiCalls.size,
                averageDuration: this.calculateAverageApiDuration(),
                slowCalls: this.getSlowApiCalls()
            },
            bundleLoads: {
                total: this.metrics.bundleLoads.size,
                averageDuration: this.calculateAverageBundleDuration()
            },
            userInteractions: {
                total: this.metrics.userInteractions.length,
                recent: this.metrics.userInteractions.slice(-10)
            },
            errors: {
                total: this.metrics.errors.length,
                recent: this.metrics.errors.slice(-5)
            }
        };
        
        // Send to analytics or log
        if (window.SEIM_LOGGER) {
            window.SEIM_LOGGER.info('Performance Report', report);
        } else {
            console.log('Performance Report:', report);
        }
    }
    
    /**
     * Calculate average API call duration
     */
    calculateAverageApiDuration() {
        const calls = Array.from(this.metrics.apiCalls.values());
        if (calls.length === 0) return 0;
        
        const totalDuration = calls.reduce((sum, call) => sum + call.duration, 0);
        return totalDuration / calls.length;
    }
    
    /**
     * Calculate average bundle load duration
     */
    calculateAverageBundleDuration() {
        const loads = Array.from(this.metrics.bundleLoads.values());
        if (loads.length === 0) return 0;
        
        const totalDuration = loads.reduce((sum, load) => sum + load.duration, 0);
        return totalDuration / loads.length;
    }
    
    /**
     * Get slow API calls (> 1 second)
     */
    getSlowApiCalls() {
        return Array.from(this.metrics.apiCalls.values())
            .filter(call => call.duration > 1000)
            .slice(-5);
    }
    
    /**
     * Get performance summary
     */
    getSummary() {
        return {
            apiCalls: this.metrics.apiCalls.size,
            bundleLoads: this.metrics.bundleLoads.size,
            userInteractions: this.metrics.userInteractions.length,
            errors: this.metrics.errors.length,
            averageApiDuration: this.calculateAverageApiDuration(),
            averageBundleDuration: this.calculateAverageBundleDuration()
        };
    }
    
    /**
     * Clear metrics (useful for testing)
     */
    clear() {
        this.metrics.apiCalls.clear();
        this.metrics.bundleLoads.clear();
        this.metrics.userInteractions = [];
        this.metrics.pageLoads.clear();
        this.metrics.errors = [];
    }
}

export const performanceMonitor = new PerformanceMonitor(); 