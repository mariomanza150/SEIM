# SEIM End-to-End Testing Guide

## Overview

This guide provides comprehensive documentation for the SEIM E2E testing infrastructure using Playwright.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Writing Tests](#writing-tests)
4. [Running Tests](#running-tests)
5. [Page Object Model](#page-object-model)
6. [Visual Regression Testing](#visual-regression-testing)
7. [Accessibility Testing](#accessibility-testing)
8. [CI/CD Integration](#cicd-integration)
9. [Debugging](#debugging)
10. [Best Practices](#best-practices)

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements-test.txt

# Install Playwright browsers
playwright install chromium firefox webkit --with-deps
```

### Running Tests

```bash
# Run all E2E tests
make e2e-test

# Run with visible browser (for debugging)
make e2e-test-headed

# Run specific test file
pytest tests/e2e_playwright/test_auth_workflows.py -v

# Run in Docker
make e2e-docker
```

## Test Structure

```
tests/e2e_playwright/
├── conftest.py                      # Shared fixtures
├── playwright.config.py             # Playwright configuration
├── pages/                           # Page Object Model
│   ├── base_page.py                # Base page class
│   ├── auth_page.py                # Authentication pages
│   ├── dashboard_page.py           # Dashboard
│   └── ...                         # Other pages
├── utils/                           # Helper utilities
│   ├── auth_helpers.py             # Authentication helpers
│   ├── assertions.py               # Custom assertions
│   └── ...                         # Other utilities
├── fixtures/                        # Test data
│   ├── users.json                  # Test users
│   └── ...                         # Other fixtures
├── test_auth_workflows.py          # Authentication tests
├── test_student_workflows.py       # Student workflow tests
└── ...                             # Other test files
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from tests.e2e_playwright.pages.auth_page import AuthPage

@pytest.mark.e2e_playwright
class TestAuthentication:
    def test_user_login(self, page, base_url, test_users):
        """Test user login functionality."""
        auth_page = AuthPage(page, base_url)
        
        # Navigate to login
        auth_page.navigate_to_login()
        auth_page.assert_login_page_loaded()
        
        # Login
        student = test_users['student1']
        auth_page.login(student['username'], student['password'])
        
        # Verify
        assert auth_page.is_logged_in()
```

### Using Fixtures

```python
def test_with_authentication(self, page, base_url, login_as_student):
    """Test that uses authenticated fixture."""
    # User is already logged in
    dashboard_page = DashboardPage(page, base_url)
    dashboard_page.navigate_to_dashboard()
    dashboard_page.assert_dashboard_loaded()
```

## Page Object Model

### Creating a Page Object

```python
from tests.e2e_playwright.pages.base_page import BasePage

class MyPage(BasePage):
    # Locators
    BUTTON = '[data-testid="my-button"]'
    INPUT = '[data-testid="my-input"]'
    
    # Actions
    def navigate_to_page(self):
        self.navigate('my-page/')
    
    def click_button(self):
        self.click(self.BUTTON)
    
    def fill_input(self, text):
        self.fill(self.INPUT, text)
    
    # Verifications
    def assert_page_loaded(self):
        self.assert_url_contains('my-page')
        self.assert_element_visible(self.BUTTON)
```

### Best Practices

- Use `data-testid` attributes for locators
- Keep locators as class constants
- Create high-level action methods
- Add verification methods
- Extend `BasePage` for common functionality

## Running Tests

### Command Line Options

```bash
# Run all tests
pytest tests/e2e_playwright/

# Run specific marker
pytest tests/e2e_playwright/ -m smoke

# Run with headed browser
pytest tests/e2e_playwright/ --headed

# Run in parallel
pytest tests/e2e_playwright/ -n auto

# Run with base URL
pytest tests/e2e_playwright/ --base-url=http://localhost:8000

# Generate HTML report
pytest tests/e2e_playwright/ --html=report.html --self-contained-html
```

### Makefile Commands

```bash
make e2e-setup          # Setup E2E environment
make e2e-test           # Run tests (headless)
make e2e-test-headed    # Run tests (visible browser)
make e2e-docker         # Run in Docker
make e2e-visual         # Run visual regression tests
make e2e-accessibility  # Run accessibility tests
make e2e-parallel       # Run in parallel
make e2e-report         # Open test report
make e2e-clean          # Clean artifacts
```

## Visual Regression Testing

### Creating Visual Tests

```python
def test_page_visual(self, page, base_url, assert_visual_match):
    """Test visual appearance of page."""
    page.goto(f"{base_url}/my-page/")
    
    # Hide dynamic elements
    from tests.e2e_playwright.utils.visual_regression import hide_dynamic_elements
    hide_dynamic_elements(page, ['.timestamp', '.notification-badge'])
    
    # Compare with baseline
    assert assert_visual_match('my_page')
```

### Updating Baselines

```bash
# Update all baselines
pytest tests/e2e_playwright/test_visual_regression.py --update-baseline

# Update specific baseline
pytest tests/e2e_playwright/test_visual_regression.py::test_login_page_visual --update-baseline
```

## Accessibility Testing

### Writing Accessibility Tests

```python
def test_page_accessibility(self, page, base_url):
    """Test accessibility compliance."""
    page.goto(f"{base_url}/my-page/")
    
    from axe_playwright_python.sync_playwright import Axe
    axe = Axe()
    results = axe.run(page)
    
    assert len(results.violations) == 0
```

### Running Accessibility Tests

```bash
make e2e-accessibility
```

## CI/CD Integration

E2E tests run automatically on:
- Push to main/develop branches
- Pull requests
- Manual workflow dispatch

### GitHub Actions

See `.github/workflows/e2e-tests.yml` for configuration.

Artifacts uploaded on failure:
- Screenshots
- Videos
- Test reports

## Debugging

### Visual Debugging

```bash
# Run with visible browser
make e2e-test-headed

# Run with slow motion
pytest tests/e2e_playwright/ --headed --slowmo=500
```

### Screenshot Debugging

Screenshots are automatically captured on test failure in:
- `tests/e2e_playwright/screenshots/`

### Using Playwright Inspector

```bash
# Run with inspector
PWDEBUG=1 pytest tests/e2e_playwright/test_auth_workflows.py
```

### Viewing Traces

```bash
# Enable tracing in conftest.py, then:
playwright show-trace tests/e2e_playwright/traces/trace.zip
```

## Best Practices

### Test Organization

- Group related tests in classes
- Use descriptive test names
- Add docstrings to tests
- Use appropriate markers (`@pytest.mark.e2e_playwright`, etc.)

### Assertions

- Use page object verification methods
- Make assertions specific and meaningful
- Assert expected behavior, not implementation details

### Waits

- Use built-in Playwright auto-waiting
- Use explicit waits for dynamic content
- Avoid fixed time sleeps

### Data

- Use fixtures for test data
- Use factories/generators for dynamic data
- Clean up test data after tests

### Maintenance

- Keep page objects in sync with UI changes
- Update visual baselines after intentional UI changes
- Refactor flaky tests immediately
- Review and update tests regularly

## Troubleshooting

### Common Issues

**Tests fail with timeout:**
- Increase timeout in `playwright.config.py`
- Check if application is running
- Verify network connectivity

**Visual tests fail unexpectedly:**
- Check if UI changed intentionally
- Update baselines if changes are correct
- Adjust threshold in config

**Accessibility tests fail:**
- Review axe violations
- Fix accessibility issues in code
- Update tests if requirements changed

**Tests pass locally but fail in CI:**
- Check environment differences
- Verify test data setup
- Review CI logs and artifacts

## Additional Resources

- [Playwright Documentation](https://playwright.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Axe Accessibility](https://www.deque.com/axe/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## Support

For issues or questions:
1. Check this documentation
2. Review example tests in `tests/e2e_playwright/examples/`
3. Check CI/CD logs for failures
4. Contact the development team

