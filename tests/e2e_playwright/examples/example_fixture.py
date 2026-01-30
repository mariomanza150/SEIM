"""
Example fixtures demonstrating best practices.

This shows how to create custom fixtures for E2E tests.
"""

import pytest


@pytest.fixture
def example_test_data():
    """
    Example fixture providing test data.
    
    Returns:
        Dictionary of test data
    """
    return {
        'valid_email': 'test@example.com',
        'invalid_email': 'not-an-email',
        'test_string': 'Hello, World!',
        'test_number': 42
    }


@pytest.fixture
def example_authenticated_page(page, base_url, test_users):
    """
    Example fixture that provides an authenticated page.
    
    Args:
        page: Playwright page fixture
        base_url: Base URL fixture
        test_users: Test users fixture
    
    Returns:
        Authenticated page object
    """
    from tests.e2e_playwright.pages.auth_page import AuthPage
    
    auth_page = AuthPage(page, base_url)
    auth_page.navigate_to_login()
    
    # Login with test user
    student = test_users['student1']
    auth_page.login(student['username'], student['password'])
    
    return page


@pytest.fixture
def example_cleanup():
    """
    Example fixture with setup and teardown.
    
    This demonstrates how to perform cleanup after a test.
    """
    # Setup code here
    test_data = []
    
    yield test_data  # Test runs here
    
    # Teardown/cleanup code here
    test_data.clear()


@pytest.fixture(scope='module')
def example_module_fixture():
    """
    Example module-scoped fixture.
    
    This fixture is created once per test module
    and shared across all tests in the module.
    """
    # Expensive setup that should only happen once
    config = {'setting': 'value'}
    
    yield config
    
    # Cleanup after all tests in module complete
    config.clear()

