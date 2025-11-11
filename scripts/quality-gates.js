#!/usr/bin/env node

/**
 * SEIM Quality Gates
 * Enforces code quality standards for CI/CD pipelines
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Quality gate thresholds
const QUALITY_GATES = {
    coverage: {
        statements: 70,
        branches: 70,
        functions: 70,
        lines: 70
    },
    linting: {
        maxErrors: 0,
        maxWarnings: 10
    },
    complexity: {
        maxComplexity: 10,
        maxLines: 300,
        maxLinesPerFunction: 50,
        maxParams: 5,
        maxDepth: 4
    },
    overallScore: 80
};

// Colors for console output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
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

// Quality gate checks
class QualityGates {
    constructor() {
        this.results = {
            coverage: { passed: false, details: {} },
            linting: { passed: false, details: {} },
            complexity: { passed: false, details: {} },
            overall: { passed: false, score: 0 }
        };
    }

    /**
     * Check test coverage
     */
    checkCoverage() {
        logSection('Checking Test Coverage');
        
        try {
            const coveragePath = path.join('coverage', 'frontend', 'coverage-summary.json');
            
            if (!fs.existsSync(coveragePath)) {
                logError('Coverage report not found. Run tests with coverage first.');
                this.results.coverage.passed = false;
                this.results.coverage.details.error = 'Coverage report not found';
                return false;
            }
            
            const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
            const total = coverage.total;
            
            let allPassed = true;
            const details = {};
            
            Object.keys(QUALITY_GATES.coverage).forEach(metric => {
                const percentage = total[metric].pct;
                const threshold = QUALITY_GATES.coverage[metric];
                const passed = percentage >= threshold;
                
                details[metric] = {
                    percentage,
                    threshold,
                    passed
                };
                
                if (passed) {
                    logSuccess(`${metric}: ${percentage}% (threshold: ${threshold}%)`);
                } else {
                    logError(`${metric}: ${percentage}% (threshold: ${threshold}%)`);
                    allPassed = false;
                }
            });
            
            this.results.coverage.passed = allPassed;
            this.results.coverage.details = details;
            
            return allPassed;
            
        } catch (error) {
            logError(`Coverage check failed: ${error.message}`);
            this.results.coverage.passed = false;
            this.results.coverage.details.error = error.message;
            return false;
        }
    }

    /**
     * Check linting
     */
    checkLinting() {
        logSection('Checking Code Linting');
        
        try {
            logInfo('Running ESLint...');
            const result = execSync('npx eslint static/js --format=json', { encoding: 'utf8' });
            const lintResults = JSON.parse(result);
            
            let totalErrors = 0;
            let totalWarnings = 0;
            const details = {
                files: lintResults.length,
                filesWithIssues: 0,
                errors: [],
                warnings: []
            };
            
            lintResults.forEach(file => {
                const fileIssues = file.messages.length;
                if (fileIssues > 0) {
                    details.filesWithIssues++;
                    
                    file.messages.forEach(message => {
                        const issue = {
                            file: file.filePath,
                            line: message.line,
                            column: message.column,
                            rule: message.ruleId,
                            message: message.message
                        };
                        
                        if (message.severity === 2) {
                            totalErrors++;
                            details.errors.push(issue);
                        } else {
                            totalWarnings++;
                            details.warnings.push(issue);
                        }
                    });
                }
            });
            
            const errorsPassed = totalErrors <= QUALITY_GATES.linting.maxErrors;
            const warningsPassed = totalWarnings <= QUALITY_GATES.linting.maxWarnings;
            const allPassed = errorsPassed && warningsPassed;
            
            details.totalErrors = totalErrors;
            details.totalWarnings = totalWarnings;
            details.errorsPassed = errorsPassed;
            details.warningsPassed = warningsPassed;
            
            if (errorsPassed) {
                logSuccess(`Errors: ${totalErrors} (max: ${QUALITY_GATES.linting.maxErrors})`);
            } else {
                logError(`Errors: ${totalErrors} (max: ${QUALITY_GATES.linting.maxErrors})`);
            }
            
            if (warningsPassed) {
                logSuccess(`Warnings: ${totalWarnings} (max: ${QUALITY_GATES.linting.maxWarnings})`);
            } else {
                logWarning(`Warnings: ${totalWarnings} (max: ${QUALITY_GATES.linting.maxWarnings})`);
            }
            
            this.results.linting.passed = allPassed;
            this.results.linting.details = details;
            
            return allPassed;
            
        } catch (error) {
            logError(`Linting check failed: ${error.message}`);
            this.results.linting.passed = false;
            this.results.linting.details.error = error.message;
            return false;
        }
    }

    /**
     * Check code complexity
     */
    checkComplexity() {
        logSection('Checking Code Complexity');
        
        try {
            // Run complexity analysis using the quality analyzer
            const result = execSync('node scripts/code-quality-analyzer.js --no-report', { encoding: 'utf8' });
            
            // Parse the output to extract complexity metrics
            const lines = result.split('\n');
            let complexityIssues = 0;
            let fileIssues = 0;
            
            lines.forEach(line => {
                if (line.includes('high-complexity') || line.includes('deep-nesting') || 
                    line.includes('too-many-params') || line.includes('file-too-long')) {
                    complexityIssues++;
                }
                if (line.includes('Files with issues:')) {
                    const match = line.match(/(\d+)/);
                    if (match) {
                        fileIssues = parseInt(match[1]);
                    }
                }
            });
            
            const passed = complexityIssues === 0;
            
            if (passed) {
                logSuccess('No complexity issues found');
            } else {
                logError(`${complexityIssues} complexity issues found in ${fileIssues} files`);
            }
            
            this.results.complexity.passed = passed;
            this.results.complexity.details = {
                complexityIssues,
                fileIssues
            };
            
            return passed;
            
        } catch (error) {
            logError(`Complexity check failed: ${error.message}`);
            this.results.complexity.passed = false;
            this.results.complexity.details.error = error.message;
            return false;
        }
    }

    /**
     * Calculate overall quality score
     */
    calculateOverallScore() {
        logSection('Calculating Overall Quality Score');
        
        let score = 0;
        let totalChecks = 0;
        
        // Coverage score (40% weight)
        if (this.results.coverage.passed) {
            score += 40;
        } else if (this.results.coverage.details.error) {
            score += 0;
        } else {
            // Partial score based on coverage
            const coverageDetails = this.results.coverage.details;
            const metrics = Object.keys(coverageDetails).filter(key => coverageDetails[key].passed);
            score += (metrics.length / 4) * 40;
        }
        totalChecks++;
        
        // Linting score (35% weight)
        if (this.results.linting.passed) {
            score += 35;
        } else if (this.results.linting.details.error) {
            score += 0;
        } else {
            // Partial score based on errors vs warnings
            const details = this.results.linting.details;
            if (details.errorsPassed) {
                score += 25; // Most weight for no errors
            }
            if (details.warningsPassed) {
                score += 10; // Some weight for warnings
            }
        }
        totalChecks++;
        
        // Complexity score (25% weight)
        if (this.results.complexity.passed) {
            score += 25;
        } else if (this.results.complexity.details.error) {
            score += 0;
        } else {
            // Partial score based on complexity issues
            const details = this.results.complexity.details;
            if (details.complexityIssues === 0) {
                score += 25;
            } else {
                score += Math.max(0, 25 - (details.complexityIssues * 5));
            }
        }
        totalChecks++;
        
        const overallScore = Math.round(score);
        const passed = overallScore >= QUALITY_GATES.overallScore;
        
        logInfo(`Overall Quality Score: ${overallScore}/100`);
        logInfo(`Quality Gate Threshold: ${QUALITY_GATES.overallScore}/100`);
        
        if (passed) {
            logSuccess('Overall quality gate PASSED');
        } else {
            logError('Overall quality gate FAILED');
        }
        
        this.results.overall.score = overallScore;
        this.results.overall.passed = passed;
        
        return passed;
    }

    /**
     * Run all quality gates
     */
    async runAllGates() {
        logHeader('SEIM Quality Gates');
        
        const coveragePassed = this.checkCoverage();
        const lintingPassed = this.checkLinting();
        const complexityPassed = this.checkComplexity();
        const overallPassed = this.calculateOverallScore();
        
        // Generate summary
        logSection('Quality Gates Summary');
        
        log(`Coverage: ${coveragePassed ? 'PASS' : 'FAIL'}`);
        log(`Linting: ${lintingPassed ? 'PASS' : 'FAIL'}`);
        log(`Complexity: ${complexityPassed ? 'PASS' : 'FAIL'}`);
        log(`Overall: ${overallPassed ? 'PASS' : 'FAIL'} (${this.results.overall.score}/100)`);
        
        // Save results
        const resultsPath = path.join('quality-reports', `quality-gates-${Date.now()}.json`);
        fs.mkdirSync('quality-reports', { recursive: true });
        fs.writeFileSync(resultsPath, JSON.stringify(this.results, null, 2));
        
        logInfo(`Quality gates report saved to ${resultsPath}`);
        
        return overallPassed;
    }

    /**
     * Get detailed results
     */
    getResults() {
        return this.results;
    }
}

