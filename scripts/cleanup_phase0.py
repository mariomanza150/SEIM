#!/usr/bin/env python3
"""
Phase 0: Preparation & Backup
This script performs the initial preparation and backup steps for the SGII cleanup project.
"""

import os
import subprocess
import datetime
import json
from pathlib import Path
import shutil

# Define the project root
PROJECT_ROOT = Path(__file__).parent.parent

def run_command(command, cwd=None):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd or PROJECT_ROOT)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def count_python_files():
    """Count Python files and lines of code"""
    py_files = []
    total_lines = 0
    
    for root, dirs, files in os.walk(PROJECT_ROOT / "SEIM"):
        # Skip __pycache__ directories
        if "__pycache__" in root:
            continue
        
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                py_files.append(str(file_path.relative_to(PROJECT_ROOT)))
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return py_files, total_lines

def create_metrics_report():
    """Create a comprehensive metrics report"""
    print("📊 Creating metrics report...")
    
    metrics = {
        "timestamp": datetime.datetime.now().isoformat(),
        "python_files": {},
        "directory_structure": {},
        "dependencies": {},
        "git_info": {}
    }
    
    # Count Python files and LOC
    py_files, total_lines = count_python_files()
    metrics["python_files"] = {
        "total_files": len(py_files),
        "total_lines": total_lines,
        "files_list": py_files
    }
    
    # Get git information
    stdout, stderr, code = run_command("git log -1 --format='%H %s'")
    if code == 0:
        metrics["git_info"]["last_commit"] = stdout.strip()
    
    stdout, stderr, code = run_command("git branch --show-current")
    if code == 0:
        metrics["git_info"]["current_branch"] = stdout.strip()
    
    # Count files by directory
    for category in ["models", "views", "services", "templates", "static", "tests"]:
        path = PROJECT_ROOT / "SEIM" / "exchange" / category
        if path.exists():
            file_count = sum(1 for _ in path.rglob("*") if _.is_file())
            metrics["directory_structure"][category] = file_count
    
    # Save metrics
    metrics_file = PROJECT_ROOT / "metrics" / "pre_cleanup_metrics.json"
    metrics_file.parent.mkdir(exist_ok=True)
    
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    
    # Create a human-readable report
    report_file = PROJECT_ROOT / "metrics" / "pre_cleanup_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Pre-Cleanup Metrics Report\n\n")
        f.write(f"Generated: {metrics['timestamp']}\n\n")
        f.write("## Python Files\n")
        f.write(f"- Total Files: {metrics['python_files']['total_files']}\n")
        f.write(f"- Total Lines of Code: {metrics['python_files']['total_lines']}\n\n")
        f.write("## Directory Structure\n")
        for category, count in metrics['directory_structure'].items():
            f.write(f"- {category}: {count} files\n")
    
    print(f"✅ Metrics saved to {metrics_file}")
    print(f"✅ Report saved to {report_file}")
    return metrics

def create_git_snapshot():
    """Create a git snapshot with proper tagging"""
    print("📸 Creating git snapshot...")
    
    # Add all files
    stdout, stderr, code = run_command("git add .")
    if code != 0:
        print(f"⚠️  Warning: git add failed: {stderr}")
    
    # Create commit
    commit_message = f"Pre-cleanup snapshot - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    stdout, stderr, code = run_command(f'git commit -m "{commit_message}"')
    if code != 0:
        if "nothing to commit" in stdout or "nothing to commit" in stderr:
            print("ℹ️  No changes to commit")
        else:
            print(f"⚠️  Warning: git commit failed: {stderr}")
    else:
        print(f"✅ Created commit: {commit_message}")
    
    # Create tag
    tag_name = f"pre-cleanup-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    stdout, stderr, code = run_command(f"git tag {tag_name}")
    if code == 0:
        print(f"✅ Created tag: {tag_name}")
    else:
        print(f"⚠️  Warning: git tag failed: {stderr}")

def create_physical_backup():
    """Create a physical backup of the project"""
    print("💾 Creating physical backup...")
    
    backup_dir = PROJECT_ROOT.parent / "SGII_backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"SGII_backup_{timestamp}"
    backup_path = backup_dir / backup_name
    
    # Create a zip archive
    try:
        # Using Python's shutil to create archive
        shutil.make_archive(
            str(backup_path),
            'zip',
            str(PROJECT_ROOT),
            '.'
        )
        print(f"✅ Backup created: {backup_path}.zip")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def main():
    """Main execution function"""
    print("🚀 Starting Phase 0: Preparation & Backup\n")
    
    # Step 1: Create metrics report
    metrics = create_metrics_report()
    
    # Step 2: Create git snapshot
    create_git_snapshot()
    
    # Step 3: Create physical backup
    create_physical_backup()
    
    print("\n✅ Phase 0 completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review the metrics report in metrics/pre_cleanup_report.md")
    print("2. Verify the git tag was created")
    print("3. Confirm the backup was created in the parent directory")
    print("4. Proceed to Phase 1: Code Analysis & Assessment")

if __name__ == "__main__":
    main()
