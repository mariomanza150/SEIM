#!/usr/bin/env python3
"""
Demo setup script for SEIM application.
This script sets up the system with comprehensive test data for demonstration.
"""

import os
import sys
from pathlib import Path

import django

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seim.settings.development")
django.setup()

from django.core.management import call_command


def setup_demo():
    """Set up the SEIM system with demo data."""
    print("🚀 Setting up SEIM Demo Environment...")

    try:
        # 1. Run initial data creation
        print("\n📋 Creating initial system data...")
        call_command("create_initial_data")

        # 2. Create comprehensive demo data
        print("\n👥 Creating demo users, programs, and applications...")
        call_command(
            "create_demo_data",
            users=25,  # 25 users total
            programs=8,  # 8 diverse programs
            applications=75,
        )  # 75 applications

        # 3. Assign roles to any existing users
        print("\n🔐 Assigning roles to users...")
        call_command("assign_user_roles")

        # 4. Create missing profiles
        print("\n👤 Creating missing user profiles...")
        call_command("create_missing_profiles")

        print("\n✅ Demo setup completed successfully!")
        print("\n📊 Demo Data Summary:")
        print("   • 25 users (2 admins, 3 coordinators, 20 students)")
        print("   • 8 exchange programs")
        print("   • 75 applications with various statuses")
        print("   • Documents, comments, and notifications")

        print("\n🔑 Demo Login Credentials:")
        print("   Admin: admin1 / admin123")
        print("   Coordinator: coordinator1 / coordinator123")
        print("   Student: student1 / student123")

        print("\n🌐 Access the application at: http://localhost:8000")

    except Exception as e:
        print(f"\n❌ Error during demo setup: {e}")
        return False

    return True


if __name__ == "__main__":
    success = setup_demo()
    sys.exit(0 if success else 1)
