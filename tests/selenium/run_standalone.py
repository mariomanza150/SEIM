#!/usr/bin/env python3
"""
Standalone test runner for Selenium E2E tests.
This bypasses pytest-django and runs tests directly.
"""

import sys
import unittest
from pathlib import Path

# Add the selenium test directory to Python path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))


def check_server_running():
    """Check if the Django server is running on localhost:8000."""
    try:
        import requests

        response = requests.get("http://localhost:8000", timeout=5)
        return response.status_code == 200
    except:
        return False


def run_standalone_tests():
    """Run Selenium tests without pytest-django."""
    print("🚀 Starting Standalone Selenium E2E Test Suite")
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

    # Import and run tests
    try:
        from test_core_functionality import TestCoreFunctionality

        # Create test suite
        suite = unittest.TestSuite()

        # Add all test methods
        test_methods = [
            "test_homepage_accessibility",
            "test_user_registration",
            "test_user_login",
            "test_dashboard_access",
            "test_programs_listing",
            "test_application_creation",
            "test_document_upload",
            "test_error_handling",
            "test_responsive_design",
        ]

        for method_name in test_methods:
            if hasattr(TestCoreFunctionality, method_name):
                suite.addTest(TestCoreFunctionality(method_name))

        # Run tests
        print(f"🧪 Running {len(test_methods)} test methods")
        print("-" * 50)

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        print("\n" + "=" * 50)
        print("📊 Test Results:")
        print(f"  Tests run: {result.testsRun}")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

        if result.failures:
            print("\n❌ Failures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")

        if result.errors:
            print("\n❌ Errors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")

        success = len(result.failures) == 0 and len(result.errors) == 0
        if success:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ {len(result.failures) + len(result.errors)} tests failed")

        return success

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed:")
        print("  pip install selenium webdriver-manager requests")
        return False
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_standalone_tests()
    sys.exit(0 if success else 1)
