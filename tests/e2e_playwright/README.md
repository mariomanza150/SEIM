# E2E Testing with Playwright

## Quick Start

### Run All Tests
```bash
make test-e2e-playwright-docker
```

### Run Specific Test Suite
```bash
# All tests
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/ -v

# Smoke tests only
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_smoke.py -v

# Auth tests only
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_auth_simple.py -v

# Student workflows
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_student_workflows.py -v

# Coordinator workflows
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_coordinator_workflows.py -v

# Admin workflows
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_admin_workflows.py -v
```

### Run with Options
```bash
# Specific browser
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/ -v --browser firefox

# Headed mode (see browser)
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/ -v --headed

# Specific test
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_auth_simple.py::TestAuthenticationSimple::test_login_with_valid_credentials -v
```

## Test Structure

```
tests/e2e_playwright/
├── conftest.py              # Shared fixtures
├── pytest.ini              # Pytest configuration
├── test_smoke.py           # Basic smoke tests (6 tests)
├── test_auth_simple.py      # Authentication tests (10 tests)
├── test_student_workflows.py    # Student workflows (7 tests)
├── test_coordinator_workflows.py # Coordinator workflows (5 tests)
├── test_admin_workflows.py      # Admin workflows (6 tests)
├── utils/
│   ├── __init__.py
│   └── auth_helpers.py     # Authentication utilities
├── screenshots/            # Failure screenshots
├── videos/                 # Test videos (on failure)
└── reports/               # HTML test reports
```

## Test Data

Test users are automatically created with email verification:
- `student1` / `student123`
- `coordinator` / `coord123`
- `admin` / `admin123`

To reseed test data:
```bash
docker-compose -f docker-compose.e2e.yml exec web python manage.py shell -c "exec(open('scripts/seed_e2e_test_data.py').read())"
```

## Writing New Tests

### Basic Test Template
```python
import pytest
from playwright.sync_api import Page
from tests.e2e_playwright.utils.auth_helpers import login_as_student

@pytest.mark.e2e_playwright
@pytest.mark.nondestructive
def test_my_feature(page: Page, base_url: str):
    # Login
    login_as_student(page, base_url)
    
    # Navigate
    page.goto(f"{base_url}/seim/my-page/")
    page.wait_for_load_state("networkidle")
    
    # Assert
    assert "login" not in page.url.lower()
    
    # Screenshot (optional)
    page.screenshot(path="tests/e2e_playwright/screenshots/my_test.png")
```

### Using Auth Helpers
```python
from tests.e2e_playwright.utils.auth_helpers import (
    login_as_student,
    login_as_coordinator,
    login_as_admin,
    logout,
    is_logged_in,
)
```

## Test Markers

- `@pytest.mark.e2e_playwright` - E2E Playwright tests
- `@pytest.mark.nondestructive` - Tests that don't modify database
- `@pytest.mark.workflow` - Workflow tests
- `@pytest.mark.student` - Student-specific tests
- `@pytest.mark.coordinator` - Coordinator-specific tests
- `@pytest.mark.admin` - Admin-specific tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.smoke` - Smoke tests

## Viewing Results

### HTML Report
After tests run, view the HTML report:
```bash
open tests/e2e_playwright/reports/report.html
```

### Screenshots
Screenshots are saved in:
```bash
tests/e2e_playwright/screenshots/
```

## Troubleshooting

### Tests Failing
1. Check screenshots in `tests/e2e_playwright/screenshots/`
2. Check HTML report in `tests/e2e_playwright/reports/`
3. Verify test users exist and have verified emails
4. Check web service is running: `docker-compose -f docker-compose.e2e.yml ps`

### Rate Limiting Errors
Auth helpers automatically handle rate limiting with retries. If you see 429 errors, tests will retry automatically.

### Browser Issues
- Use `--headed` flag to see what's happening
- Check browser version: `docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright playwright --version`

## CI/CD Integration

Tests are ready for CI/CD. Example GitHub Actions:

```yaml
- name: Run E2E Tests
  run: |
    docker-compose -f docker-compose.e2e.yml --profile e2e up --build --abort-on-container-exit e2e_playwright
    docker-compose -f docker-compose.e2e.yml --profile e2e down
```

## More Information

See `E2E_TESTING_COMPLETE_SUMMARY.md` for comprehensive documentation.
