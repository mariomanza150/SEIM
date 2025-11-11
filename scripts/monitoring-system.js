#!/usr/bin/env node

/**
 * SEIM Frontend Monitoring System
 * Provides error tracking, performance monitoring, user analytics, and alerting
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// Configuration
const config = {
    // Monitoring settings
    enabled: true,
    logLevel: 'info',
    metricsInterval: 60000, // 1 minute
    retentionDays: 30,
    
    // Error tracking
    errorTracking: {
        enabled: true,
        captureUnhandled: true,
        captureConsole: true,
        maxErrors: 1000
    },
    
    // Performance monitoring
    performanceMonitoring: {
        enabled: true,
        metrics: ['loadTime', 'memoryUsage', 'bundleSize', 'apiResponseTime'],
        thresholds: {
            loadTime: 3000,
            memoryUsage: 0.8,
            bundleSize: 500,
            apiResponseTime: 5000
        }
    },
    
    // User analytics
    userAnalytics: {
        enabled: true,
        trackPageViews: true,
        trackUserActions: true,
        trackErrors: true,
        anonymizeData: true
    },
    
    // Alerting
    alerting: {
        enabled: true,
        channels: {
            email: process.env.ALERT_EMAIL || null,
            slack: process.env.SLACK_WEBHOOK || null,
            webhook: process.env.WEBHOOK_URL || null
        },
        thresholds: {
            errorRate: 0.05,      // 5% error rate
            responseTime: 5000,   // 5 seconds
            memoryUsage: 0.9,     // 90% memory usage
            bundleSize: 1000      // 1MB bundle size
        }
    },
    
    // Storage
    storage: {
        type: 'file', // file, database, external
        path: 'monitoring-data',
        maxSize: '100MB'
    }
};

// Colors for console output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

// Utility functions
function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logHeader(message) {
    log('\n' + '='.repeat(60), 'cyan');
    log(` ${message}`, 'bright');
    log('='.repeat(60), 'cyan');
}

function logSection(message) {
    log('\n' + '-'.repeat(40), 'blue');
    log(` ${message}`, 'blue');
    log('-'.repeat(40), 'blue');
}

function logSuccess(message) {
    log(`✅ ${message}`, 'green');
}

function logError(message) {
    log(`❌ ${message}`, 'red');
}

function logWarning(message) {
    log(`⚠️  ${message}`, 'yellow');
}

function logInfo(message) {
    log(`ℹ️  ${message}`, 'blue');
}

// Monitoring system class
class MonitoringSystem {
    constructor() {
        this.metrics = {
            errors: [],
            performance: [],
            userActions: [],
            alerts: []
        };
        
        this.stats = {
            totalErrors: 0,
            totalRequests: 0,
            averageResponseTime: 0,
            peakMemoryUsage: 0,
            uniqueUsers: new Set()
        };
        
        this.isRunning = false;
        this.metricsInterval = null;
    }

    /**
     * Initialize the monitoring system
     */
    async init() {
        logHeader('SEIM Frontend Monitoring System');
        
        if (!config.enabled) {
            logInfo('Monitoring system disabled');
            return;
        }
        
        try {
            // Setup storage
            this.setupStorage();
            
            // Setup error tracking
            if (config.errorTracking.enabled) {
                this.setupErrorTracking();
            }
            
            // Setup performance monitoring
            if (config.performanceMonitoring.enabled) {
                this.setupPerformanceMonitoring();
            }
            
            // Setup user analytics
            if (config.userAnalytics.enabled) {
                this.setupUserAnalytics();
            }
            
            // Start metrics collection
            this.startMetricsCollection();
            
            logSuccess('Monitoring system initialized successfully');
            
        } catch (error) {
            logError(`Monitoring system initialization failed: ${error.message}`);
            throw error;
        }
    }

    /**
     * Setup storage for monitoring data
     */
    setupStorage() {
        const storagePath = path.join(process.cwd(), config.storage.path);
        
        if (!fs.existsSync(storagePath)) {
            fs.mkdirSync(storagePath, { recursive: true });
        }
        
        // Create subdirectories
        const subdirs = ['errors', 'performance', 'analytics', 'alerts'];
        subdirs.forEach(dir => {
            const dirPath = path.join(storagePath, dir);
            if (!fs.existsSync(dirPath)) {
                fs.mkdirSync(dirPath, { recursive: true });
            }
        });
        
        logInfo(`Storage setup at ${storagePath}`);
    }

    /**
     * Setup error tracking
     */
    setupErrorTracking() {
        // Capture unhandled errors
        if (config.errorTracking.captureUnhandled) {
            process.on('uncaughtException', (error) => {
                this.trackError(error, 'uncaught');
            });
            
            process.on('unhandledRejection', (reason, promise) => {
                this.trackError(reason, 'unhandled_rejection');
            });
        }
        
        // Capture console errors
        if (config.errorTracking.captureConsole) {
            const originalError = console.error;
            console.error = (...args) => {
                this.trackError(args.join(' '), 'console');
                originalError.apply(console, args);
            };
        }
        
        logInfo('Error tracking setup completed');
    }

    /**
     * Setup performance monitoring
     */
    setupPerformanceMonitoring() {
        // Monitor memory usage
        setInterval(() => {
            if (global.gc) {
                global.gc(); // Force garbage collection if available
            }
            
            const memoryUsage = process.memoryUsage();
            this.trackPerformance('memoryUsage', {
                rss: memoryUsage.rss,
                heapUsed: memoryUsage.heapUsed,
                heapTotal: memoryUsage.heapTotal,
                external: memoryUsage.external
            });
        }, config.metricsInterval);
        
        logInfo('Performance monitoring setup completed');
    }

    /**
     * Setup user analytics
     */
    setupUserAnalytics() {
        // Track page views (simulated for server-side monitoring)
        this.trackUserAction('page_view', {
            page: '/',
            timestamp: new Date().toISOString()
        });
        
        logInfo('User analytics setup completed');
    }

    /**
     * Start metrics collection
     */
    startMetricsCollection() {
        if (this.isRunning) {
            return;
        }
        
        this.isRunning = true;
        
        // Collect metrics at regular intervals
        this.metricsInterval = setInterval(() => {
            this.collectMetrics();
        }, config.metricsInterval);
        
        logInfo('Metrics collection started');
    }

    /**
     * Stop metrics collection
     */
    stopMetricsCollection() {
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
            this.metricsInterval = null;
        }
        
        this.isRunning = false;
        logInfo('Metrics collection stopped');
    }

    /**
     * Track an error
     */
    trackError(error, type = 'unknown') {
        if (!config.errorTracking.enabled) {
            return;
        }
        
        const errorData = {
            id: this.generateId(),
            type: type,
            message: error.message || error.toString(),
            stack: error.stack,
            timestamp: new Date().toISOString(),
            userAgent: process.env.USER_AGENT || 'server',
            url: process.env.REQUEST_URL || '/',
            userId: this.anonymizeUserId(process.env.USER_ID || 'anonymous')
        };
        
        this.metrics.errors.push(errorData);
        this.stats.totalErrors++;
        
        // Limit stored errors
        if (this.metrics.errors.length > config.errorTracking.maxErrors) {
            this.metrics.errors.shift();
        }
        
        // Check for alerting
        this.checkErrorAlerts();
        
        // Save error data
        this.saveErrorData(errorData);
        
        logWarning(`Error tracked: ${errorData.message}`);
    }

    /**
     * Track performance metrics
     */
    trackPerformance(metric, value) {
        if (!config.performanceMonitoring.enabled) {
            return;
        }
        
        const performanceData = {
            id: this.generateId(),
            metric: metric,
            value: value,
            timestamp: new Date().toISOString(),
            threshold: config.performanceMonitoring.thresholds[metric] || null
        };
        
        this.metrics.performance.push(performanceData);
        
        // Update stats
        if (metric === 'memoryUsage') {
            const memoryPercent = value.heapUsed / value.heapTotal;
            if (memoryPercent > this.stats.peakMemoryUsage) {
                this.stats.peakMemoryUsage = memoryPercent;
            }
        }
        
        // Check for alerting
        this.checkPerformanceAlerts(performanceData);
        
        // Save performance data
        this.savePerformanceData(performanceData);
    }

    /**
     * Track user action
     */
    trackUserAction(action, data) {
        if (!config.userAnalytics.enabled) {
            return;
        }
        
        const userData = {
            id: this.generateId(),
            action: action,
            data: data,
            timestamp: new Date().toISOString(),
            userId: this.anonymizeUserId(data.userId || 'anonymous'),
            sessionId: data.sessionId || this.generateId()
        };
        
        this.metrics.userActions.push(userData);
        this.stats.uniqueUsers.add(userData.userId);
        
        // Save user data
        this.saveUserData(userData);
    }

    /**
     * Track API request
     */
    trackApiRequest(url, method, duration, statusCode) {
        this.stats.totalRequests++;
        
        // Update average response time
        const currentAvg = this.stats.averageResponseTime;
        const requestCount = this.stats.totalRequests;
        this.stats.averageResponseTime = (currentAvg * (requestCount - 1) + duration) / requestCount;
        
        // Track performance
        this.trackPerformance('apiResponseTime', {
            url: url,
            method: method,
            duration: duration,
            statusCode: statusCode
        });
        
        // Track user action
        this.trackUserAction('api_request', {
            url: url,
            method: method,
            duration: duration,
            statusCode: statusCode
        });
    }

    /**
     * Collect all metrics
     */
    collectMetrics() {
        const metrics = {
            timestamp: new Date().toISOString(),
            stats: { ...this.stats },
            memory: process.memoryUsage(),
            uptime: process.uptime(),
            cpu: process.cpuUsage()
        };
        
        // Save metrics
        this.saveMetrics(metrics);
        
        // Check for alerts
        this.checkAlerts();
    }

    /**
     * Check for error alerts
     */
    checkErrorAlerts() {
        const errorRate = this.calculateErrorRate();
        
        if (errorRate > config.alerting.thresholds.errorRate) {
            this.createAlert('high_error_rate', {
                errorRate: errorRate,
                threshold: config.alerting.thresholds.errorRate,
                totalErrors: this.stats.totalErrors,
                totalRequests: this.stats.totalRequests
            });
        }
    }

    /**
     * Check for performance alerts
     */
    checkPerformanceAlerts(performanceData) {
        const threshold = performanceData.threshold;
        if (!threshold) {
            return;
        }
        
        let value = performanceData.value;
        if (typeof value === 'object') {
            value = value.duration || value.heapUsed / value.heapTotal;
        }
        
        if (value > threshold) {
            this.createAlert('performance_threshold_exceeded', {
                metric: performanceData.metric,
                value: value,
                threshold: threshold,
                timestamp: performanceData.timestamp
            });
        }
    }

    /**
     * Check for general alerts
     */
    checkAlerts() {
        // Check memory usage
        const memoryUsage = process.memoryUsage();
        const memoryPercent = memoryUsage.heapUsed / memoryUsage.heapTotal;
        
        if (memoryPercent > config.alerting.thresholds.memoryUsage) {
            this.createAlert('high_memory_usage', {
                memoryPercent: memoryPercent,
                threshold: config.alerting.thresholds.memoryUsage,
                heapUsed: memoryUsage.heapUsed,
                heapTotal: memoryUsage.heapTotal
            });
        }
        
        // Check response time
        if (this.stats.averageResponseTime > config.alerting.thresholds.responseTime) {
            this.createAlert('high_response_time', {
                averageResponseTime: this.stats.averageResponseTime,
                threshold: config.alerting.thresholds.responseTime,
                totalRequests: this.stats.totalRequests
            });
        }
    }

    /**
     * Create an alert
     */
    createAlert(type, data) {
        const alert = {
            id: this.generateId(),
            type: type,
            data: data,
            timestamp: new Date().toISOString(),
            severity: this.calculateSeverity(type, data)
        };
        
        this.metrics.alerts.push(alert);
        
        // Save alert
        this.saveAlertData(alert);
        
        // Send alert notifications
        this.sendAlertNotifications(alert);
        
        logWarning(`Alert created: ${type} - ${JSON.stringify(data)}`);
    }

    /**
     * Calculate alert severity
     */
    calculateSeverity(type, data) {
        switch (type) {
            case 'high_error_rate':
                return data.errorRate > 0.1 ? 'critical' : 'warning';
            case 'performance_threshold_exceeded':
                return 'warning';
            case 'high_memory_usage':
                return data.memoryPercent > 0.95 ? 'critical' : 'warning';
            case 'high_response_time':
                return 'warning';
            default:
                return 'info';
        }
    }

    /**
     * Calculate error rate
     */
    calculateErrorRate() {
        if (this.stats.totalRequests === 0) {
            return 0;
        }
        
        return this.stats.totalErrors / this.stats.totalRequests;
    }

    /**
     * Send alert notifications
     */
    async sendAlertNotifications(alert) {
        if (!config.alerting.enabled) {
            return;
        }
        
        const message = this.formatAlertMessage(alert);
        
        // Send to Slack
        if (config.alerting.channels.slack) {
            await this.sendSlackNotification(message);
        }
        
        // Send to webhook
        if (config.alerting.channels.webhook) {
            await this.sendWebhookNotification(alert);
        }
        
        // Send email (simulated)
        if (config.alerting.channels.email) {
            await this.sendEmailNotification(message);
        }
    }

    /**
     * Format alert message
     */
    formatAlertMessage(alert) {
        const emoji = {
            critical: '🚨',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        return {
            text: `${emoji[alert.severity]} SEIM Frontend Alert: ${alert.type}`,
            attachments: [{
                color: alert.severity === 'critical' ? 'danger' : 'warning',
                fields: Object.entries(alert.data).map(([key, value]) => ({
                    title: key,
                    value: typeof value === 'number' ? value.toFixed(2) : value.toString(),
                    short: true
                })),
                footer: `Alert ID: ${alert.id}`,
                ts: Math.floor(new Date(alert.timestamp).getTime() / 1000)
            }]
        };
    }

    /**
     * Send Slack notification
     */
    async sendSlackNotification(message) {
        try {
            const data = JSON.stringify(message);
            
            const options = {
                hostname: 'hooks.slack.com',
                port: 443,
                path: config.alerting.channels.slack,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': data.length
                }
            };
            
            const req = https.request(options, (res) => {
                if (res.statusCode === 200) {
                    logSuccess('Slack alert sent');
                } else {
                    logError(`Slack alert failed: ${res.statusCode}`);
                }
            });
            
            req.on('error', (error) => {
                logError(`Slack alert error: ${error.message}`);
            });
            
            req.write(data);
            req.end();
            
        } catch (error) {
            logError(`Slack alert failed: ${error.message}`);
        }
    }

    /**
     * Send webhook notification
     */
    async sendWebhookNotification(alert) {
        try {
            const data = JSON.stringify(alert);
            
            const url = new URL(config.alerting.channels.webhook);
            const options = {
                hostname: url.hostname,
                port: url.port || (url.protocol === 'https:' ? 443 : 80),
                path: url.pathname + url.search,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': data.length
                }
            };
            
            const protocol = url.protocol === 'https:' ? https : http;
            const req = protocol.request(options, (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    logSuccess('Webhook alert sent');
                } else {
                    logError(`Webhook alert failed: ${res.statusCode}`);
                }
            });
            
            req.on('error', (error) => {
                logError(`Webhook alert error: ${error.message}`);
            });
            
            req.write(data);
            req.end();
            
        } catch (error) {
            logError(`Webhook alert failed: ${error.message}`);
        }
    }

    /**
     * Send email notification (simulated)
     */
    async sendEmailNotification(message) {
        logInfo(`Email alert would be sent to: ${config.alerting.channels.email}`);
        logInfo(`Subject: ${message.text}`);
        logInfo(`Body: ${JSON.stringify(message.attachments[0].fields)}`);
    }

    /**
     * Save error data
     */
    saveErrorData(errorData) {
        const filePath = path.join(
            process.cwd(),
            config.storage.path,
            'errors',
            `${errorData.id}.json`
        );
        
        fs.writeFileSync(filePath, JSON.stringify(errorData, null, 2));
    }

    /**
     * Save performance data
     */
    savePerformanceData(performanceData) {
        const filePath = path.join(
            process.cwd(),
            config.storage.path,
            'performance',
            `${performanceData.id}.json`
        );
        
        fs.writeFileSync(filePath, JSON.stringify(performanceData, null, 2));
    }

    /**
     * Save user data
     */
    saveUserData(userData) {
        const filePath = path.join(
            process.cwd(),
            config.storage.path,
            'analytics',
            `${userData.id}.json`
        );
        
        fs.writeFileSync(filePath, JSON.stringify(userData, null, 2));
    }

    /**
     * Save alert data
     */
    saveAlertData(alertData) {
        const filePath = path.join(
            process.cwd(),
            config.storage.path,
            'alerts',
            `${alertData.id}.json`
        );
        
        fs.writeFileSync(filePath, JSON.stringify(alertData, null, 2));
    }

    /**
     * Save metrics
     */
    saveMetrics(metrics) {
        const filePath = path.join(
            process.cwd(),
            config.storage.path,
            `metrics-${Date.now()}.json`
        );
        
        fs.writeFileSync(filePath, JSON.stringify(metrics, null, 2));
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * Anonymize user ID
     */
    anonymizeUserId(userId) {
        if (!config.userAnalytics.anonymizeData) {
            return userId;
        }
        
        // Simple hash for anonymization
        let hash = 0;
        for (let i = 0; i < userId.length; i++) {
            const char = userId.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        
        return `user_${Math.abs(hash).toString(36)}`;
    }

    /**
     * Get monitoring statistics
     */
    getStats() {
        return {
            ...this.stats,
            uniqueUsers: this.stats.uniqueUsers.size,
            errorRate: this.calculateErrorRate(),
            alerts: this.metrics.alerts.length,
            isRunning: this.isRunning
        };
    }

    /**
     * Generate monitoring report
     */
    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            stats: this.getStats(),
            metrics: {
                errors: this.metrics.errors.length,
                performance: this.metrics.performance.length,
                userActions: this.metrics.userActions.length,
                alerts: this.metrics.alerts.length
            },
            recentAlerts: this.metrics.alerts.slice(-10),
            recentErrors: this.metrics.errors.slice(-10)
        };
        
        const reportPath = path.join(
            process.cwd(),
            config.storage.path,
            `monitoring-report-${Date.now()}.json`
        );
        
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        
        logInfo(`Monitoring report saved to ${reportPath}`);
        return report;
    }

    /**
     * Cleanup old data
     */
    cleanupOldData() {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - config.retentionDays);
        
        const storagePath = path.join(process.cwd(), config.storage.path);
        const subdirs = ['errors', 'performance', 'analytics', 'alerts'];
        
        subdirs.forEach(dir => {
            const dirPath = path.join(storagePath, dir);
            if (fs.existsSync(dirPath)) {
                const files = fs.readdirSync(dirPath);
                
                files.forEach(file => {
                    const filePath = path.join(dirPath, file);
                    const stats = fs.statSync(filePath);
                    
                    if (stats.mtime < cutoffDate) {
                        fs.unlinkSync(filePath);
                        logInfo(`Cleaned up old file: ${filePath}`);
                    }
                });
            }
        });
        
        logSuccess('Data cleanup completed');
    }
}

