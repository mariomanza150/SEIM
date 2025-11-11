# SEIM Test Scripts

This directory contains scripts for running different types of tests in the SEIM project.

## Scripts Overview

### Core Test Scripts

#### `run_tests.sh` - Comprehensive Test Runner
Orchestrates all test types: backend (Docker), frontend (host), and Selenium (host).

**Usage:**
```bash
./scripts/run_tests.sh [test_suite] [backend_type] [frontend_type] [selenium_type]
```

**Test Suites:**
- `all` - Run all test types (default)
- `backend` - Run backend tests only
- `frontend` - Run frontend tests only
- `selenium` - Run Selenium tests only
- `quick` - Run quick test suite (unit tests only)
- `ci` - Run CI test suite (comprehensive with coverage)

**Examples:**
```bash
./scripts/run_tests.sh                    # Run all tests
./scripts/run_tests.sh quick              # Run quick test suite
./scripts/run_tests.sh backend unit       # Run backend unit tests only
./scripts/run_tests.sh frontend unit      # Run frontend unit tests only
./scripts/run_tests.sh selenium e2e       # Run Selenium E2E tests only
./scripts/run_tests.sh ci                 # Run CI test suite
```

#### `test_frontend.sh` - Frontend Test Runner
Runs Jest tests on the host OS (not Docker).

**Usage:**
```bash
./scripts/test_frontend.sh [test_type] [coverage] [watch]
```

**Test Types:**
- `all` - All frontend tests (default)
- `unit` - Unit tests only
- `integration` - Integration tests only
- `e2e` - E2E tests only
- `debug` - Debug mode
- `ci` - CI mode with coverage

**Examples:**
```bash
./scripts/test_frontend.sh                    # Run all tests
./scripts/test_frontend.sh unit true         # Run unit tests with coverage
./scripts/test_frontend.sh all true true     # Run all tests with coverage and watch mode
./scripts/test_frontend.sh ci                # Run CI tests
```

#### `test_selenium.sh` - Selenium Test Runner
Runs Selenium E2E tests on the host OS (not Docker).

**Usage:**
```bash
./scripts/test_selenium.sh [test_type]
```

**Test Types:**
- `all` - All Selenium E2E tests (default)
- `e2e` - E2E tests only
- `selenium` - Core functionality tests
- `standalone` - Standalone tests
- `setup` - Setup verification

**Environment Variables:**
- `SELENIUM_HOST` - Host for Selenium tests (default: host.docker.internal)
- `CHROME_HEADLESS` - Run Chrome in headless mode (default: true)
- `PYTEST_OPTS` - Additional pytest options

**Examples:**
```bash
./scripts/test_selenium.sh                    # Run all tests
./scripts/test_selenium.sh e2e               # Run E2E tests only
./scripts/test_selenium.sh setup             # Test setup
SELENIUM_HOST=localhost ./scripts/test_selenium.sh  # Use localhost
```

### Setup Scripts

#### `setup_test_environment.sh` - Test Environment Setup
Sets up the environment for running all test types.

**Usage:**
```bash
./scripts/setup_test_environment.sh
```

**What it does:**
1. Checks and sets up Docker environment for backend tests
2. Checks and sets up Node.js environment for frontend tests
3. Checks and sets up Python environment for Selenium tests
4. Installs required dependencies
5. Tests the setup

**Requirements:**
- Docker Desktop or Docker daemon
- Node.js 14+ and npm
- Python 3.8+ and pip
- Chrome browser (for Selenium tests)

## Environment Requirements

### Backend Tests (Docker)
- Docker and Docker Compose
- Django server running in container
- Database migrations applied

### Frontend Tests (Host OS)
- Node.js 14+ and npm
- Jest configuration (`jest.config.frontend.js`)
- npm dependencies installed

### Selenium Tests (Host OS)
- Python 3.8+ with selenium, webdriver-manager, pytest-selenium, requests
- Chrome browser installed
- Django server running (for E2E tests)

## Makefile Integration

The scripts are integrated into the Makefile with convenient targets:

```bash
# Quick test suite
make test-quick

# Unit tests (backend + frontend)
make test-unit

# Integration tests (backend + frontend)
make test-integration

# E2E tests
make test-e2e

# Frontend tests
make test-frontend

# Selenium tests
make test-selenium

# All tests
make test-all

# Test workflow
make test-workflow

# Setup test environment
make setup-test-env
```

## Test Reports

The comprehensive test runner (`run_tests.sh`) generates test reports with:
- Test results (passed/failed/skipped)
- Execution times
- Coverage information (when applicable)
- Summary statistics

Reports are saved to `test-report-YYYYMMDD-HHMMSS.txt` in the project root.

## Troubleshooting

### Common Issues

1. **Docker not running**
   - Start Docker Desktop or Docker daemon
   - Check with `docker info`

2. **Node.js/npm not found**
   - Install Node.js from https://nodejs.org/
   - Verify with `node --version` and `npm --version`

3. **Python dependencies missing**
   - Run `pip install selenium webdriver-manager pytest-selenium requests`
   - Or use `./scripts/setup_test_environment.sh`

4. **Chrome browser not found**
   - Install Chrome browser from https://www.google.com/chrome/
   - Verify installation path

5. **Django server not running**
   - Start with `docker-compose up web`
   - Check if accessible at http://localhost:8000

### Getting Help

- Run `./scripts/run_tests.sh --help` for comprehensive test runner help
- Run `./scripts/test_frontend.sh --help` for frontend test help
- Run `./scripts/test_selenium.sh --help` for Selenium test help
- Run `./scripts/setup_test_environment.sh --help` for setup help

## Best Practices

1. **Always run tests in the correct environment:**
   - Backend tests: Docker containers
   - Frontend tests: Host OS with Node.js
   - Selenium tests: Host OS with Python and Chrome

2. **Use the comprehensive test runner for CI/CD:**
   ```bash
   ./scripts/run_tests.sh ci
   ```

3. **Set up the test environment once:**
   ```bash
   make setup-test-env
   ```

4. **Run quick tests during development:**
   ```bash
   make test-quick
   ```

5. **Check test reports for detailed information:**
   - Look for generated test report files
   - Check coverage reports in `coverage/` directories 