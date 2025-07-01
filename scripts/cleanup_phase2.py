#!/usr/bin/env python3
"""
Phase 2: Code Formatting & Style
Apply consistent formatting and fix style violations across the codebase.
"""

import os
import subprocess
import shutil
from pathlib import Path
import datetime

PROJECT_ROOT = Path(__file__).parent.parent
SEIM_DIR = PROJECT_ROOT / "SEIM"
REPORTS_DIR = PROJECT_ROOT / "reports"

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or str(PROJECT_ROOT)
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def backup_before_formatting():
    """Create a backup before applying formatting"""
    print("💾 Creating backup before formatting...")
    
    backup_dir = PROJECT_ROOT / "backups" / f"pre_formatting_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy Python files
    for py_file in SEIM_DIR.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            relative_path = py_file.relative_to(PROJECT_ROOT)
            backup_path = backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, backup_path)
    
    print(f"✅ Backup created: {backup_dir}")

def apply_black_formatting():
    """Apply Black formatting to all Python files"""
    print("\n⚫ Applying Black formatting...")
    
    # Configure Black
    config = """
[tool.black]
line-length = 120
target-version = ['py312']
include = '\\.pyi?$'
extend-exclude = '''
/(
  migrations
  | __pycache__
  | \\.venv
  | build
  | dist
  | staticfiles
)/
'''
"""
    
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        with open(pyproject_path, 'w') as f:
            f.write(config)
    
    # Run Black
    stdout, stderr, code = run_command("python -m black SEIM/ --verbose")
    
    if code == 0:
        print("✅ Black formatting applied successfully")
    else:
        print(f"⚠️  Black formatting had issues: {stderr}")
    
    # Save report
    with open(REPORTS_DIR / "black_formatting.txt", 'w') as f:
        f.write(f"Black Formatting Report\n")
        f.write(f"Generated: {datetime.datetime.now()}\n")
        f.write("=" * 80 + "\n")
        f.write(stdout)
        if stderr:
            f.write("\nErrors:\n")
            f.write(stderr)

def apply_isort_formatting():
    """Apply isort to organize imports"""
    print("\n📦 Organizing imports with isort...")
    
    # Configure isort in pyproject.toml
    isort_config = """

[tool.isort]
profile = "black"
line_length = 120
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "*/__pycache__/*"]
known_django = ["django"]
known_first_party = ["exchange", "seim"]
sections = ["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
"""
    
    # Append to pyproject.toml
    with open(PROJECT_ROOT / "pyproject.toml", 'a') as f:
        f.write(isort_config)
    
    # Run isort
    stdout, stderr, code = run_command("python -m isort SEIM/ --verbose")
    
    if code == 0:
        print("✅ Import sorting completed successfully")
    else:
        print(f"⚠️  Import sorting had issues: {stderr}")
    
    # Save report
    with open(REPORTS_DIR / "isort_formatting.txt", 'w') as f:
        f.write(f"isort Import Sorting Report\n")
        f.write(f"Generated: {datetime.datetime.now()}\n")
        f.write("=" * 80 + "\n")
        f.write(stdout)

def fix_common_issues():
    """Fix common style issues"""
    print("\n🔧 Fixing common style issues...")
    
    issues_fixed = {
        "trailing_whitespace": 0,
        "missing_newline_eof": 0,
        "multiple_blank_lines": 0
    }
    
    for py_file in SEIM_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove trailing whitespace
            lines = content.split('\n')
            cleaned_lines = [line.rstrip() for line in lines]
            if lines != cleaned_lines:
                issues_fixed["trailing_whitespace"] += 1
                content = '\n'.join(cleaned_lines)
            
            # Ensure newline at end of file
            if content and not content.endswith('\n'):
                content += '\n'
                issues_fixed["missing_newline_eof"] += 1
            
            # Fix multiple blank lines (more than 2)
            while '\n\n\n\n' in content:
                content = content.replace('\n\n\n\n', '\n\n\n')
                issues_fixed["multiple_blank_lines"] += 1
            
            # Write back if changed
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        except Exception as e:
            print(f"⚠️  Error processing {py_file}: {e}")
    
    print(f"✅ Fixed issues:")
    for issue, count in issues_fixed.items():
        print(f"   - {issue}: {count} files")

