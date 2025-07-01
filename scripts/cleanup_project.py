#!/usr/bin/env python3
"""
Project Cleanup Script for SGII

This script helps clean up the project by removing:
- Python cache files and directories (__pycache__, *.pyc)
- SQLite database (optional)
- Empty directories
- Other temporary files

Usage:
    python cleanup_project.py [options]
    
Options:
    --dry-run          Show what would be deleted without actually deleting
    --include-db       Include SQLite database in cleanup
    --include-static   Include staticfiles directory
    --include-media    Include media directory
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime


class ProjectCleaner:
    def __init__(self, project_root, dry_run=False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.cleaned_items = []
        self.errors = []
        
    def log_action(self, action, item):
        """Log cleanup actions."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] {action}: {item}"
        print(message)
        self.cleaned_items.append(message)
        
    def remove_file(self, file_path):
        """Remove a file with error handling."""
        try:
            if self.dry_run:
                self.log_action("Would remove file", file_path)
            else:
                file_path.unlink()
                self.log_action("Removed file", file_path)
        except Exception as e:
            self.errors.append(f"Error removing {file_path}: {e}")
            
    def remove_directory(self, dir_path):
        """Remove a directory with error handling."""
        try:
            if self.dry_run:
                self.log_action("Would remove directory", dir_path)
            else:
                shutil.rmtree(dir_path)
                self.log_action("Removed directory", dir_path)
        except Exception as e:
            self.errors.append(f"Error removing {dir_path}: {e}")
            
    def clean_python_cache(self):
        """Remove Python cache files and directories."""
        print("\n=== Cleaning Python cache files ===")
        
        # Remove __pycache__ directories
        for pycache_dir in self.project_root.rglob("__pycache__"):
            self.remove_directory(pycache_dir)
            
        # Remove .pyc files
        for pyc_file in self.project_root.rglob("*.pyc"):
            self.remove_file(pyc_file)
            
        # Remove .pyo files
        for pyo_file in self.project_root.rglob("*.pyo"):
            self.remove_file(pyo_file)
            
    def clean_sqlite_db(self):
        """Remove SQLite database files."""
        print("\n=== Cleaning SQLite database ===")
        
        # Common SQLite database patterns
        db_patterns = ["*.sqlite3", "*.sqlite", "*.db"]
        
        for pattern in db_patterns:
            for db_file in self.project_root.rglob(pattern):
                # Skip if it's in .git directory
                if ".git" not in str(db_file):
                    self.remove_file(db_file)
                    
    def clean_temporary_files(self):
        """Remove temporary and backup files."""
        print("\n=== Cleaning temporary files ===")
        
        temp_patterns = [
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.backup",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                # Skip if it's in .git directory
                if ".git" not in str(temp_file):
                    self.remove_file(temp_file)
                    
    def clean_empty_directories(self):
        """Remove empty directories."""
        print("\n=== Cleaning empty directories ===")
        
        # Get all directories in reverse order (deepest first)
        directories = sorted(
            [d for d in self.project_root.rglob("*") if d.is_dir()],
            key=lambda x: len(x.parts),
            reverse=True
        )
        
        for directory in directories:
            # Skip .git directories
            if ".git" in str(directory):
                continue
                
            try:
                # Check if directory is empty
                if not any(directory.iterdir()):
                    self.remove_directory(directory)
            except Exception as e:
                self.errors.append(f"Error checking {directory}: {e}")
                
    def clean_django_static_media(self, include_static=False, include_media=False):
        """Clean Django static and media directories."""
        print("\n=== Cleaning Django directories ===")
        
        seim_dir = self.project_root / "SEIM"
        
        if include_static:
            staticfiles_dir = seim_dir / "staticfiles"
            if staticfiles_dir.exists():
                self.remove_directory(staticfiles_dir)
                
        if include_media:
            media_dir = seim_dir / "media"
            if media_dir.exists():
                self.remove_directory(media_dir)
                
    def clean_log_files(self):
        """Clean log files."""
        print("\n=== Cleaning log files ===")
        
        log_patterns = ["*.log", "*.log.*"]
        
        for pattern in log_patterns:
            for log_file in self.project_root.rglob(pattern):
                # Skip if it's in .git directory
                if ".git" not in str(log_file):
                    self.remove_file(log_file)
                    
    def generate_report(self):
        """Generate cleanup report."""
        report_path = self.project_root / "cleanup_report.txt"
        
        if not self.dry_run:
            with open(report_path, "w") as f:
                f.write("=== SGII Project Cleanup Report ===\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Mode: {'Dry Run' if self.dry_run else 'Actual Cleanup'}\n\n")
                
                f.write("=== Cleaned Items ===\n")
                for item in self.cleaned_items:
                    f.write(f"{item}\n")
                    
                if self.errors:
                    f.write("\n=== Errors ===\n")
                    for error in self.errors:
                        f.write(f"{error}\n")
                        
            print(f"\nReport saved to: {report_path}")
        
        # Print summary
        print("\n=== Cleanup Summary ===")
        print(f"Total items cleaned: {len(self.cleaned_items)}")
        print(f"Errors encountered: {len(self.errors)}")
        
    def run(self, include_db=False, include_static=False, include_media=False):
        """Run the cleanup process."""
        print(f"Starting cleanup of {self.project_root}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'ACTUAL CLEANUP'}\n")
        
        # Clean Python cache
        self.clean_python_cache()
        
        # Clean temporary files
        self.clean_temporary_files()
        
        # Clean log files
        self.clean_log_files()
        
        # Clean SQLite database if requested
        if include_db:
            self.clean_sqlite_db()
            
        # Clean Django directories if requested
        self.clean_django_static_media(include_static, include_media)
        
        # Clean empty directories
        self.clean_empty_directories()
        
        # Generate report
        self.generate_report()
        

def main():
    parser = argparse.ArgumentParser(description="Clean up SGII project")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be deleted without actually deleting")
    parser.add_argument("--include-db", action="store_true",
                       help="Include SQLite database in cleanup")
    parser.add_argument("--include-static", action="store_true",
                       help="Include staticfiles directory")
    parser.add_argument("--include-media", action="store_true",
                       help="Include media directory")
    
    args = parser.parse_args()
    
    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    
    # Create cleaner instance
    cleaner = ProjectCleaner(project_root, dry_run=args.dry_run)
    
    # Run cleanup
    cleaner.run(
        include_db=args.include_db,
        include_static=args.include_static,
        include_media=args.include_media
    )
    

if __name__ == "__main__":
    main()
