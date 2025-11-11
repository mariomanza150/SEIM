#!/usr/bin/env python3
"""
Script to automatically rename test files for uniqueness and clean up pycache files.
This resolves import conflicts caused by duplicate test file names across directories.
"""

import glob
import os
import shutil


def clean_pycache_files():
    """Remove all __pycache__ directories and .pyc files."""
    print("Cleaning up __pycache__ files...")

    # Find all __pycache__ directories
    pycache_dirs = []
    for root, dirs, _files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))

    # Remove __pycache__ directories
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"Removed: {pycache_dir}")
        except Exception as e:
            print(f"Error removing {pycache_dir}: {e}")

    # Find and remove .pyc files
    pyc_files = glob.glob('**/*.pyc', recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"Removed: {pyc_file}")
        except Exception as e:
            print(f"Error removing {pyc_file}: {e}")

def rename_test_files():
    """Rename test files to ensure uniqueness across directories."""
    print("Renaming test files for uniqueness...")

    # Define the renaming rules
    rename_rules = {
        # Unit tests
        'tests/unit/accounts/test_views.py': 'tests/unit/accounts/test_accounts_views.py',
        'tests/unit/accounts/test_views_simple.py': 'tests/unit/accounts/test_accounts_views_simple.py',
        'tests/unit/accounts/test_serializers.py': 'tests/unit/accounts/test_accounts_serializers.py',
        'tests/unit/accounts/test_models.py': 'tests/unit/accounts/test_accounts_models.py',
        'tests/unit/accounts/test_management_commands.py': 'tests/unit/accounts/test_accounts_management_commands.py',
        'tests/unit/accounts/test_management_commands_accounts.py': 'tests/unit/accounts/test_accounts_management_commands_accounts.py',
        'tests/unit/accounts/test_management_commands_assign_user_roles.py': 'tests/unit/accounts/test_accounts_management_commands_assign_user_roles.py',
        'tests/unit/accounts/test_signals.py': 'tests/unit/accounts/test_accounts_signals.py',

        'tests/unit/analytics/test_views.py': 'tests/unit/analytics/test_analytics_views.py',
        'tests/unit/analytics/test_serializers.py': 'tests/unit/analytics/test_analytics_serializers.py',
        'tests/unit/analytics/test_services.py': 'tests/unit/analytics/test_analytics_services.py',
        'tests/unit/analytics/test_analytics_views_simple.py': 'tests/unit/analytics/test_analytics_views_simple.py',
        'tests/unit/analytics/test_analytics_views_extended.py': 'tests/unit/analytics/test_analytics_views_extended.py',
        'tests/unit/analytics/test_analytics_services.py': 'tests/unit/analytics/test_analytics_services_extended.py',
        'tests/unit/analytics/test_analytics_views.py': 'tests/unit/analytics/test_analytics_views_main.py',
        'tests/unit/analytics/test_services_analytics.py': 'tests/unit/analytics/test_analytics_services_main.py',
        'tests/unit/analytics/test_analytics_models.py': 'tests/unit/analytics/test_analytics_models.py',
        'tests/unit/analytics/test_tasks.py': 'tests/unit/analytics/test_analytics_tasks.py',

        'tests/unit/core/test_views.py': 'tests/unit/core/test_core_views.py',
        'tests/unit/core/test_management_commands.py': 'tests/unit/core/test_core_management_commands.py',
        'tests/unit/core/test_management_commands_basic.py': 'tests/unit/core/test_core_management_commands_basic.py',
        'tests/unit/core/test_management_commands_simple.py': 'tests/unit/core/test_core_management_commands_simple.py',
        'tests/unit/core/test_management_commands_extended.py': 'tests/unit/core/test_core_management_commands_extended.py',
        'tests/unit/core/test_management_commands_core.py': 'tests/unit/core/test_core_management_commands_core.py',
        'tests/unit/core/test_permissions.py': 'tests/unit/core/test_core_permissions.py',
        'tests/unit/core/test_cache.py': 'tests/unit/core/test_core_cache.py',
        'tests/unit/core/test_core_models.py': 'tests/unit/core/test_core_models.py',

        'tests/unit/documents/test_services.py': 'tests/unit/documents/test_documents_services.py',
        'tests/unit/documents/test_document_services.py': 'tests/unit/documents/test_documents_services_main.py',
        'tests/unit/documents/test_document_services_simple.py': 'tests/unit/documents/test_documents_services_simple.py',
        'tests/unit/documents/test_document_serializers.py': 'tests/unit/documents/test_documents_serializers.py',
        'tests/unit/documents/test_document_tasks.py': 'tests/unit/documents/test_documents_tasks.py',

        'tests/unit/exchange/test_views.py': 'tests/unit/exchange/test_exchange_views.py',
        'tests/unit/exchange/test_serializers.py': 'tests/unit/exchange/test_exchange_serializers.py',
        'tests/unit/exchange/test_models.py': 'tests/unit/exchange/test_exchange_models.py',
        'tests/unit/exchange/test_services_exchange.py': 'tests/unit/exchange/test_exchange_services.py',
        'tests/unit/exchange/test_management_commands_cleanup_demo_data.py': 'tests/unit/exchange/test_exchange_management_commands_cleanup_demo_data.py',

        'tests/unit/notifications/test_services.py': 'tests/unit/notifications/test_notifications_services.py',
        'tests/unit/notifications/test_services_notifications.py': 'tests/unit/notifications/test_notifications_services_extended.py',
        'tests/unit/notifications/test_notification_services.py': 'tests/unit/notifications/test_notifications_services_main.py',

        'tests/unit/frontend/test_views.py': 'tests/unit/frontend/test_frontend_views.py',
        'tests/unit/frontend/test_frontend_views.py': 'tests/unit/frontend/test_frontend_views_main.py',

        'tests/unit/api/test_views.py': 'tests/unit/api/test_api_views.py',

        'tests/unit/dashboard/test_views.py': 'tests/unit/dashboard/test_dashboard_views.py',

        'tests/unit/management/test_management_commands.py': 'tests/unit/management/test_management_commands_main.py',

        'tests/unit/test_dynforms_access.py': 'tests/unit/test_dynforms_access.py',
        'tests/unit/test_dashboard_username.py': 'tests/unit/test_dashboard_username.py',
        'tests/unit/test_simple_coverage.py': 'tests/unit/test_simple_coverage.py',
        'tests/unit/test_basic_coverage.py': 'tests/unit/test_basic_coverage.py',

        # Integration tests
        'tests/integration/api/test_applications_api.py': 'tests/integration/api/test_applications_api.py',
        'tests/integration/api/test_auth_api.py': 'tests/integration/api/test_auth_api.py',
        'tests/integration/api/test_exchange_api.py': 'tests/integration/api/test_exchange_api.py',

        # E2E tests
        'tests/e2e/test_user_workflows.py': 'tests/e2e/test_user_workflows.py',

        # Selenium tests
        'tests/selenium/standalone/test_selenium_setup.py': 'tests/selenium/standalone/test_selenium_setup.py',
        'tests/selenium/standalone/test_selenium_simple.py': 'tests/selenium/standalone/test_selenium_simple.py',
        'tests/selenium/standalone/test_theme_debug_selenium.py': 'tests/selenium/standalone/test_theme_debug_selenium.py',
        'tests/selenium/standalone/test_selenium_registration.py': 'tests/selenium/standalone/test_selenium_registration.py',

        # Frontend tests
        'tests/frontend/e2e/user-workflows.test.js': 'tests/frontend/e2e/user-workflows.test.js',
        'tests/frontend/integration/api/api-enhanced.test.js': 'tests/frontend/integration/api/api-enhanced.test.js',
        'tests/frontend/unit/applications.test.js': 'tests/frontend/unit/applications.test.js',
        'tests/frontend/unit/auth.test.js': 'tests/frontend/unit/auth.test.js',
        'tests/frontend/unit/modules/accessibility-tester.test.js': 'tests/frontend/unit/modules/accessibility-tester.test.js',
        'tests/frontend/unit/modules/accessibility.test.js': 'tests/frontend/unit/modules/accessibility.test.js',
        'tests/frontend/unit/modules/api-enhanced.test.js': 'tests/frontend/unit/modules/api-enhanced.test.js',
        'tests/frontend/unit/modules/ui/auth_ui.test.js': 'tests/frontend/unit/modules/ui/auth_ui.test.js',
        'tests/frontend/unit/modules/ui/bootstrap_helpers.test.js': 'tests/frontend/unit/modules/ui/bootstrap_helpers.test.js',
        'tests/frontend/unit/modules/ui/loading.test.js': 'tests/frontend/unit/modules/ui/loading.test.js',
        'tests/frontend/unit/modules/analytics.test.js': 'tests/frontend/unit/modules/analytics.test.js',
        'tests/frontend/unit/modules/applications.test.js': 'tests/frontend/unit/modules/applications.test.js',
        'tests/frontend/unit/modules/auth.test.js': 'tests/frontend/unit/modules/auth.test.js',
        'tests/frontend/unit/modules/dashboard.test.js': 'tests/frontend/unit/modules/dashboard.test.js',
        'tests/frontend/unit/modules/documents.test.js': 'tests/frontend/unit/modules/documents.test.js',
        'tests/frontend/unit/modules/exchange.test.js': 'tests/frontend/unit/modules/exchange.test.js',
        'tests/frontend/unit/modules/forms.test.js': 'tests/frontend/unit/modules/forms.test.js',
        'tests/frontend/unit/modules/navigation.test.js': 'tests/frontend/unit/modules/navigation.test.js',
        'tests/frontend/unit/modules/notifications.test.js': 'tests/frontend/unit/modules/notifications.test.js',
        'tests/frontend/unit/modules/programs.test.js': 'tests/frontend/unit/modules/programs.test.js',
        'tests/frontend/unit/modules/search.test.js': 'tests/frontend/unit/modules/search.test.js',
        'tests/frontend/unit/modules/theme.test.js': 'tests/frontend/unit/modules/theme.test.js',
        'tests/frontend/unit/modules/ui.test.js': 'tests/frontend/unit/modules/ui.test.js',
        'tests/frontend/unit/modules/utils.test.js': 'tests/frontend/unit/modules/utils.test.js',
        'tests/frontend/unit/modules/validation.test.js': 'tests/frontend/unit/modules/validation.test.js',
        'tests/frontend/unit/modules/workflow.test.js': 'tests/frontend/unit/modules/workflow.test.js',
        'tests/frontend/utils/test-utils.js': 'tests/frontend/utils/test-utils.js',
    }

    # Perform the renames
    for old_path, new_path in rename_rules.items():
        if os.path.exists(old_path):
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(new_path), exist_ok=True)

                # Rename the file
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")
            except Exception as e:
                print(f"Error renaming {old_path}: {e}")
        else:
            print(f"File not found: {old_path}")

def main():
    """Main function to clean pycache and rename test files."""
    print("Starting test file cleanup and renaming...")

    # Clean pycache files first
    clean_pycache_files()

    # Rename test files
    rename_test_files()

    print("Test file cleanup and renaming completed!")

if __name__ == "__main__":
    main()
