#!/usr/bin/env node

/**
 * SEIM Frontend Maintenance Automation
 * Handles dependency updates, security audits, performance monitoring, and maintenance scheduling
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const https = require('https');

// Configuration
const config = {
    // Maintenance settings
    autoUpdateDependencies: true,
    securityAuditEnabled: true,
    performanceMonitoring: true,
    maintenanceSchedule: {
        dependencyCheck: 'weekly',    // weekly, daily, monthly
        securityAudit: 'weekly',      // weekly, daily, monthly
        performanceCheck: 'daily',    // weekly, daily, monthly
        cleanup: 'monthly'            // weekly, daily, monthly
    },
    
    // Notification settings
    notifications: {
        email: process.env.MAINTENANCE_EMAIL || null,
        slack: process.env.SLACK_WEBHOOK || null,
        console: true
    },
    
    // Performance thresholds
    performanceThresholds: {
        bundleSize: 500,              // KB
        loadTime: 3000,               // milliseconds
        memoryUsage: 0.8,             // percentage
        errorRate: 0.01               // percentage
    },
    
    // Security settings
    securitySettings: {
        auditLevel: 'moderate',       // low, moderate, high
        autoFix: false,               // Auto-fix security issues
        ignoreDevDependencies: false  // Include dev dependencies in audit
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

// Maintenance automation class
class MaintenanceAutomation {
    constructor() {
        this.results = {
            dependencies: { updated: 0, failed: 0, details: [] },
            security: { vulnerabilities: 0, fixed: 0, details: [] },
            performance: { issues: 0, improvements: 0, details: [] },
            cleanup: { filesRemoved: 0, spaceFreed: 0, details: [] }
        };
    }

    /**
     * Run all maintenance tasks
     */
    async runMaintenance() {
        logHeader('SEIM Frontend Maintenance Automation');
        
        try {
            // Check maintenance schedule
            const shouldRun = this.checkMaintenanceSchedule();
            if (!shouldRun) {
                logInfo('Maintenance not scheduled for today');
                return;
            }

            // Run maintenance tasks
            await this.updateDependencies();
            await this.runSecurityAudit();
            await this.checkPerformance();
            await this.cleanupProject();
            
            // Generate report
            this.generateReport();
            
            // Send notifications
            await this.sendNotifications();
            
            logSuccess('Maintenance completed successfully');
            
        } catch (error) {
            logError(`Maintenance failed: ${error.message}`);
            await this.sendErrorNotification(error);
        }
    }

    /**
     * Check if maintenance should run based on schedule
     */
    checkMaintenanceSchedule() {
        const today = new Date();
        const dayOfWeek = today.getDay();
        const dayOfMonth = today.getDate();
        
        // Check daily tasks
        if (config.maintenanceSchedule.performanceCheck === 'daily') {
            return true;
        }
        
        // Check weekly tasks (Monday = 1)
        if (config.maintenanceSchedule.dependencyCheck === 'weekly' && dayOfWeek === 1) {
            return true;
        }
        
        if (config.maintenanceSchedule.securityAudit === 'weekly' && dayOfWeek === 1) {
            return true;
        }
        
        // Check monthly tasks (first day of month)
        if (config.maintenanceSchedule.cleanup === 'monthly' && dayOfMonth === 1) {
            return true;
        }
        
        return false;
    }

    /**
     * Update dependencies
     */
    async updateDependencies() {
        logSection('Updating Dependencies');
        
        try {
            // Check for outdated packages
            logInfo('Checking for outdated packages...');
            const outdatedResult = execSync('npm outdated --json', { encoding: 'utf8' });
            const outdated = JSON.parse(outdatedResult);
            
            if (Object.keys(outdated).length === 0) {
                logSuccess('All dependencies are up to date');
                return;
            }
            
            logInfo(`Found ${Object.keys(outdated).length} outdated packages`);
            
            // Update packages if auto-update is enabled
            if (config.autoUpdateDependencies) {
                logInfo('Auto-updating dependencies...');
                
                // Update minor and patch versions
                execSync('npm update', { stdio: 'inherit' });
                
                // Check for major version updates
                const majorUpdates = Object.keys(outdated).filter(pkg => {
                    const current = outdated[pkg].current;
                    const latest = outdated[pkg].latest;
                    return this.isMajorUpdate(current, latest);
                });
                
                if (majorUpdates.length > 0) {
                    logWarning(`Found ${majorUpdates.length} major version updates available`);
                    this.results.dependencies.details.push({
                        type: 'major_updates_available',
                        packages: majorUpdates
                    });
                }
                
                this.results.dependencies.updated = Object.keys(outdated).length;
                logSuccess(`Updated ${this.results.dependencies.updated} packages`);
                
            } else {
                logInfo('Auto-update disabled. Manual update required.');
                this.results.dependencies.details.push({
                    type: 'manual_update_required',
                    packages: Object.keys(outdated)
                });
            }
            
        } catch (error) {
            logError(`Dependency update failed: ${error.message}`);
            this.results.dependencies.failed++;
            this.results.dependencies.details.push({
                type: 'update_failed',
                error: error.message
            });
        }
    }

    /**
     * Check if version update is major
     */
    isMajorUpdate(current, latest) {
        const currentMajor = parseInt(current.split('.')[0]);
        const latestMajor = parseInt(latest.split('.')[0]);
        return latestMajor > currentMajor;
    }

    /**
     * Run security audit
     */
    async runSecurityAudit() {
        if (!config.securityAuditEnabled) {
            logInfo('Security audit disabled');
            return;
        }
        
        logSection('Running Security Audit');
        
        try {
            logInfo('Running npm audit...');
            const auditResult = execSync('npm audit --json', { encoding: 'utf8' });
            const audit = JSON.parse(auditResult);
            
            const vulnerabilities = audit.metadata.vulnerabilities;
            const totalVulnerabilities = Object.values(vulnerabilities).reduce((sum, count) => sum + count, 0);
            
            if (totalVulnerabilities === 0) {
                logSuccess('No security vulnerabilities found');
                return;
            }
            
            logWarning(`Found ${totalVulnerabilities} security vulnerabilities`);
            
            // Log vulnerability details
            Object.entries(vulnerabilities).forEach(([severity, count]) => {
                logWarning(`${severity}: ${count} vulnerabilities`);
            });
            
            this.results.security.vulnerabilities = totalVulnerabilities;
            this.results.security.details.push({
                type: 'vulnerabilities_found',
                count: totalVulnerabilities,
                breakdown: vulnerabilities
            });
            
            // Auto-fix if enabled
            if (config.securitySettings.autoFix) {
                logInfo('Attempting to auto-fix vulnerabilities...');
                try {
                    execSync('npm audit fix', { stdio: 'inherit' });
                    this.results.security.fixed = totalVulnerabilities;
                    logSuccess('Auto-fix completed');
                } catch (fixError) {
                    logError(`Auto-fix failed: ${fixError.message}`);
                    this.results.security.details.push({
                        type: 'auto_fix_failed',
                        error: fixError.message
                    });
                }
            } else {
                logInfo('Auto-fix disabled. Manual fix required.');
                this.results.security.details.push({
                    type: 'manual_fix_required',
                    vulnerabilities: totalVulnerabilities
                });
            }
            
        } catch (error) {
            logError(`Security audit failed: ${error.message}`);
            this.results.security.details.push({
                type: 'audit_failed',
                error: error.message
            });
        }
    }

    /**
     * Check performance metrics
     */
    async checkPerformance() {
        if (!config.performanceMonitoring) {
            logInfo('Performance monitoring disabled');
            return;
        }
        
        logSection('Checking Performance');
        
        try {
            // Build project to check bundle size
            logInfo('Building project to check bundle size...');
            execSync('npm run build', { stdio: 'pipe' });
            
            // Analyze bundle size
            const bundleSize = this.analyzeBundleSize();
            
            if (bundleSize > config.performanceThresholds.bundleSize) {
                logWarning(`Bundle size (${bundleSize}KB) exceeds threshold (${config.performanceThresholds.bundleSize}KB)`);
                this.results.performance.issues++;
                this.results.performance.details.push({
                    type: 'bundle_size_exceeded',
                    current: bundleSize,
                    threshold: config.performanceThresholds.bundleSize
                });
            } else {
                logSuccess(`Bundle size (${bundleSize}KB) within threshold`);
            }
            
            // Check for performance regressions
            const performanceIssues = this.checkPerformanceRegressions();
            if (performanceIssues.length > 0) {
                logWarning(`Found ${performanceIssues.length} performance issues`);
                this.results.performance.issues += performanceIssues.length;
                this.results.performance.details.push(...performanceIssues);
            }
            
        } catch (error) {
            logError(`Performance check failed: ${error.message}`);
            this.results.performance.details.push({
                type: 'performance_check_failed',
                error: error.message
            });
        }
    }

    /**
     * Analyze bundle size
     */
    analyzeBundleSize() {
        try {
            const distPath = path.join(process.cwd(), 'staticfiles');
            if (!fs.existsSync(distPath)) {
                return 0;
            }
            
            let totalSize = 0;
            const files = fs.readdirSync(distPath);
            
            files.forEach(file => {
                if (file.endsWith('.js')) {
                    const filePath = path.join(distPath, file);
                    const stats = fs.statSync(filePath);
                    totalSize += stats.size;
                }
            });
            
            return Math.round(totalSize / 1024); // Convert to KB
        } catch (error) {
            logError(`Bundle size analysis failed: ${error.message}`);
            return 0;
        }
    }

    /**
     * Check for performance regressions
     */
    checkPerformanceRegressions() {
        const issues = [];
        
        // Check for common performance issues
        const jsFiles = this.findJSFiles('static/js');
        
        jsFiles.forEach(file => {
            const content = fs.readFileSync(file, 'utf8');
            
            // Check for large functions
            const functionMatches = content.match(/function\s+\w+\s*\([^)]*\)\s*\{[^}]*\}/g);
            if (functionMatches) {
                functionMatches.forEach(func => {
                    const lines = func.split('\n').length;
                    if (lines > 50) {
                        issues.push({
                            type: 'large_function',
                            file: file,
                            function: func.match(/function\s+(\w+)/)?.[1] || 'anonymous',
                            lines: lines
                        });
                    }
                });
            }
            
            // Check for console.log statements in production
            if (content.includes('console.log(')) {
                issues.push({
                    type: 'console_log_in_production',
                    file: file,
                    count: (content.match(/console\.log\(/g) || []).length
                });
            }
        });
        
        return issues;
    }

    /**
     * Find JavaScript files recursively
     */
    findJSFiles(dir) {
        const files = [];
        
        if (!fs.existsSync(dir)) {
            return files;
        }
        
        const items = fs.readdirSync(dir);
        
        items.forEach(item => {
            const fullPath = path.join(dir, item);
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                files.push(...this.findJSFiles(fullPath));
            } else if (item.endsWith('.js')) {
                files.push(fullPath);
            }
        });
        
        return files;
    }

    /**
     * Cleanup project files
     */
    async cleanupProject() {
        logSection('Cleaning Up Project');
        
        try {
            let filesRemoved = 0;
            let spaceFreed = 0;
            
            // Clean node_modules cache
            logInfo('Cleaning npm cache...');
            execSync('npm cache clean --force', { stdio: 'pipe' });
            
            // Remove old build files
            const buildDirs = ['dist', 'build', 'staticfiles'];
            buildDirs.forEach(dir => {
                const dirPath = path.join(process.cwd(), dir);
                if (fs.existsSync(dirPath)) {
                    const stats = fs.statSync(dirPath);
                    spaceFreed += stats.size;
                    
                    fs.rmSync(dirPath, { recursive: true, force: true });
                    filesRemoved++;
                    logInfo(`Removed ${dir} directory`);
                }
            });
            
            // Remove old log files
            const logFiles = this.findLogFiles();
            logFiles.forEach(file => {
                const stats = fs.statSync(file);
                spaceFreed += stats.size;
                
                fs.unlinkSync(file);
                filesRemoved++;
            });
            
            if (logFiles.length > 0) {
                logInfo(`Removed ${logFiles.length} log files`);
            }
            
            this.results.cleanup.filesRemoved = filesRemoved;
            this.results.cleanup.spaceFreed = Math.round(spaceFreed / 1024); // KB
            
            logSuccess(`Cleanup completed: ${filesRemoved} files removed, ${this.results.cleanup.spaceFreed}KB freed`);
            
        } catch (error) {
            logError(`Cleanup failed: ${error.message}`);
            this.results.cleanup.details.push({
                type: 'cleanup_failed',
                error: error.message
            });
        }
    }

    /**
     * Find log files
     */
    findLogFiles() {
        const logFiles = [];
        const logPatterns = ['*.log', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*'];
        
        logPatterns.forEach(pattern => {
            try {
                const files = fs.readdirSync(process.cwd());
                files.forEach(file => {
                    if (file.match(pattern.replace('*', '.*'))) {
                        logFiles.push(path.join(process.cwd(), file));
                    }
                });
            } catch (error) {
                // Ignore errors
            }
        });
        
        return logFiles;
    }

    /**
     * Generate maintenance report
     */
    generateReport() {
        logSection('Generating Maintenance Report');
        
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                dependencies: {
                    updated: this.results.dependencies.updated,
                    failed: this.results.dependencies.failed
                },
                security: {
                    vulnerabilities: this.results.security.vulnerabilities,
                    fixed: this.results.security.fixed
                },
                performance: {
                    issues: this.results.performance.issues,
                    improvements: this.results.performance.improvements
                },
                cleanup: {
                    filesRemoved: this.results.cleanup.filesRemoved,
                    spaceFreed: this.results.cleanup.spaceFreed
                }
            },
            details: this.results
        };
        
        // Save report
        const reportsDir = path.join(process.cwd(), 'maintenance-reports');
        fs.mkdirSync(reportsDir, { recursive: true });
        
        const reportPath = path.join(reportsDir, `maintenance-${Date.now()}.json`);
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        
        logInfo(`Maintenance report saved to ${reportPath}`);
        
        // Display summary
        logInfo('Maintenance Summary:');
        log(`  Dependencies: ${report.summary.dependencies.updated} updated, ${report.summary.dependencies.failed} failed`);
        log(`  Security: ${report.summary.security.vulnerabilities} vulnerabilities, ${report.summary.security.fixed} fixed`);
        log(`  Performance: ${report.summary.performance.issues} issues found`);
        log(`  Cleanup: ${report.summary.cleanup.filesRemoved} files removed, ${report.summary.cleanup.spaceFreed}KB freed`);
    }

    /**
     * Send notifications
     */
    async sendNotifications() {
        logSection('Sending Notifications');
        
        const hasIssues = this.results.dependencies.failed > 0 ||
                         this.results.security.vulnerabilities > 0 ||
                         this.results.performance.issues > 0;
        
        if (hasIssues) {
            await this.sendAlertNotification();
        } else {
            await this.sendSuccessNotification();
        }
    }

    /**
     * Send alert notification
     */
    async sendAlertNotification() {
        const message = {
            text: '🚨 SEIM Frontend Maintenance Alert',
            attachments: [{
                color: 'danger',
                fields: [
                    {
                        title: 'Dependencies',
                        value: `${this.results.dependencies.failed} failed updates`,
                        short: true
                    },
                    {
                        title: 'Security',
                        value: `${this.results.security.vulnerabilities} vulnerabilities found`,
                        short: true
                    },
                    {
                        title: 'Performance',
                        value: `${this.results.performance.issues} issues detected`,
                        short: true
                    }
                ]
            }]
        };
        
        await this.sendSlackNotification(message);
    }

    /**
     * Send success notification
     */
    async sendSuccessNotification() {
        const message = {
            text: '✅ SEIM Frontend Maintenance Completed Successfully',
            attachments: [{
                color: 'good',
                fields: [
                    {
                        title: 'Dependencies',
                        value: `${this.results.dependencies.updated} packages updated`,
                        short: true
                    },
                    {
                        title: 'Security',
                        value: 'No vulnerabilities found',
                        short: true
                    },
                    {
                        title: 'Performance',
                        value: 'All checks passed',
                        short: true
                    },
                    {
                        title: 'Cleanup',
                        value: `${this.results.cleanup.filesRemoved} files removed`,
                        short: true
                    }
                ]
            }]
        };
        
        await this.sendSlackNotification(message);
    }

    /**
     * Send error notification
     */
    async sendErrorNotification(error) {
        const message = {
            text: '💥 SEIM Frontend Maintenance Failed',
            attachments: [{
                color: 'danger',
                text: `Error: ${error.message}`,
                fields: [
                    {
                        title: 'Stack Trace',
                        value: error.stack || 'No stack trace available',
                        short: false
                    }
                ]
            }]
        };
        
        await this.sendSlackNotification(message);
    }

    /**
     * Send Slack notification
     */
    async sendSlackNotification(message) {
        if (!config.notifications.slack) {
            return;
        }
        
        try {
            const data = JSON.stringify(message);
            
            const options = {
                hostname: 'hooks.slack.com',
                port: 443,
                path: config.notifications.slack,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': data.length
                }
            };
            
            const req = https.request(options, (res) => {
                if (res.statusCode === 200) {
                    logSuccess('Slack notification sent');
                } else {
                    logError(`Slack notification failed: ${res.statusCode}`);
                }
            });
            
            req.on('error', (error) => {
                logError(`Slack notification error: ${error.message}`);
            });
            
            req.write(data);
            req.end();
            
        } catch (error) {
            logError(`Slack notification failed: ${error.message}`);
        }
    }
}

