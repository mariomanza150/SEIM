# SEIM Testing Guide

## Overview
This guide covers all testing approaches for SEIM, including unit tests, integration tests, frontend tests, and Selenium E2E tests.

---

## 🧪 **Test Types**

### **1. Unit & Integration Tests (Docker)**
- **Location**: `tests/unit/`, `tests/integration/`
- **Environment**: Docker containers
- **Command**: `make test-unit`, `make test-integration`

### **2. Frontend Tests (Host OS)**
- **Location**: `tests/frontend/`
- **Environment**: Host OS with Node.js
- **Command**: `npx jest --config=jest.config.js`

### **3. Selenium E2E Tests (HOST OS ONLY)**
- **Location**: `tests/e2e/`, `tests/selenium/`
- **Environment**: Host OS (not Docker)
- **Command**: `make test-selenium`

---

## 🌐 **Selenium E2E Testing (HOST OS ONLY)**

> **⚠️ IMPORTANT: Selenium tests run from the HOST OS, not Docker containers.**
> This is because Selenium requires direct access to the browser and display system.

### **Prerequisites**
- Google Chrome installed on host OS
- Python 3.8+ on host OS
- Django server running in Docker (`docker-compose up web`)

### **Setup Selenium Environment**

#### **Option 1: Use Makefile (Recommended)**
```bash
# Setup Selenium environment on host OS
make setup-selenium-host
```

#### **Option 2: Manual Setup**
```bash
# Install Python dependencies
pip install selenium webdriver-manager pytest-selenium requests

# Verify Chrome installation
# Windows: C:\Program Files\Google\Chrome\Application\chrome.exe
# macOS: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
# Linux: /usr/bin/google-chrome
```

### **Running Selenium Tests**

#### **Quick Commands**
```bash
# Run all Selenium E2E tests
make test-selenium

# Run standalone Selenium tests
make test-selenium-standalone

# Test Selenium setup
make test-selenium-setup

# Run specific test file
python -m pytest tests/e2e/test_user_workflows.py -v
```

#### **Manual Commands**
```bash
# Run with pytest
python -m pytest tests/e2e/ -v -m e2e

# Run standalone test runner
python tests/selenium/run_standalone.py

# Test setup verification
python tests/selenium/test_setup_verification.py
```

### **Test Structure**
```
tests/
├── e2e/                    # Main E2E tests (pytest)
│   └── test_user_workflows.py
├── selenium/               # Selenium test runners
│   ├── run_standalone.py
│   ├── run_tests.py
│   ├── test_core_functionality.py
│   ├── test_setup_verification.py
│   └── standalone/         # Standalone test files
│       ├── test_selenium_setup.py
│       ├── test_selenium_simple.py
│       └── test_theme_toggle.py
```

### **Configuration**
Selenium tests are configured to use Remote WebDriver connecting to Chrome on the host OS:

```python
# Example configuration from tests/e2e/test_user_workflows.py
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Use Remote WebDriver to connect to Chrome on host OS
host_ip = os.environ.get("SELENIUM_HOST", "host.docker.internal")
cls.driver = webdriver.Remote(
    command_executor=f"http://{host_ip}:4444/wd/hub",
    options=chrome_options,
)
```

### **Environment Variables**
```bash
# Optional: Set custom Selenium host
export SELENIUM_HOST=localhost

# Optional: Set Chrome options
export CHROME_HEADLESS=true
```

---

## 🐳 **Docker-Based Testing**

### **Unit & Integration Tests**
```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-api

# Run with coverage
make test-coverage

# Run specific app tests
make test-accounts
make test-exchange
make test-documents
```

### **Test Structure**
```
tests/
├── unit/                    # Unit tests
│   ├── accounts/           # User management tests
│   ├── exchange/           # Exchange logic tests
│   └── documents/          # Document handling tests
├── integration/            # Integration tests
│   └── api/               # API endpoint tests
└── fixtures/              # Test data
    ├── users.json         # User test data
    └── programs.json      # Program test data
```

---

## 🎨 **Frontend Testing**

### **Jest Configuration**
```bash
# Run all frontend tests
npx jest --config=jest.config.js

# Run with coverage
npx jest --config=jest.config.js --coverage

# Run specific test file
npx jest --config=jest.config.js tests/frontend/unit/modules/logger.test.js
```

### **Test Structure**
```
tests/frontend/
├── unit/                   # Unit tests
│   └── modules/           # JavaScript module tests
├── integration/           # Integration tests
│   └── api/              # API integration tests
└── setup.js              # Jest setup file
```

---

## 🔧 **Troubleshooting**

### **Selenium Issues (HOST OS)**
```bash
# Chrome not found
# Install Chrome browser on your host OS

# ChromeDriver issues
pip install --upgrade webdriver-manager

# Django server not running
docker-compose up web

# Permission issues
# Run tests with appropriate user permissions
```

### **Docker Test Issues**
```bash
# Database connection issues
docker-compose down -v
docker-compose up -d db
docker-compose exec web python manage.py migrate

# Test environment issues
docker-compose exec web python manage.py check
```

### **Frontend Test Issues**
```bash
# Node modules issues
rm -rf node_modules package-lock.json
npm install

# Jest configuration issues
npx jest --config=jest.config.js --verbose
```

---

## 📚 **Additional Resources**

- **[Main Testing Guide](../documentation/testing.md)** - Comprehensive testing documentation
- **[Developer Guide](../documentation/developer_guide.md)** - Development setup and workflows
- **[Installation Guide](../documentation/installation.md)** - Project setup instructions

---

## 📋 **Quick Reference**

### **All Test Commands**
```bash
# Docker-based tests
make test              # All tests
make test-unit         # Unit tests
make test-integration  # Integration tests
make test-api          # API tests

# Host OS tests
make test-selenium     # Selenium E2E tests
npx jest --config=jest.config.js  # Frontend tests

# Setup
make setup-selenium-host  # Setup Selenium environment
```

### **Test Coverage**
```bash
# Backend coverage (Docker)
make test-coverage

# Frontend coverage (Host OS)
npx jest --config=jest.config.js --coverage

# Selenium coverage (Host OS)
python -m pytest tests/e2e/ --cov=. --cov-report=html:htmlcov_selenium
``` 