def add_missing_docstrings():
    """Add template docstrings to functions/classes missing them"""
    print("\n📝 Checking for missing docstrings...")
    
    # This is a placeholder - in reality, you'd use AST parsing
    # to identify functions/classes without docstrings
    print("⚠️  Manual review needed for missing docstrings")
    print("   Consider using tools like pydocstyle for detailed analysis")

def update_file_headers():
    """Update or add file headers with copyright and description"""
    print("\n📄 Updating file headers...")
    
    header_template = '''"""
{description}

Copyright (c) 2025 SGII Project
Licensed under the MIT License
"""

'''
    
    files_updated = 0
    
    # This is simplified - you'd want more sophisticated logic
    print("⚠️  File header updates require manual review")
    print("   Ensure each module has appropriate description")

def run_style_check():
    """Run a final style check after formatting"""
    print("\n🔍 Running final style check...")
    
    # Run flake8 with specific configuration
    flake8_config = """
[flake8]
max-line-length = 120
exclude = 
    migrations,
    __pycache__,
    .venv,
    staticfiles,
    media
ignore = 
    # Black compatibility
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
    # Django specific
    DJ01,  # null=True on string fields
per-file-ignores =
    __init__.py:F401
"""
    
    with open(PROJECT_ROOT / ".flake8", 'w') as f:
        f.write(flake8_config)
    
    stdout, stderr, code = run_command(
        "python -m flake8 SEIM/ --statistics --output-file=reports/flake8_post_formatting.txt"
    )
    
    print("✅ Style check complete - see reports/flake8_post_formatting.txt")

def generate_formatting_report():
    """Generate a summary report of formatting changes"""
    print("\n📊 Generating formatting report...")
    
    report_path = REPORTS_DIR / "formatting_summary.md"
    
    with open(report_path, 'w') as f:
        f.write("# Code Formatting Summary\n\n")
        f.write(f"Generated: {datetime.datetime.now()}\n\n")
        
        f.write("## 🎨 Formatting Tools Applied\n\n")
        f.write("1. **Black** - Code formatting\n")
        f.write("   - Line length: 120 characters\n")
        f.write("   - Target version: Python 3.12\n\n")
        
        f.write("2. **isort** - Import sorting\n")
        f.write("   - Profile: black compatible\n")
        f.write("   - Sections: STDLIB, DJANGO, THIRDPARTY, FIRSTPARTY\n\n")
        
        f.write("3. **Custom fixes**\n")
        f.write("   - Removed trailing whitespace\n")
        f.write("   - Added missing newlines at EOF\n")
        f.write("   - Normalized blank lines\n\n")
        
        f.write("## 📋 Next Steps\n\n")
        f.write("1. Review the formatting changes in git\n")
        f.write("2. Run tests to ensure nothing broke\n")
        f.write("3. Address any remaining style violations\n")
        f.write("4. Consider adding pre-commit hooks\n")
    
    print(f"✅ Report saved: {report_path}")

def main():
    """Main execution function"""
    print("🚀 Starting Phase 2: Code Formatting & Style\n")
    
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(exist_ok=True)
    
    # Step 1: Backup before formatting
    backup_before_formatting()
    
    # Step 2: Apply formatters
    apply_black_formatting()
    apply_isort_formatting()
    
    # Step 3: Fix common issues
    fix_common_issues()
    
    # Step 4: Add missing docstrings (placeholder)
    add_missing_docstrings()
    
    # Step 5: Update file headers (placeholder)
    update_file_headers()
    
    # Step 6: Run final style check
    run_style_check()
    
    # Step 7: Generate report
    generate_formatting_report()
    
    print("\n✅ Phase 2 completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review formatting changes: git diff")
    print("2. Run tests: python manage.py test")
    print("3. Commit changes: git add -A && git commit -m 'Apply code formatting'")
    print("4. Proceed to Phase 3: Structural Refactoring")

if __name__ == "__main__":
    main()
