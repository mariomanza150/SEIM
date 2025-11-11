#!/usr/bin/env node

/**
 * SEIM Code Quality Analyzer
 * Comprehensive code quality analysis and reporting
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const config = {
    sourceDir: 'static/js',
    testDir: 'tests/frontend',
    coverageDir: 'coverage/frontend',
    reportsDir: 'quality-reports',
    thresholds: {
        complexity: 10,
        maxLines: 300,
        maxLinesPerFunction: 50,
        maxParams: 5,
        maxDepth: 4,
        coverage: {
            statements: 70,
            branches: 70,
            functions: 70,
            lines: 70
        }
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

// File analysis functions
function analyzeFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    
    const analysis = {
        file: filePath,
        lines: lines.length,
        functions: 0,
        complexity: 0,
        maxComplexity: 0,
        maxDepth: 0,
        maxParams: 0,
        issues: []
    };
    
    // Analyze each line
    lines.forEach((line, index) => {
        const lineNum = index + 1;
        const trimmedLine = line.trim();
        
        // Count functions
        if (trimmedLine.match(/^(function|const|let|var)\s+\w+\s*=\s*(async\s+)?\(/)) {
            analysis.functions++;
        }
        
        // Check complexity indicators
        const complexityIndicators = [
            'if', 'else', 'for', 'while', 'do', 'switch', 'case',
            'catch', '&&', '||', '?', ':', '?.', '??'
        ];
        
        complexityIndicators.forEach(indicator => {
            if (trimmedLine.includes(indicator)) {
                analysis.complexity++;
            }
        });
        
        // Check nesting depth
        const depth = (line.match(/^\s*/)[0].length / 4) + 1;
        if (depth > analysis.maxDepth) {
            analysis.maxDepth = depth;
        }
        
        // Check function parameters
        const paramMatch = trimmedLine.match(/\(([^)]*)\)/);
        if (paramMatch) {
            const params = paramMatch[1].split(',').filter(p => p.trim());
            if (params.length > analysis.maxParams) {
                analysis.maxParams = params.length;
            }
        }
        
        // Check for issues
        if (trimmedLine.length > config.thresholds.maxLines) {
            analysis.issues.push({
                line: lineNum,
                type: 'long-line',
                message: `Line ${lineNum} exceeds ${config.thresholds.maxLines} characters`
            });
        }
        
        if (trimmedLine.includes('TODO') || trimmedLine.includes('FIXME')) {
            analysis.issues.push({
                line: lineNum,
                type: 'todo',
                message: `TODO/FIXME found on line ${lineNum}`
            });
        }
        
        if (trimmedLine.includes('console.log')) {
            analysis.issues.push({
                line: lineNum,
                type: 'console-log',
                message: `console.log found on line ${lineNum}`
            });
        }
    });
    
    // Check thresholds
    if (analysis.lines > config.thresholds.maxLines) {
        analysis.issues.push({
            line: 0,
            type: 'file-too-long',
            message: `File has ${analysis.lines} lines (max: ${config.thresholds.maxLines})`
        });
    }
    
    if (analysis.maxComplexity > config.thresholds.complexity) {
        analysis.issues.push({
            line: 0,
            type: 'high-complexity',
            message: `File complexity is ${analysis.maxComplexity} (max: ${config.thresholds.complexity})`
        });
    }
    
    if (analysis.maxDepth > config.thresholds.maxDepth) {
        analysis.issues.push({
            line: 0,
            type: 'deep-nesting',
            message: `Maximum nesting depth is ${analysis.maxDepth} (max: ${config.thresholds.maxDepth})`
        });
    }
    
    if (analysis.maxParams > config.thresholds.maxParams) {
        analysis.issues.push({
            line: 0,
            type: 'too-many-params',
            message: `Function has ${analysis.maxParams} parameters (max: ${config.thresholds.maxParams})`
        });
    }
    
    return analysis;
}

function analyzeDirectory(dirPath) {
    const analysis = {
        files: [],
        summary: {
            totalFiles: 0,
            totalLines: 0,
            totalFunctions: 0,
            totalIssues: 0,
            filesWithIssues: 0
        }
    };
    
    function walkDir(currentPath) {
        const items = fs.readdirSync(currentPath);
        
        items.forEach(item => {
            const fullPath = path.join(currentPath, item);
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                walkDir(fullPath);
            } else if (item.endsWith('.js')) {
                const fileAnalysis = analyzeFile(fullPath);
                analysis.files.push(fileAnalysis);
                
                analysis.summary.totalFiles++;
                analysis.summary.totalLines += fileAnalysis.lines;
                analysis.summary.totalFunctions += fileAnalysis.functions;
                analysis.summary.totalIssues += fileAnalysis.issues.length;
                
                if (fileAnalysis.issues.length > 0) {
                    analysis.summary.filesWithIssues++;
                }
            }
        });
    }
    
    walkDir(dirPath);
    return analysis;
}

