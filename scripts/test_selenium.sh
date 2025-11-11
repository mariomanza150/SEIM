#!/bin/bash
set -e

# SEIM Selenium Test Runner
# Runs Selenium E2E tests on HOST OS (not Docker)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SELENIUM_HOST="${SELENIUM_HOST:-host.docker.internal}"
CHROME_HEADLESS="${CHROME_HEADLESS:-true}"
PYTEST_OPTS="${PYTEST_OPTS:--v --tb=short}"

# Export environment variables
export SELENIUM_HOST
export CHROME_HEADLESS
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

log_info "SEIM Selenium Test Runner"
log_info "========================"
log_info "SELENIUM_HOST: $SELENIUM_HOST"
log_info "CHROME_HEADLESS: $CHROME_HEADLESS"
log_info "Project root: $PROJECT_ROOT"

# Check if Django server is running
check_server() {
    log_info "Checking if Django server is running..."
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        log_success "Django server is running on http://localhost:8000"
        return 0
    else
        log_error "Django server is not running on http://localhost:8000"
        log_warning "Please start the server first:"
        log_warning "  docker-compose up web"
        log_warning "  or"
        log_warning "  python manage.py runserver"
        return 1
    fi
}

# Check Python dependencies
check_dependencies() {
    log_info "Checking Python dependencies..."
    
    local missing_deps=()
    
    python -c "import selenium" 2>/dev/null || missing_deps+=("selenium")
    python -c "import pytest" 2>/dev/null || missing_deps+=("pytest")
    python -c "import requests" 2>/dev/null || missing_deps+=("requests")
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_warning "Missing dependencies: ${missing_deps[*]}"
        log_info "Installing missing dependencies..."
        pip install "${missing_deps[@]}"
    else
        log_success "All dependencies are installed"
    fi
}

# Run Selenium tests
run_selenium_tests() {
    local test_path="$1"
    local test_type="$2"
    
    log_info "Running $test_type tests..."
    log_info "Test path: $test_path"
    
    cd "$PROJECT_ROOT"
    
    # Run pytest with the specified options
    if python -m pytest "$test_path" $PYTEST_OPTS; then
        log_success "$test_type tests completed successfully"
        return 0
    else
        log_error "$test_type tests failed"
        return 1
    fi
}

# Main execution
main() {
    local test_type="${1:-all}"
    local exit_code=0
    
    # Check server first
    if ! check_server; then
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    # Run tests based on type
    case "$test_type" in
        "all"|"e2e")
            log_info "Running all Selenium E2E tests..."
            if ! run_selenium_tests "tests/e2e/" "E2E"; then
                exit_code=1
            fi
            ;;
        "selenium")
            log_info "Running Selenium core functionality tests..."
            if ! run_selenium_tests "tests/selenium/test_core_functionality.py" "Selenium Core"; then
                exit_code=1
            fi
            ;;
        "standalone")
            log_info "Running standalone Selenium tests..."
            if ! python tests/selenium/run_standalone.py; then
                exit_code=1
            fi
            ;;
        "setup")
            log_info "Testing Selenium setup..."
            if ! python tests/selenium/standalone/test_selenium_setup.py; then
                exit_code=1
            fi
            ;;
        *)
            log_error "Unknown test type: $test_type"
            log_info "Available types: all, e2e, selenium, standalone, setup"
            exit 1
            ;;
    esac
    
    if [ $exit_code -eq 0 ]; then
        log_success "All tests completed successfully!"
    else
        log_error "Some tests failed!"
    fi
    
    exit $exit_code
}

# Show help
show_help() {
    echo "SEIM Selenium Test Runner"
    echo "========================"
    echo ""
    echo "Usage: $0 [test_type]"
    echo ""
    echo "Test types:"
    echo "  all        - Run all Selenium E2E tests (default)"
    echo "  e2e        - Run E2E tests only"
    echo "  selenium   - Run Selenium core functionality tests"
    echo "  standalone - Run standalone Selenium tests"
    echo "  setup      - Test Selenium setup"
    echo ""
    echo "Environment variables:"
    echo "  SELENIUM_HOST    - Host for Selenium tests (default: host.docker.internal)"
    echo "  CHROME_HEADLESS  - Run Chrome in headless mode (default: true)"
    echo "  PYTEST_OPTS      - Additional pytest options"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 e2e               # Run E2E tests only"
    echo "  $0 setup             # Test setup"
    echo "  SELENIUM_HOST=localhost $0  # Use localhost"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 