// CLI argument parsing
function parseArguments() {
    const args = process.argv.slice(2);
    const options = {
        start: false,
        stop: false,
        report: false,
        cleanup: false,
        stats: false
    };
    
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        
        switch (arg) {
            case '--start':
                options.start = true;
                break;
            case '--stop':
                options.stop = true;
                break;
            case '--report':
                options.report = true;
                break;
            case '--cleanup':
                options.cleanup = true;
                break;
            case '--stats':
                options.stats = true;
                break;
            case '--help':
            case '-h':
                showHelp();
                process.exit(0);
                break;
            default:
                logWarning(`Unknown argument: ${arg}`);
                break;
        }
    }
    
    return options;
}

function showHelp() {
    logHeader('SEIM Monitoring System Help');
    log(`
Usage: node scripts/monitoring-system.js [options]

Options:
  --start              Start the monitoring system
  --stop               Stop the monitoring system
  --report             Generate monitoring report
  --cleanup            Cleanup old monitoring data
  --stats              Show current statistics
  --help, -h           Show this help message

Examples:
  node scripts/monitoring-system.js --start           # Start monitoring
  node scripts/monitoring-system.js --report          # Generate report
  node scripts/monitoring-system.js --cleanup         # Cleanup old data
`, 'cyan');
}

// Main execution
if (require.main === module) {
    const options = parseArguments();
    
    const monitoring = new MonitoringSystem();
    
    if (options.start) {
        monitoring.init().then(() => {
            logSuccess('Monitoring system started');
        }).catch(error => {
            logError(`Failed to start monitoring: ${error.message}`);
            process.exit(1);
        });
    } else if (options.stop) {
        monitoring.stopMetricsCollection();
        logSuccess('Monitoring system stopped');
    } else if (options.report) {
        const report = monitoring.generateReport();
        logInfo('Monitoring report generated');
        console.log(JSON.stringify(report, null, 2));
    } else if (options.cleanup) {
        monitoring.cleanupOldData();
    } else if (options.stats) {
        const stats = monitoring.getStats();
        logInfo('Current monitoring statistics:');
        console.log(JSON.stringify(stats, null, 2));
    } else {
        showHelp();
    }
}

module.exports = {
    MonitoringSystem,
    config
}; 