// CLI argument parsing
function parseArguments() {
    const args = process.argv.slice(2);
    const options = {
        detailed: false,
        saveReport: true,
        failOnFailure: true
    };
    
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        
        switch (arg) {
            case '--detailed':
                options.detailed = true;
                break;
            case '--no-report':
                options.saveReport = false;
                break;
            case '--no-fail':
                options.failOnFailure = false;
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
    logHeader('SEIM Quality Gates Help');
    log(`
Usage: node scripts/quality-gates.js [options]

Options:
  --detailed         Show detailed analysis for each gate
  --no-report        Skip saving the quality gates report
  --no-fail          Don't exit with error code on failure
  --help, -h         Show this help message

Examples:
  node scripts/quality-gates.js                    # Run all gates
  node scripts/quality-gates.js --detailed        # Show detailed results
  node scripts/quality-gates.js --no-fail         # Don't fail on gate failure
`, 'cyan');
}

// Main execution
if (require.main === module) {
    const options = parseArguments();
    
    const qualityGates = new QualityGates();
    
    qualityGates.runAllGates().then(passed => {
        if (options.failOnFailure && !passed) {
            logError('Quality gates failed. Exiting with error code.');
            process.exit(1);
        }
    }).catch(error => {
        logError(`Quality gates failed: ${error.message}`);
        if (options.failOnFailure) {
            process.exit(1);
        }
    });
}

module.exports = {
    QualityGates,
    QUALITY_GATES
}; 