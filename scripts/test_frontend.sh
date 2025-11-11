#!/bin/bash
set -e

# SEIM Frontend Test Runner
# Runs Jest tests on HOST OS (not Docker)

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
JEST_CONFIG="jest.config.frontend.js"
COVERAGE_DIR="coverage/frontend"

# Check if Node.js and npm are available
check_node_environment() {
    log_info "Checking Node.js environment..."
    
    if ! command -v node >/dev/null 2>&1; then
        log_error "Node.js is not installed or not in PATH"
        log_warning "Please install Node.js from https://nodejs.org/"
        return 1
    fi
    
    if ! command -v npm >/dev/null 2>&1; then
        log_error "npm is not installed or not in PATH"
        log_warning "Please install npm"
        return 1
    fi
    
    log_success "Node.js $(node --version) and npm $(npm --version) are available"
    return 0
}

# Check if Jest config exists
check_jest_config() {
    log_info "Checking Jest configuration..."
    
    if [ ! -f "$PROJECT_ROOT/$JEST_CONFIG" ]; then
        log_error "Jest configuration file not found: $JEST_CONFIG"
        return 1
    fi
    
    log_success "Jest configuration found: $JEST_CONFIG"
    return 0
}

# Install dependencies if needed
install_dependencies() {
    log_info "Checking npm dependencies..."
    
    if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
        log_warning "node_modules not found, installing dependencies..."
        cd "$PROJECT_ROOT"
        npm install
        log_success "Dependencies installed"
    else
        log_success "Dependencies already installed"
    fi
}

# Run Jest tests
run_jest_tests() {
    local test_type="$1"
    local jest_opts="$2"
    
    log_info "Running $test_type tests..."
    
    cd "$PROJECT_ROOT"
    
    # Build Jest command
    local cmd="npx jest --config $JEST_CONFIG"
    
    # Add test path pattern if specified
    if [ -n "$test_type" ] && [ "$test_type" != "all" ]; then
        cmd="$cmd --testPathPattern=tests/frontend/$test_type"
    fi
    
    # Add additional options
    if [ -n "$jest_opts" ]; then
        cmd="$cmd $jest_opts"
    fi
    
    log_info "Command: $cmd"
    
    # Run Jest
    if eval "$cmd"; then
        log_success "$test_type tests completed successfully"
        return 0
    else
        log_error "$test_type tests failed"
        return 1
    fi
}

# Show coverage report
show_coverage() {
    if [ -d "$PROJECT_ROOT/$COVERAGE_DIR" ]; then
        log_info "Coverage report available at: $COVERAGE_DIR/index.html"
        
        # Show summary if available
        if [ -f "$PROJECT_ROOT/$COVERAGE_DIR/coverage-summary.json" ]; then
            log_info "Coverage summary:"
            cat "$PROJECT_ROOT/$COVERAGE_DIR/coverage-summary.json" | grep -E '"total"' -A 10
        fi
    fi
}

# Main execution
main() {
    local test_type="${1:-all}"
    local coverage="${2:-false}"
    local watch="${3:-false}"
    local exit_code=0
    
    log_info "SEIM Frontend Test Runner"
    log_info "========================"
    log_info "Test type: $test_type"
    log_info "Coverage: $coverage"
    log_info "Watch mode: $watch"
    log_info "Project root: $PROJECT_ROOT"
    
    # Check environment
    if ! check_node_environment; then
        exit 1
    fi
    
    if ! check_jest_config; then
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Build Jest options
    local jest_opts=""
    if [ "$coverage" = "true" ]; then
        jest_opts="$jest_opts --coverage"
    fi
    
    if [ "$watch" = "true" ]; then
        jest_opts="$jest_opts --watch"
    fi
    
    # Run tests based on type
    case "$test_type" in
        "all")
            log_info "Running all frontend tests..."
            if ! run_jest_tests "all" "$jest_opts"; then
                exit_code=1
            fi
            ;;
        "unit")
            log_info "Running unit tests..."
            if ! run_jest_tests "unit" "$jest_opts"; then
                exit_code=1
            fi
            ;;
        "integration")
            log_info "Running integration tests..."
            if ! run_jest_tests "integration" "$jest_opts"; then
                exit_code=1
            fi
            ;;
        "e2e")
            log_info "Running E2E tests..."
            if ! run_jest_tests "e2e" "$jest_opts"; then
                exit_code=1
            fi
            ;;
        "debug")
            log_info "Running tests in debug mode..."
            if ! run_jest_tests "all" "--runInBand --detectOpenHandles"; then
                exit_code=1
            fi
            ;;
        "ci")
            log_info "Running tests in CI mode..."
            if ! run_jest_tests "all" "--ci --coverage --watchAll=false"; then
                exit_code=1
            fi
            ;;
        *)
            log_error "Unknown test type: $test_type"
            log_info "Available types: all, unit, integration, e2e, debug, ci"
            exit 1
            ;;
    esac
    
    # Show coverage if generated
    if [ "$coverage" = "true" ] || [ "$test_type" = "ci" ]; then
        show_coverage
    fi
    
    if [ $exit_code -eq 0 ]; then
        log_success "All frontend tests completed successfully!"
    else
        log_error "Some frontend tests failed!"
    fi
    
    exit $exit_code
}

# Show help
show_help() {
    echo "SEIM Frontend Test Runner"
    echo "========================"
    echo ""
    echo "Usage: $0 [test_type] [coverage] [watch]"
    echo ""
    echo "Test types:"
    echo "  all          - Run all frontend tests (default)"
    echo "  unit         - Run unit tests only"
    echo "  integration  - Run integration tests only"
    echo "  e2e          - Run E2E tests only"
    echo "  debug        - Run tests in debug mode"
    echo "  ci           - Run tests in CI mode (with coverage)"
    echo ""
    echo "Options:"
    echo "  coverage     - Generate coverage report (true/false, default: false)"
    echo "  watch        - Run tests in watch mode (true/false, default: false)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 unit true         # Run unit tests with coverage"
    echo "  $0 all true true     # Run all tests with coverage and watch mode"
    echo "  $0 ci                # Run CI tests"
    echo ""
    echo "Environment:"
    echo "  Uses jest.config.frontend.js for configuration"
    echo "  Coverage reports saved to coverage/frontend/"
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