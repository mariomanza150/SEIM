#!/usr/bin/env node

/**
 * SEIM Frontend Test Runner
 * Comprehensive test execution and reporting script
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const config = {
    testTypes: ['unit', 'integration', 'e2e'],
    coverageThreshold: {
        statements: 70,
        branches: 70,
        functions: 70,
        lines: 70
    },
    outputDir: 'coverage/frontend',
    reportsDir: 'test-reports'
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

// Test execution functions
function runCommand(command, args = [], options = {}) {
    return new Promise((resolve, reject) => {
        const child = spawn(command, args, {
            stdio: 'inherit',
            shell: true,
            ...options
        });

        child.on('close', (code) => {
            if (code === 0) {
                resolve(code);
            } else {
                reject(new Error(`Command failed with exit code ${code}`));
            }
        });

        child.on('error', (error) => {
            reject(error);
        });
    });
}

function runJestTests(testType = 'all', options = {}) {
    const args = [
        '--config', 'jest.config.frontend.js',
        '--verbose',
        '--detectOpenHandles'
    ];

    if (testType !== 'all') {
        args.push('--testPathPattern', `tests/frontend/${testType}`);
    }

    if (options.coverage) {
        args.push('--coverage');
    }

    if (options.watch) {
        args.push('--watch');
    }

    if (options.ci) {
        args.push('--ci', '--watchAll=false');
    }

    return runCommand('npx', ['jest', ...args]);
}

// Coverage analysis
function analyzeCoverage() {
    try {
        const coveragePath = path.join(config.outputDir, 'coverage-summary.json');
        
        if (!fs.existsSync(coveragePath)) {
            logWarning('Coverage report not found');
            return false;
        }

        const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
        const total = coverage.total;

        logSection('Coverage Analysis');
        
        const metrics = ['statements', 'branches', 'functions', 'lines'];
        let allPassed = true;

        metrics.forEach(metric => {
            const percentage = total[metric].pct;
            const threshold = config.coverageThreshold[metric];
            const status = percentage >= threshold ? 'PASS' : 'FAIL';
            const color = percentage >= threshold ? 'green' : 'red';
            
            log(`${metric.toUpperCase()}: ${percentage}% (threshold: ${threshold}%)`, color);
            
            if (percentage < threshold) {
                allPassed = false;
            }
        });

        return allPassed;
    } catch (error) {
        logError(`Coverage analysis failed: ${error.message}`);
        return false;
    }
}

// Test report generation
function generateTestReport(results) {
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            total: 0,
            passed: 0,
            failed: 0,
            skipped: 0
        },
        testTypes: {},
        coverage: null,
        duration: 0
    };

    // Aggregate results
    Object.keys(results).forEach(testType => {
        const result = results[testType];
        report.testTypes[testType] = result;
        
        report.summary.total += result.total || 0;
        report.summary.passed += result.passed || 0;
        report.summary.failed += result.failed || 0;
        report.summary.skipped += result.skipped || 0;
    });

    // Add coverage if available
    try {
        const coveragePath = path.join(config.outputDir, 'coverage-summary.json');
        if (fs.existsSync(coveragePath)) {
            report.coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
        }
    } catch (error) {
        logWarning('Could not read coverage data');
    }

    // Save report
    const reportPath = path.join(config.reportsDir, `test-report-${Date.now()}.json`);
    fs.mkdirSync(config.reportsDir, { recursive: true });
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    logSuccess(`Test report saved to ${reportPath}`);
    return report;
}

// Main test runner
async function runTests(options = {}) {
    const startTime = Date.now();
    const results = {};
    
    logHeader('SEIM Frontend Test Suite');
    
    try {
        // Run different test types
        for (const testType of config.testTypes) {
            if (options.testType && options.testType !== testType && options.testType !== 'all') {
                continue;
            }

            logSection(`Running ${testType.toUpperCase()} Tests`);
            
            try {
                await runJestTests(testType, {
                    coverage: options.coverage,
                    watch: options.watch,
                    ci: options.ci
                });
                
                results[testType] = { status: 'passed' };
                logSuccess(`${testType} tests passed`);
                
            } catch (error) {
                results[testType] = { 
                    status: 'failed', 
                    error: error.message 
                };
                logError(`${testType} tests failed: ${error.message}`);
                
                if (options.failFast) {
                    throw error;
                }
            }
        }

        // Analyze coverage if requested
        if (options.coverage) {
            logSection('Coverage Analysis');
            const coveragePassed = analyzeCoverage();
            
            if (!coveragePassed && options.strict) {
                throw new Error('Coverage thresholds not met');
            }
        }

        // Generate test report
        if (options.report) {
            const report = generateTestReport(results);
            logSection('Test Summary');
            log(`Total Tests: ${report.summary.total}`);
            log(`Passed: ${report.summary.passed}`, 'green');
            log(`Failed: ${report.summary.failed}`, 'red');
            log(`Skipped: ${report.summary.skipped}`, 'yellow');
        }

        const duration = Date.now() - startTime;
        logSuccess(`All tests completed in ${duration}ms`);

    } catch (error) {
        logError(`Test suite failed: ${error.message}`);
        process.exit(1);
    }
}

// CLI argument parsing
function parseArguments() {
    const args = process.argv.slice(2);
    const options = {
        testType: 'all',
        coverage: false,
        watch: false,
        ci: false,
        strict: false,
        failFast: false,
        report: true
    };

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        
        switch (arg) {
            case '--unit':
                options.testType = 'unit';
                break;
            case '--integration':
                options.testType = 'integration';
                break;
            case '--e2e':
                options.testType = 'e2e';
                break;
            case '--coverage':
                options.coverage = true;
                break;
            case '--watch':
                options.watch = true;
                break;
            case '--ci':
                options.ci = true;
                break;
            case '--strict':
                options.strict = true;
                break;
            case '--fail-fast':
                options.failFast = true;
                break;
            case '--no-report':
                options.report = false;
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
    logHeader('SEIM Frontend Test Runner Help');
    log(`
Usage: node scripts/run-frontend-tests.js [options]

Options:
  --unit              Run only unit tests
  --integration       Run only integration tests
  --e2e               Run only end-to-end tests
  --coverage          Generate coverage report
  --watch             Run tests in watch mode
  --ci                Run tests in CI mode
  --strict            Fail if coverage thresholds not met
  --fail-fast         Stop on first failure
  --no-report         Skip test report generation
  --help, -h          Show this help message

Examples:
  node scripts/run-frontend-tests.js                    # Run all tests
  node scripts/run-frontend-tests.js --unit --coverage  # Run unit tests with coverage
  node scripts/run-frontend-tests.js --e2e --watch      # Run E2E tests in watch mode
  node scripts/run-frontend-tests.js --ci --strict      # Run CI tests with strict coverage
`, 'cyan');
}

// Main execution
if (require.main === module) {
    const options = parseArguments();
    runTests(options).catch(error => {
        logError(`Test runner failed: ${error.message}`);
        process.exit(1);
    });
}

module.exports = {
    runTests,
    analyzeCoverage,
    generateTestReport
}; 