# SEIM Testing Guide

## Overview
This guide covers comprehensive testing strategies for SEIM (Student Exchange Information Manager), including unit tests, integration tests, frontend tests, and end-to-end testing.

---

## 🧪 **Testing Strategy**

### **Testing Pyramid**
```
        E2E Tests (Few)
           /    \
          /      \
   Integration Tests (Some)
          /    \
         /      \
   Unit Tests (Many)
```

### **Test Types:**
1. **Unit Tests**: Individual components and functions
2. **Integration Tests**: API endpoints and database interactions
3. **Frontend Tests**: JavaScript functionality and UI components
4. **End-to-End Tests (Playwright)**: Comprehensive user workflows with visual regression and accessibility testing
5. **End-to-End Tests (Selenium)**: Legacy browser automation (HOST OS ONLY)
6. **Performance Tests**: Load and stress testing

---

## 🚀 **Quick Start**

### **Run All Tests:**
```bash
# Run all tests (Docker)
make test

# Run with coverage
make test-coverage

# Run specific test types
make test-unit
make test-integration
make test-e2e
```

### **Playwright E2E Tests (Recommended):**
```bash
# Setup E2E environment
make e2e-setup

# Run E2E tests
make e2e-test

# Run with visible browser (debugging)
make e2e-test-headed

# Run in Docker
make e2e-docker

# Run visual regression tests
make e2e-visual

# Run accessibility tests
make e2e-accessibility
```

**See detailed documentation:** [E2E Testing Guide](e2e_testing_guide.md)

### **Selenium E2E Tests (Legacy - HOST OS ONLY):**
```bash
# 1. Setup Virtual Environment (one-time)
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e ".[dev]"

# 2. Setup Selenium environment on host OS
make setup-selenium-host

# 3. Run Selenium tests (requires Django server running in Docker)
make test-selenium

# 4. Run standalone Selenium tests
make test-selenium-standalone

# 5. Test Selenium setup
make test-selenium-setup

# 6. Deactivate virtual environment when done
deactivate
```

### **Frontend Tests:**
```bash
# Vue 3 SPA (Vitest) — no virtualenv required
npm --prefix frontend-vue run test:run

# Coverage
npm --prefix frontend-vue run test:run -- --coverage

# Watch mode
npm --prefix frontend-vue run test
```

---

## 🐍 **Backend Testing (Docker)**

### **Test Structure**
```
tests/
├── unit/                    # Unit tests
│   ├── accounts/           # User management tests
│   ├── exchange/           # Exchange logic tests
│   ├── documents/          # Document handling tests
│   └── notifications/      # Notification tests
├── integration/            # Integration tests
│   ├── api/               # API endpoint tests
│   └── database/          # Database interaction tests
├── e2e/                   # End-to-end tests (Selenium - HOST OS)
│   └── test_user_workflows.py
└── selenium/              # Selenium test runners (HOST OS)
    ├── run_standalone.py
    └── standalone/
```

### **Unit Testing**

#### **Running Unit Tests:**
```bash
# All unit tests (Docker)
make test-unit

# Specific app tests
make test-accounts
make test-exchange
make test-documents
make test-notifications

# Specific test file
docker-compose exec web pytest tests/unit/accounts/test_models.py -v

# Run with verbose output
docker-compose exec web pytest tests/unit/ -v
```

#### **Example Unit Test:**
```python
# tests/unit/accounts/test_models.py
import pytest
from django.test import TestCase
from accounts.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

    def test_user_creation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_role_default(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.role, 'student')

    def test_email_verification(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_email_verified)
        
        user.is_email_verified = True
        user.save()
        self.assertTrue(user.is_email_verified)
```

### **Integration Testing**

#### **API Testing:**
```bash
# Run API integration tests (Docker)
make test-api

# Specific API test
docker-compose exec web pytest tests/integration/api/test_auth_api.py -v
```

#### **Example API Test:**
```python
# tests/integration/api/test_auth_api.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.api
class TestAuthAPI:
    def test_user_login(self):
        client = APIClient()
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post(login_url, login_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
```

### **Database Testing**

#### **Test Database Configuration:**
```python
# settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_seim_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}
```

#### **Using Test Fixtures:**
```python
# tests/unit/exchange/test_models.py
import pytest
from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/fixtures/programs.json')
        call_command('loaddata', 'tests/fixtures/users.json')

class TestProgramModel:
    def test_program_creation(self, django_db_setup):
        from exchange.models import Program
        
        program = Program.objects.create(
            name='Test Program',
            description='Test Description',
            institution='Test University',
            country='Test Country',
            min_gpa=3.0
        )
        
        assert program.name == 'Test Program'
        assert program.min_gpa == 3.0
```

---

## 🌐 **Selenium E2E Testing (HOST OS ONLY - Virtual Environment Required)**

> **⚠️ IMPORTANT: Selenium tests run from the HOST OS, not Docker containers.**
> This is because Selenium requires direct access to the browser and display system.
> **Virtual Environment Required**: All Selenium tests must be run from within a virtual environment.

### **Prerequisites:**
1. **Virtual Environment**: Must be created and activated with all dev dependencies installed
2. **Chrome Browser**: Installed on your host OS
3. **Django Server**: Running in Docker (`docker-compose up web`)
4. **Python Dependencies**: Installed in virtual environment