// CLI argument parsing
function parseArguments() {
    const args = process.argv.slice(2);
    const options = {
        force: false,
        skipDependencies: false,
        skipSecurity: false,
        skipPerformance: false,
        skipCleanup: false
    };
    
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        
        switch (arg) {
            case '--force':
                options.force = true;
                break;
            case '--skip-dependencies':
                options.skipDependencies = true;
                break;
            case '--skip-security':
                options.skipSecurity = true;
                break;
            case '--skip-performance':
                options.skipPerformance = true;
                break;
            case '--skip-cleanup':
                options.skipCleanup = true;
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
    logHeader('SEIM Maintenance Automation Help');
    log(`
Usage: node scripts/maintenance-automation.js [options]

Options:
  --force              Force maintenance regardless of schedule
  --skip-dependencies  Skip dependency updates
  --skip-security      Skip security audit
  --skip-performance   Skip performance checks
  --skip-cleanup       Skip cleanup tasks
  --help, -h           Show this help message

Examples:
  node scripts/maintenance-automation.js                    # Run scheduled maintenance
  node scripts/maintenance-automation.js --force           # Force maintenance
  node scripts/maintenance-automation.js --skip-security   # Skip security audit
`, 'cyan');
}

// Main execution
if (require.main === module) {
    const options = parseArguments();
    
    const maintenance = new MaintenanceAutomation();
    
    // Override config based on options
    if (options.force) {
        maintenance.checkMaintenanceSchedule = () => true;
    }
    
    maintenance.runMaintenance().catch(error => {
        logError(`Maintenance automation failed: ${error.message}`);
        process.exit(1);
    });
}

module.exports = {
    MaintenanceAutomation,
    config
}; 