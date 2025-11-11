#!/usr/bin/env python3
"""
Test runner for Selenium E2E tests with coverage reporting.
"""

import subprocess
import sys
from pathlib import Path


def check_server_running():
    """Check if the Django server is running on localhost:8000."""
    try:
        import requests

        response = requests.get("http://localhost:8000", timeout=5)
        return response.status_code == 200
    except:
        return False


def run_selenium_tests():
    """Run Selenium tests with coverage."""
    print("🚀 Starting Selenium E2E Test Suite")
    print("=" * 50)

    # Check if server is running
    if not check_server_running():
        print("❌ Django server is not running on http://localhost:8000")
        print("Please start the server first:")
        print("  docker-compose up web")
        print("  or")
        print("  python manage.py runserver")
        return False

    print("✅ Django server is running")

    # Install coverage if not available
    try:
        import coverage
    except ImportError:
        print("📦 Installing coverage...")
        subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], check=True)

    # Run tests with coverage
    test_file = Path(__file__).parent / "test_core_functionality.py"

    print(f"🧪 Running tests from: {test_file}")
    print("-" * 50)

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--cov=tests.selenium",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov_selenium",
        "--cov-report=xml:coverage_selenium.xml",
    ]

    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ Selenium tests completed successfully!")

        # Show coverage report
        coverage_file = Path("htmlcov_selenium/index.html")
        if coverage_file.exists():
            print(f"📊 Coverage report available at: {coverage_file.absolute()}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code: {e.returncode}")
        return False


if __name__ == "__main__":
    success = run_selenium_tests()
    sys.exit(0 if success else 1)