### **Setup Selenium Environment:**
```bash
# 1. Create and activate virtual environment (one-time setup)
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Install Selenium dependencies in virtual environment
pip install -e ".[dev]"

# 3. Setup Selenium environment
make setup-selenium-host
```

### **Running Selenium Tests:**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Ensure Django server is running in Docker
docker-compose up -d

# 3. Run all Selenium tests
make test-selenium

# 4. Run specific Selenium test
pytest tests/selenium/test_dynforms_builder.py -v

# 5. Run standalone Selenium tests
make test-selenium-standalone

# 6. Test Selenium setup
make test-selenium-setup

# 7. Deactivate virtual environment when done
deactivate
```

### **Selenium Test Structure:**
```
tests/selenium/
├── test_dynforms_builder.py      # Dynforms form builder tests
├── run_standalone.py             # Standalone test runner
└── standalone/                   # Standalone test files
    ├── test_selenium_setup.py
    └── test_selenium_simple.py
```

### **Example Selenium Test:**
```python
# tests/selenium/test_dynforms_builder.py
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class TestDynformsBuilder(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.base_url = "http://localhost:8001"

    def test_dynforms_builder_loads(self):
        # Login as admin
        self.driver.get(f"{self.base_url}/login/")
        # ... test implementation

    def tearDown(self):
        self.driver.quit()
```

### **Troubleshooting Selenium Tests:**

#### **Common Issues:**
```bash
# Issue: "No module named 'celery'" or similar import errors
# Solution: Ensure virtual environment is activated and dependencies are installed
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Issue: Chrome driver not found
# Solution: Install Chrome browser and ensure it's in PATH
# Or use webdriver-manager for automatic driver management

# Issue: Django server not accessible
# Solution: Ensure Docker containers are running
docker-compose up -d

# Issue: Permission errors on Windows
# Solution: Run PowerShell as Administrator or use:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Selenium Test Commands:**
```bash
# Run all Selenium tests
make test-selenium

# Run specific test file
pytest tests/selenium/test_dynforms_builder.py -v

# Run with browser visible (not headless)
pytest tests/selenium/ --headed

# Run with specific browser
pytest tests/selenium/ --browser=chrome

# Run with custom base URL
pytest tests/selenium/ --base-url=http://localhost:8001
```

---

## 🎯 **Frontend Testing (Vue / Vitest)**

### **Vitest setup:**
```bash
npm --prefix frontend-vue run test:run
npm --prefix frontend-vue run test:run -- --coverage
npm --prefix frontend-vue run test
```

### **Frontend Test Structure:**
```
frontend-vue/src/            # Vue views, stores, and colocated *.spec.js
```

### **Example Vitest test:**
```javascript
// frontend-vue/src/stores/auth.spec.js
import { describe, it, expect } from 'vitest'
import { useAuthStore } from './auth'

describe('auth store', () => {
    it('starts unauthenticated', () => {
        const store = useAuthStore()
        expect(store.isAuthenticated).toBe(false)
    })
})
```

---

## 📊 **Test Coverage**

### **Backend Coverage (Docker):**
```bash
# Run tests with coverage
docker-compose exec web coverage run --source='.' manage.py test

# Generate coverage report
docker-compose exec web coverage report

# Generate HTML coverage report
docker-compose exec web coverage html
```

### **Frontend Coverage:**
```bash
npm --prefix frontend-vue run test:coverage
```

### **Coverage Targets:**
- **Backend**: Minimum 80% coverage (hard CI gate: pytest `--cov-fail-under=80`)
- **Frontend**: Vitest coverage collected in CI for `src/stores` and `src/services` (no fail-under gate)
- **Codecov**: Historical tracker + GitHub checks. Add repository secret `CODECOV_TOKEN` from [codecov.io](https://codecov.io) after linking `mariomanza150/SEIM`. Coverage reports are always generated. Upload runs when the secret is set; a missing secret warns and skips upload. The hard gate is pytest `--cov-fail-under=80`. Setup: [`.github/README.md`](../.github/README.md).

---

## 🔧 **Test Configuration**

### **pytest.ini Configuration:**
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = seim.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = --strict-markers --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    api: marks tests as API tests
```

### **Vitest:**
Vue unit tests use `frontend-vue/vitest.config.js` (or the Vite config `test` block). Run them with `npm --prefix frontend-vue run test:run`.

---

## 🚀 **CI/CD Testing**

CI lives in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). Backend pytest writes `coverage.xml`; Vue Vitest writes `frontend-vue/coverage/lcov.info`. Both upload to Codecov (see [`.github/README.md`](../.github/README.md) for `CODECOV_TOKEN`).

### **Local CI Simulation:**
```bash
# Run all tests locally (simulate CI)
make test-all

# Run with coverage
make test-coverage

# Run code quality checks
make quality-check
```

---

## 📚 **Additional Resources**

- **[Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)**
- **[pytest Documentation](https://docs.pytest.org/)**
- **[Selenium Documentation](https://selenium-python.readthedocs.io/)**
- **[Vitest Documentation](https://vitest.dev/)**

---

For testing-specific issues or questions, see the [Troubleshooting Guide](../troubleshooting.md) or [Developer Guide](../developer_guide.md). 