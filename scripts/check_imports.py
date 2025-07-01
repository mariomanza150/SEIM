#!/usr/bin/env python
"""
Import checker script for SEIM project.
Checks all Python files for import errors and reports broken imports.
"""

import os
import sys
import ast
import importlib
import traceback
from pathlib import Path


class ImportChecker:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []
        
    def check_file(self, file_path):
        """Check a single Python file for import issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse the AST to find import statements
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.check_import(alias.name, file_path)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.check_from_import(node.module, node.names, file_path)
                        
        except SyntaxError as e:
            self.errors.append(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            self.errors.append(f"Error parsing {file_path}: {e}")
            
    def check_import(self, module_name, file_path):
        """Check if a module can be imported"""
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            self.errors.append(f"Import error in {file_path}: import {module_name} - {e}")
        except Exception as e:
            self.warnings.append(f"Warning in {file_path}: import {module_name} - {e}")
            
    def check_from_import(self, module_name, names, file_path):
        """Check from imports"""
        try:
            module = importlib.import_module(module_name)
            for alias in names:
                if alias.name != '*':
                    if not hasattr(module, alias.name):
                        self.warnings.append(
                            f"Warning in {file_path}: from {module_name} import {alias.name} - "
                            f"attribute may not exist"
                        )
        except ImportError as e:
            self.errors.append(f"Import error in {file_path}: from {module_name} import ... - {e}")
        except Exception as e:
            self.warnings.append(f"Warning in {file_path}: from {module_name} import ... - {e}")
            
    def check_project(self):
        """Check all Python files in the project"""
        print(f"Checking imports in {self.project_root}...")
        
        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', '.git', 'node_modules', 'staticfiles', 
                'media', 'logs', '.pytest_cache', 'venv', 'env'
            ]]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
                    
        print(f"Found {len(python_files)} Python files")
        
        # Check each file
        for file_path in python_files:
            print(f"Checking {file_path.relative_to(self.project_root)}...")
            self.check_file(file_path)
            
        # Report results
        self.report_results()
        
    def report_results(self):
        """Report the results of the import check"""
        print("\n" + "="*80)
        print("IMPORT CHECK RESULTS")
        print("="*80)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print("\n✅ No import errors found!")
            
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        else:
            print("\n✅ No import warnings!")
            
        print(f"\nSUMMARY:")
        print(f"  • Errors: {len(self.errors)}")
        print(f"  • Warnings: {len(self.warnings)}")
        
        if self.errors == 0 and self.warnings == 0:
            print("\n🎉 All imports are clean!")
            return True
        return False


if __name__ == "__main__":
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.custom_settings.dev')
    
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent / "SEIM"
    sys.path.insert(0, str(project_root))
    
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"Warning: Could not set up Django environment: {e}")
        print("Continuing with basic import checking...")
        
    # Run the import checker
    checker = ImportChecker(project_root)
    success = checker.check_project()
    
    sys.exit(0 if success else 1)
