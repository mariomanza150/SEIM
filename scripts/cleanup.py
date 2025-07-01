#!/usr/bin/env python3
"""
SGII Project Cleanup Master Script
This script orchestrates the entire cleanup process across all phases.
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).parent.parent

# Define all cleanup phases
PHASES = {
    0: {
        "name": "Preparation & Backup",
        "script": "cleanup_phase0.py",
        "description": "Create backups and document current state"
    },
    1: {
        "name": "Code Analysis & Assessment",
        "script": "cleanup_phase1.py",
        "description": "Analyze code quality, complexity, and security"
    },
    2: {
        "name": "Code Formatting & Style",
        "script": "cleanup_phase2.py",
        "description": "Apply consistent formatting and fix style issues"
    },
    3: {
        "name": "Structural Refactoring",
        "script": "cleanup_phase3.py",
        "description": "Reorganize code structure for better modularity"
    },
    4: {
        "name": "Testing & Quality Assurance",
        "script": "cleanup_phase4.py",
        "description": "Enhance test coverage and ensure functionality"
    },
    5: {
        "name": "Configuration & Settings",
        "script": "cleanup_phase5.py",
        "description": "Optimize Django settings and configurations"
    },
    6: {
        "name": "Performance Optimization",
        "script": "cleanup_phase6.py",
        "description": "Optimize queries, implement caching, and improve performance"
    },
    7: {
        "name": "Documentation",
        "script": "cleanup_phase7.py",
        "description": "Update and enhance project documentation"
    },
    8: {
        "name": "Security Hardening",
        "script": "cleanup_phase8.py",
        "description": "Fix vulnerabilities and enhance security measures"
    },
    9: {
        "name": "Final Validation",
        "script": "cleanup_phase9.py",
        "description": "Validate all changes and ensure nothing is broken"
    },
    10: {
        "name": "Deployment Preparation",
        "script": "cleanup_phase10.py",
        "description": "Prepare for production deployment"
    }
}

def print_header(phase_num, phase_info):
    """Print a formatted header for each phase"""
    print("\n" + "=" * 80)
    print(f"🔧 PHASE {phase_num}: {phase_info['name'].upper()}")
    print(f"📋 {phase_info['description']}")
    print("=" * 80 + "\n")

def run_phase(phase_num):
    """Run a specific cleanup phase"""
    phase_info = PHASES.get(phase_num)
    if not phase_info:
        print(f"❌ Invalid phase number: {phase_num}")
        return False
    
    print_header(phase_num, phase_info)
    
    script_path = PROJECT_ROOT / "scripts" / phase_info["script"]
    
    if not script_path.exists():
        print(f"⚠️  Script not found: {script_path}")
        print("Creating placeholder script...")
        create_placeholder_script(phase_num, phase_info)
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=False
        )
        
        if result.returncode == 0:
            print(f"\n✅ Phase {phase_num} completed successfully!")
            mark_phase_complete(phase_num)
            return True
        else:
            print(f"\n❌ Phase {phase_num} failed with exit code: {result.returncode}")
            return False
    except Exception as e:
        print(f"\n❌ Error running phase {phase_num}: {e}")
        return False

def create_placeholder_script(phase_num, phase_info):
    """Create a placeholder script for phases not yet implemented"""
    script_path = PROJECT_ROOT / "scripts" / phase_info["script"]
    
    content = f'''#!/usr/bin/env python3
"""
Phase {phase_num}: {phase_info['name']}
{phase_info['description']}
"""

import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def main():
    """Main execution function"""
    print("🚀 Starting Phase {phase_num}: {phase_info['name']}\\n")
    
    # TODO: Implement phase {phase_num} logic
    print("⚠️  This phase is not yet implemented")
    print("📋 Tasks for this phase:")
    print("- Review CLEANUP_PLAN.md for detailed steps")
    print("- Implement required functionality")
    print("- Test thoroughly before proceeding")
    
    print("\\n✅ Phase {phase_num} placeholder completed!")

if __name__ == "__main__":
    main()
'''
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created placeholder: {script_path}")

def mark_phase_complete(phase_num):
    """Mark a phase as complete"""
    status_file = PROJECT_ROOT / "reports" / f"phase_{phase_num}_completed.txt"
    status_file.parent.mkdir(exist_ok=True)
    
    with open(status_file, 'w') as f:
        f.write(f"Phase {phase_num} completed at {datetime.datetime.now()}\n")

def show_progress():
    """Show cleanup progress based on completed phases"""
    print("\n📊 CLEANUP PROGRESS")
    print("=" * 80)
    
    completed = []
    pending = []
    
    for phase_num, phase_info in PHASES.items():
        status_file = PROJECT_ROOT / "reports" / f"phase_{phase_num}_completed.txt"
        
        if status_file.exists():
            completed.append(phase_num)
            print(f"✅ Phase {phase_num}: {phase_info['name']}")
        else:
            pending.append(phase_num)
            print(f"⏳ Phase {phase_num}: {phase_info['name']}")
    
    print("\n" + "=" * 80)
    print(f"Completed: {len(completed)}/{len(PHASES)} phases")
    print(f"Progress: {'█' * len(completed)}{'░' * len(pending)} {len(completed)*10}%")
    print("=" * 80)

def run_all_phases(start_from=0):
    """Run all phases sequentially"""
    print("🚀 STARTING FULL CLEANUP PROCESS")
    print(f"Starting from phase {start_from}")
    
    for phase_num in range(start_from, len(PHASES)):
        if not run_phase(phase_num):
            print(f"\n⚠️  Stopping at phase {phase_num} due to errors")
            print("Fix the issues and run again with --start-from {}".format(phase_num))
            return False
        
        # Ask for confirmation before proceeding to next phase
        if phase_num < len(PHASES) - 1:
            response = input(f"\nProceed to phase {phase_num + 1}? (y/n): ")
            if response.lower() != 'y':
                print("⏸️  Paused cleanup process")
                print(f"Resume with: python cleanup.py --start-from {phase_num + 1}")
                return True
    
    print("\n🎉 ALL PHASES COMPLETED SUCCESSFULLY!")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SGII Project Cleanup Tool")
    parser.add_argument(
        "--phase",
        type=int,
        help="Run a specific phase (0-10)"
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=0,
        help="Start from a specific phase when running all"
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show cleanup progress"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all phases"
    )
    
    args = parser.parse_args()
    
    print("🧹 SGII PROJECT CLEANUP TOOL")
    print("=" * 80)
    
    if args.list:
        print("\n📋 Available Phases:")
        for phase_num, phase_info in PHASES.items():
            print(f"  {phase_num}: {phase_info['name']}")
            print(f"     {phase_info['description']}")
        return
    
    if args.progress:
        show_progress()
        return
    
    if args.phase is not None:
        run_phase(args.phase)
    else:
        run_all_phases(args.start_from)

if __name__ == "__main__":
    main()
