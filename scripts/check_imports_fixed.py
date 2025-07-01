"""
Import checker script to find and fix import errors after refactoring.
"""

import os
import ast
import sys
from pathlib import Path


class ImportChecker(ast.NodeVisitor):
    """Check imports in Python files."""
    
    def __init__(self, filename):
        self.filename = filename
        self.imports = []
        self.errors = []
    
    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            self.imports.append({
                'type': 'import',
                'module': alias.name,
                'line': node.lineno
            })
    
    def visit_ImportFrom(self, node):
        """Visit from...import statements."""
        module = node.module or ''
        for alias in node.names:
            self.imports.append({
                'type': 'from',
                'module': module,
                'name': alias.name,
                'line': node.lineno
            })


def check_file(filepath):
    """Check a single Python file for import issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        checker = ImportChecker(filepath)
        checker.visit(tree)
        
        # Check for problematic imports
        issues = []
        for imp in checker.imports:
            # Check for old serializer imports
            if 'serializers' in imp['module'] and 'api.v1' not in imp['module']:
                if 'exchange.serializers' in imp['module']:
                    issues.append({
                        'file': filepath,
                        'line': imp['line'],
                        'issue': f"Import from '{imp['module']}' should be from 'exchange.api.v1.serializers'",
                        'type': 'serializer_import'
                    })
            
            # Check for old template paths
            if imp['type'] == 'from' and imp['module'] == 'django.template.loader':
                # This would need to check the actual template names used
                pass
            
            # Check for old static paths
            if imp['type'] == 'from' and imp['module'] == 'django.templatetags.static':
                # Static paths are in templates, not Python imports
                pass
        
        return issues
    
    except Exception as e:
        return [{'file': filepath, 'issue': f"Error parsing file: {e}", 'type': 'parse_error'}]


def find_python_files(root_dir):
    """Find all Python files in the project."""
    python_files = []
    exclude_dirs = {'migrations', '__pycache__', '.git', 'venv', '.venv'}
    
    for root, dirs, files in os.walk(root_dir):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def generate_fix_script(issues):
    """Generate a script to fix the issues."""
    fixes = []
    
    for issue in issues:
        if issue['type'] == 'serializer_import':
            fixes.append({
                'file': issue['file'],
                'line': issue['line'],
                'old': 'from exchange.serializers',
                'new': 'from exchange.api.v1.serializers'
            })
    
    return fixes


def main():
    """Main function to check all imports."""
    # Use /app as the project root in the container
    project_root = Path('/app')
    exchange_dir = project_root / 'exchange'
    
    print("Checking Python files for import issues...")
    python_files = find_python_files(exchange_dir)
    
    print(f"Found {len(python_files)} Python files")
    
    all_issues = []
    for pyfile in python_files:
        issues = check_file(pyfile)
        if issues:
            all_issues.extend(issues)
    
    if all_issues:
        print(f"\nFound {len(all_issues)} import issues:\n")
        for issue in all_issues:
            print(f"{issue['file']}:{issue.get('line', '?')}")
            print(f"  Issue: {issue['issue']}")
            print()
        
        # Generate fixes
        fixes = generate_fix_script(all_issues)
        if fixes:
            print("\nSuggested fixes:")
            for fix in fixes:
                print(f"In {fix['file']} line {fix['line']}:")
                print(f"  Replace: {fix['old']}")
                print(f"  With: {fix['new']}")
    else:
        print("\nNo import issues found!")


if __name__ == "__main__":
    main()