// Coverage analysis
function analyzeCoverage() {
    try {
        const coveragePath = path.join(config.coverageDir, 'coverage-summary.json');
        
        if (!fs.existsSync(coveragePath)) {
            logWarning('Coverage report not found');
            return null;
        }
        
        const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
        const total = coverage.total;
        
        const analysis = {
            statements: {
                covered: total.statements.covered,
                total: total.statements.total,
                percentage: total.statements.pct,
                threshold: config.thresholds.coverage.statements,
                passed: total.statements.pct >= config.thresholds.coverage.statements
            },
            branches: {
                covered: total.branches.covered,
                total: total.branches.total,
                percentage: total.branches.pct,
                threshold: config.thresholds.coverage.branches,
                passed: total.branches.pct >= config.thresholds.coverage.branches
            },
            functions: {
                covered: total.functions.covered,
                total: total.functions.total,
                percentage: total.functions.pct,
                threshold: config.thresholds.coverage.functions,
                passed: total.functions.pct >= config.thresholds.coverage.functions
            },
            lines: {
                covered: total.lines.covered,
                total: total.lines.total,
                percentage: total.lines.pct,
                threshold: config.thresholds.coverage.lines,
                passed: total.lines.pct >= config.thresholds.coverage.lines
            }
        };
        
        return analysis;
    } catch (error) {
        logError(`Coverage analysis failed: ${error.message}`);
        return null;
    }
}

// Linting analysis
function runLinting() {
    try {
        logInfo('Running ESLint...');
        const result = execSync('npx eslint static/js --format=json', { encoding: 'utf8' });
        const lintResults = JSON.parse(result);
        
        const analysis = {
            totalFiles: lintResults.length,
            totalErrors: 0,
            totalWarnings: 0,
            filesWithIssues: 0,
            issues: []
        };
        
        lintResults.forEach(file => {
            const fileIssues = file.messages.length;
            if (fileIssues > 0) {
                analysis.filesWithIssues++;
                analysis.totalErrors += file.messages.filter(m => m.severity === 2).length;
                analysis.totalWarnings += file.messages.filter(m => m.severity === 1).length;
                
                file.messages.forEach(message => {
                    analysis.issues.push({
                        file: file.filePath,
                        line: message.line,
                        column: message.column,
                        severity: message.severity === 2 ? 'error' : 'warning',
                        rule: message.ruleId,
                        message: message.message
                    });
                });
            }
        });
        
        return analysis;
    } catch (error) {
        logError(`Linting failed: ${error.message}`);
        return null;
    }
}

// Generate quality report
function generateQualityReport(codeAnalysis, coverageAnalysis, lintAnalysis) {
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            overallScore: 0,
            codeQuality: 0,
            testCoverage: 0,
            linting: 0
        },
        codeAnalysis,
        coverageAnalysis,
        lintAnalysis,
        recommendations: []
    };
    
    // Calculate scores
    let codeQualityScore = 100;
    let lintingScore = 100;
    let coverageScore = 0;
    
    // Code quality score
    if (codeAnalysis.summary.filesWithIssues > 0) {
        codeQualityScore -= (codeAnalysis.summary.filesWithIssues / codeAnalysis.summary.totalFiles) * 50;
    }
    
    // Linting score
    if (lintAnalysis) {
        if (lintAnalysis.totalErrors > 0) {
            lintingScore -= (lintAnalysis.totalErrors / codeAnalysis.summary.totalFiles) * 30;
        }
        if (lintAnalysis.totalWarnings > 0) {
            lintingScore -= (lintAnalysis.totalWarnings / codeAnalysis.summary.totalFiles) * 10;
        }
    }
    
    // Coverage score
    if (coverageAnalysis) {
        const coverageMetrics = ['statements', 'branches', 'functions', 'lines'];
        let totalCoverage = 0;
        
        coverageMetrics.forEach(metric => {
            totalCoverage += coverageAnalysis[metric].percentage;
        });
        
        coverageScore = totalCoverage / coverageMetrics.length;
    }
    
    // Overall score
    report.summary.overallScore = Math.round((codeQualityScore + lintingScore + coverageScore) / 3);
    report.summary.codeQuality = Math.round(codeQualityScore);
    report.summary.testCoverage = Math.round(coverageScore);
    report.summary.linting = Math.round(lintingScore);
    
    // Generate recommendations
    if (codeAnalysis.summary.filesWithIssues > 0) {
        report.recommendations.push('Address code quality issues in files with violations');
    }
    
    if (lintAnalysis && lintAnalysis.totalErrors > 0) {
        report.recommendations.push('Fix ESLint errors to improve code consistency');
    }
    
    if (coverageAnalysis) {
        const coverageMetrics = ['statements', 'branches', 'functions', 'lines'];
        coverageMetrics.forEach(metric => {
            if (!coverageAnalysis[metric].passed) {
                report.recommendations.push(`Increase ${metric} coverage to meet ${coverageAnalysis[metric].threshold}% threshold`);
            }
        });
    }
    
    return report;
}

