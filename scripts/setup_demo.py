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
        # 1. Seed deterministic demo-ready data
        print("\n📋 Creating demo-ready users, programs, applications, and supporting records...")
        call_command("seed_demo_readiness")

        print("\n✅ Demo setup completed successfully!")
        print("\n📊 Demo Data Summary:")
        print("   • Canonical admin, coordinator, and student demo accounts")
        print("   • Active exchange programs ready for browsing")
        print("   • Applications in every workflow status")
        print("   • Supporting documents, comments, timeline events, and notifications")
        print("   • Exchange agreements (active, draft, renewal pending, expired) for the staff registry")

        print("\n🔑 Demo Login Credentials:")
        print("   Admin: admin@test.com / admin123")
        print("   Coordinator: coordinator@test.com / coordinator123")
        print("   Student: student@test.com / student123")

        print("\n🌐 Access the application at: http://localhost:8000")

    except Exception as e:
        print(f"\n❌ Error during demo setup: {e}")
        return False

    return True


if __name__ == "__main__":
    success = setup_demo()
    sys.exit(0 if success else 1)
