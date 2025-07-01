#!/usr/bin/env python3
"""
Phase 1: Code Analysis & Assessment
This script performs comprehensive code analysis on the SGII project.
"""

import os
import subprocess
import json
import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
SEIM_DIR = PROJECT_ROOT / "SEIM"

# Ensure reports directory exists
REPORTS_DIR.mkdir(exist_ok=True)

def run_command(command, output_file=None):
    """Run a command and optionally save output to file"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=str(PROJECT_ROOT)
        )
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Command: {command}\n")
                f.write(f"Exit Code: {result.returncode}\n")
                f.write(f"Timestamp: {datetime.datetime.now()}\n")
                f.write("=" * 80 + "\n")
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
        
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return "", str(e), 1

def install_analysis_tools():
    """Install required analysis tools"""
    print("📦 Installing analysis tools...")
    tools = [
        "radon",
        "pylint",
        "flake8",
        "black",
        "isort",
        "vulture",
        "bandit",
        "safety",
        "mypy",
        "coverage"
    ]
    
    for tool in tools:
        print(f"Installing {tool}...")
        stdout, stderr, code = run_command(f"pip install {tool}")
        if code != 0:
            print(f"⚠️  Failed to install {tool}: {stderr}")

def analyze_complexity():
    """Run complexity analysis with radon"""
    print("\n📊 Running complexity analysis...")
    
    # Cyclomatic complexity
    run_command(
        "python -m radon cc SEIM/ -s -a --json",
        REPORTS_DIR / "complexity_cc.json"
    )
    
    # Maintainability index
    run_command(
        "python -m radon mi SEIM/ -s",
        REPORTS_DIR / "maintainability_index.txt"
    )
    
    # Raw metrics
    run_command(
        "python -m radon raw SEIM/",
        REPORTS_DIR / "raw_metrics.txt"
    )
    
    # Halstead metrics
    run_command(
        "python -m radon hal SEIM/",
        REPORTS_DIR / "halstead_metrics.txt"
    )

def analyze_code_quality():
    """Run code quality analysis"""
    print("\n🔍 Running code quality analysis...")
    
    # Pylint
    run_command(
        "python -m pylint SEIM/ --output-format=json",
        REPORTS_DIR / "pylint_report.json"
    )
    
    # Also create a text report for easier reading
    run_command(
        "python -m pylint SEIM/ --output-format=text",
        REPORTS_DIR / "pylint_report.txt"
    )
    
    # Flake8
    run_command(
        "python -m flake8 SEIM/ --format=default --output-file=" + str(REPORTS_DIR / "flake8_report.txt"),
        REPORTS_DIR / "flake8_full_output.txt"
    )

def analyze_security():
    """Run security analysis"""
    print("\n🔒 Running security analysis...")
    
    # Bandit
    run_command(
        "python -m bandit -r SEIM/ -f json",
        REPORTS_DIR / "bandit_security.json"
    )
    
    # Also create a text report
    run_command(
        "python -m bandit -r SEIM/ -f txt",
        REPORTS_DIR / "bandit_security.txt"
    )
    
    # Safety check for dependencies
    run_command(
        "python -m safety check --json",
        REPORTS_DIR / "safety_dependencies.json"
    )

def analyze_dead_code():
    """Detect dead code with vulture"""
    print("\n🦅 Detecting dead code...")
    
    run_command(
        "python -m vulture SEIM/ --min-confidence 80",
        REPORTS_DIR / "dead_code_analysis.txt"
    )

def analyze_type_hints():
    """Check type hints with mypy"""
    print("\n🏷️  Analyzing type hints...")
    
    run_command(
        "python -m mypy SEIM/ --ignore-missing-imports",
        REPORTS_DIR / "mypy_type_analysis.txt"
    )

def analyze_test_coverage():
    """Analyze test coverage"""
    print("\n🧪 Analyzing test coverage...")
    
    # Run tests with coverage
    run_command(
        "python -m coverage run --source=SEIM manage.py test",
        REPORTS_DIR / "coverage_run.txt"
    )
    
    # Generate coverage report
    run_command(
        "python -m coverage report",
        REPORTS_DIR / "coverage_report.txt"
    )
    
    # Generate HTML coverage report
    run_command("python -m coverage html --directory=reports/coverage_html")

def create_analysis_summary():
    """Create a summary of all analysis results"""
    print("\n📝 Creating analysis summary...")
    
    summary_file = REPORTS_DIR / "ANALYSIS_SUMMARY.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Code Analysis Summary\n\n")
        f.write(f"Generated: {datetime.datetime.now()}\n\n")
        
        f.write("## 📊 Complexity Analysis\n")
        f.write("- See complexity_cc.json for cyclomatic complexity details\n")
        f.write("- See maintainability_index.txt for maintainability scores\n")
        f.write("- See raw_metrics.txt for LOC and other metrics\n\n")
        
        f.write("## 🔍 Code Quality\n")
        f.write("- Pylint report: pylint_report.txt\n")
        f.write("- Flake8 violations: flake8_report.txt\n\n")
        
        f.write("## 🔒 Security Analysis\n")
        f.write("- Bandit security issues: bandit_security.txt\n")
        f.write("- Dependency vulnerabilities: safety_dependencies.json\n\n")
        
        f.write("## 🦅 Dead Code\n")
        f.write("- Potential dead code: dead_code_analysis.txt\n\n")
        
        f.write("## 🏷️ Type Hints\n")
        f.write("- Type checking results: mypy_type_analysis.txt\n\n")
        
        f.write("## 🧪 Test Coverage\n")
        f.write("- Coverage report: coverage_report.txt\n")
        f.write("- HTML report: coverage_html/index.html\n\n")
        
        f.write("## 🎯 Priority Areas for Cleanup\n")
        f.write("1. **High Complexity Functions**: Review functions with CC > 10\n")
        f.write("2. **Security Issues**: Address any high-severity security findings\n")
        f.write("3. **Code Style**: Fix flake8 and pylint violations\n")
        f.write("4. **Dead Code**: Remove unused functions and variables\n")
        f.write("5. **Test Coverage**: Increase coverage for critical paths\n")
        f.write("6. **Type Hints**: Add type annotations to improve code clarity\n")
    
    print(f"✅ Summary created: {summary_file}")

def main():
    """Main execution function"""
    print("🚀 Starting Phase 1: Code Analysis & Assessment\n")
    
    # Step 1: Install tools
    install_analysis_tools()
    
    # Step 2: Run analyses
    analyze_complexity()
    analyze_code_quality()
    analyze_security()
    analyze_dead_code()
    analyze_type_hints()
    analyze_test_coverage()
    
    # Step 3: Create summary
    create_analysis_summary()
    
    print("\n✅ Phase 1 completed!")
    print("\n📋 Next steps:")
    print("1. Review the analysis reports in the reports/ directory")
    print("2. Prioritize issues based on severity and impact")
    print("3. Proceed to Phase 2: Code Formatting & Style")

if __name__ == "__main__":
    main()