// Main analysis function
async function runQualityAnalysis() {
    logHeader('SEIM Code Quality Analysis');
    
    try {
        // Analyze source code
        logSection('Analyzing Source Code');
        const codeAnalysis = analyzeDirectory(config.sourceDir);
        
        logInfo(`Analyzed ${codeAnalysis.summary.totalFiles} files`);
        logInfo(`Total lines: ${codeAnalysis.summary.totalLines}`);
        logInfo(`Total functions: ${codeAnalysis.summary.totalFunctions}`);
        logInfo(`Files with issues: ${codeAnalysis.summary.filesWithIssues}`);
        logInfo(`Total issues: ${codeAnalysis.summary.totalIssues}`);
        
        // Analyze coverage
        logSection('Analyzing Test Coverage');
        const coverageAnalysis = analyzeCoverage();
        
        if (coverageAnalysis) {
            const metrics = ['statements', 'branches', 'functions', 'lines'];
            metrics.forEach(metric => {
                const data = coverageAnalysis[metric];
                const status = data.passed ? 'PASS' : 'FAIL';
                const color = data.passed ? 'green' : 'red';
                log(`${metric.toUpperCase()}: ${data.percentage}% (threshold: ${data.threshold}%)`, color);
            });
        }
        
        // Run linting
        logSection('Running Linting Analysis');
        const lintAnalysis = runLinting();
        
        if (lintAnalysis) {
            logInfo(`Linted ${lintAnalysis.totalFiles} files`);
            logInfo(`Files with issues: ${lintAnalysis.filesWithIssues}`);
            logInfo(`Total errors: ${lintAnalysis.totalErrors}`);
            logInfo(`Total warnings: ${lintAnalysis.totalWarnings}`);
        }
        
        // Generate report
        logSection('Generating Quality Report');
        const report = generateQualityReport(codeAnalysis, coverageAnalysis, lintAnalysis);
        
        // Display summary
        logSection('Quality Summary');
        log(`Overall Score: ${report.summary.overallScore}/100`);
        log(`Code Quality: ${report.summary.codeQuality}/100`);
        log(`Test Coverage: ${report.summary.testCoverage}/100`);
        log(`Linting: ${report.summary.linting}/100`);
        
        // Display recommendations
        if (report.recommendations.length > 0) {
            logSection('Recommendations');
            report.recommendations.forEach(rec => {
                logWarning(rec);
            });
        }
        
        // Save report
        const reportPath = path.join(config.reportsDir, `quality-report-${Date.now()}.json`);
        fs.mkdirSync(config.reportsDir, { recursive: true });
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        
        logSuccess(`Quality report saved to ${reportPath}`);
        
        // Return overall status
        const passed = report.summary.overallScore >= 80;
        if (passed) {
            logSuccess('Quality analysis passed!');
        } else {
            logError('Quality analysis failed - score below 80');
        }
        
        return passed;
        
    } catch (error) {
        logError(`Quality analysis failed: ${error.message}`);
        return false;
    }
}

// CLI argument parsing
function parseArguments() {
    const args = process.argv.slice(2);
    const options = {
        detailed: false,
        saveReport: true,
        failOnIssues: false
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
            case '--fail-on-issues':
                options.failOnIssues = true;
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
    logHeader('SEIM Code Quality Analyzer Help');
    log(`
Usage: node scripts/code-quality-analyzer.js [options]

Options:
  --detailed         Show detailed analysis for each file
  --no-report        Skip saving the quality report
  --fail-on-issues   Exit with error code if quality score < 80
  --help, -h         Show this help message

Examples:
  node scripts/code-quality-analyzer.js                    # Run basic analysis
  node scripts/code-quality-analyzer.js --detailed        # Show detailed results
  node scripts/code-quality-analyzer.js --fail-on-issues  # Fail if quality is poor
`, 'cyan');
}

// Main execution
if (require.main === module) {
    const options = parseArguments();
    runQualityAnalysis().then(passed => {
        if (options.failOnIssues && !passed) {
            process.exit(1);
        }
    }).catch(error => {
        logError(`Quality analyzer failed: ${error.message}`);
        process.exit(1);
    });
}

module.exports = {
    runQualityAnalysis,
    analyzeFile,
    analyzeDirectory,
    analyzeCoverage,
    runLinting
}; 