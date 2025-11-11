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
4. **End-to-End Tests**: Complete user workflows (Selenium - HOST OS ONLY)
5. **Performance Tests**: Load and stress testing

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

### **Selenium E2E Tests (HOST OS ONLY - Virtual Environment Required):**
```bash
# 1. Setup Virtual Environment (one-time)
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements-dev.txt

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
# Run Jest tests (Virtual Environment Required)
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Run tests
npx jest --config=jest.config.js

# 3. Run with coverage
npx jest --config=jest.config.js --coverage

# 4. Watch mode
npx jest --config=jest.config.js --watch

# 5. Deactivate when done
deactivate
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
pip install -r requirements-dev.txt

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
        self.base_url = "http://localhost:8000"

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
pip install -r requirements-dev.txt

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
pytest tests/selenium/ --base-url=http://localhost:8000
```

---

## 🎯 **Frontend Testing (Virtual Environment Required)**

### **Jest Testing Setup:**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Run Jest tests
npx jest --config=jest.config.js

# 3. Run with coverage
npx jest --config=jest.config.js --coverage

# 4. Watch mode for development
npx jest --config=jest.config.js --watch

# 5. Deactivate when done
deactivate
```

### **Frontend Test Structure:**
```
tests/frontend/
├── unit/                    # Unit tests for JavaScript modules
│   └── modules/
│       └── logger.test.js
├── integration/            # Integration tests
│   └── api/
│       └── api-enhanced.test.js
├── e2e/                   # Frontend E2E tests
│   └── user-workflows.test.js
└── utils/                 # Test utilities
    └── test-utils.js
```

### **Example Jest Test:**
```javascript
// tests/frontend/unit/modules/logger.test.js
import { Logger } from '../../../static/js/modules/logger.js';

describe('Logger', () => {
    test('should log messages correctly', () => {
        const logger = new Logger();
        const consoleSpy = jest.spyOn(console, 'log');
        
        logger.info('Test message');
        
        expect(consoleSpy).toHaveBeenCalledWith('INFO:', 'Test message');
    });
});
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

### **Frontend Coverage (Virtual Environment):**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Run tests with coverage
npx jest --config=jest.config.js --coverage

# 3. View coverage report
# Coverage reports are generated in coverage/frontend/

# 4. Deactivate
deactivate
```

### **Coverage Targets:**
- **Backend**: Minimum 80% coverage
- **Frontend**: Minimum 70% coverage
- **Critical Paths**: 100% coverage for authentication, payment, and data integrity

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

### **Jest Configuration:**
```javascript
// jest.config.js
module.exports = {
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/tests/frontend/setup.js'],
    moduleNameMapping: {
        '^@/(.*)$': '<rootDir>/static/js/$1'
    },
    collectCoverageFrom: [
        'static/js/**/*.js',
        '!static/js/vendor/**'
    ]
};
```

---

## 🚀 **CI/CD Testing**

### **GitHub Actions Workflow:**
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          make test
```

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
- **[Jest Documentation](https://jestjs.io/docs/getting-started)**

---

For testing-specific issues or questions, see the [Troubleshooting Guide](../troubleshooting.md) or [Developer Guide](../developer_guide.md). 