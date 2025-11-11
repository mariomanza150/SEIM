#!/bin/bash
set -e

# SEIM Comprehensive Test Runner
# Orchestrates all test types: backend (Docker), frontend (host), Selenium (host)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
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

log_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN} $1${NC}"
    echo -e "${CYAN}================================${NC}"
}

log_section() {
    echo -e "${MAGENTA}--- $1 ---${NC}"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

# Test results tracking
declare -A test_results
declare -A test_durations

# Timer function
start_timer() {
    echo $(date +%s)
}

end_timer() {
    local start_time=$1
    local end_time=$(date +%s)
    echo $((end_time - start_time))
}

# Check if Docker is running
check_docker() {
    log_info "Checking Docker status..."
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running or not accessible"
        log_warning "Please start Docker Desktop or Docker daemon"
        return 1
    fi
    log_success "Docker is running"
    return 0
}

# Check if Docker Compose file exists
check_docker_compose() {
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        return 1
    fi
    log_success "Docker Compose file found"
    return 0
}

# Check if Django server is running
check_django_server() {
    log_info "Checking Django server status..."
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        log_success "Django server is running on http://localhost:8000"
        return 0
    else
        log_warning "Django server is not running on http://localhost:8000"
        log_info "This is required for Selenium tests"
        return 1
    fi
}

# Run backend tests (Docker)
run_backend_tests() {
    local test_type="$1"
    local start_time=$(start_timer)
    
    log_section "Running Backend Tests ($test_type)"
    
    case "$test_type" in
        "all")
            log_info "Running all backend tests..."
            if docker-compose exec -T web pytest; then
                test_results["backend"]="passed"
                log_success "Backend tests passed"
            else
                test_results["backend"]="failed"
                log_error "Backend tests failed"
                return 1
            fi
            ;;
        "unit")
            log_info "Running unit tests..."
            if docker-compose exec -T web pytest tests/unit/ -v; then
                test_results["backend_unit"]="passed"
                log_success "Unit tests passed"
            else
                test_results["backend_unit"]="failed"
                log_error "Unit tests failed"
                return 1
            fi
            ;;
        "integration")
            log_info "Running integration tests..."
            if docker-compose exec -T web pytest tests/integration/ -v; then
                test_results["backend_integration"]="passed"
                log_success "Integration tests passed"
            else
                test_results["backend_integration"]="failed"
                log_error "Integration tests failed"
                return 1
            fi
            ;;
        "api")
            log_info "Running API tests..."
            if docker-compose exec -T web pytest -m api -v; then
                test_results["backend_api"]="passed"
                log_success "API tests passed"
            else
                test_results["backend_api"]="failed"
                log_error "API tests failed"
                return 1
            fi
            ;;
        "coverage")
            log_info "Running tests with coverage..."
            if docker-compose exec -T web pytest --cov=. --cov-report=html:htmlcov --cov-report=term-missing; then
                test_results["backend_coverage"]="passed"
                log_success "Coverage tests passed"
            else
                test_results["backend_coverage"]="failed"
                log_error "Coverage tests failed"
                return 1
            fi
            ;;
        *)
            log_error "Unknown backend test type: $test_type"
            return 1
            ;;
    esac
    
    test_durations["backend_$test_type"]=$(end_timer $start_time)
    return 0
}

# Run frontend tests (host OS)
run_frontend_tests() {
    local test_type="$1"
    local start_time=$(start_timer)
    
    log_section "Running Frontend Tests ($test_type)"
    
    # Use the frontend test script
    if ./scripts/test_frontend.sh "$test_type"; then
        test_results["frontend_$test_type"]="passed"
        log_success "Frontend tests ($test_type) passed"
    else
        test_results["frontend_$test_type"]="failed"
        log_error "Frontend tests ($test_type) failed"
        return 1
    fi
    
    test_durations["frontend_$test_type"]=$(end_timer $start_time)
    return 0
}

# Run Selenium tests (host OS)
run_selenium_tests() {
    local test_type="$1"
    local start_time=$(start_timer)
    
    log_section "Running Selenium Tests ($test_type)"
    
    # Check if Django server is running for Selenium tests
    if ! check_django_server; then
        log_warning "Skipping Selenium tests - Django server not running"
        test_results["selenium_$test_type"]="skipped"
        test_durations["selenium_$test_type"]=0
        return 0
    fi
    
    # Use the Selenium test script
    if ./scripts/test_selenium.sh "$test_type"; then
        test_results["selenium_$test_type"]="passed"
        log_success "Selenium tests ($test_type) passed"
    else
        test_results["selenium_$test_type"]="failed"
        log_error "Selenium tests ($test_type) failed"
        return 1
    fi
    
    test_durations["selenium_$test_type"]=$(end_timer $start_time)
    return 0
}

# Generate test report
generate_report() {
    log_header "Test Execution Report"
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    local skipped_tests=0
    local total_duration=0
    
    echo ""
    echo "Test Results:"
    echo "============="
    
    for test_name in "${!test_results[@]}"; do
        local result="${test_results[$test_name]}"
        local duration="${test_durations[$test_name]:-0}"
        
        case "$result" in
            "passed")
                echo -e "✅ $test_name (${duration}s)"
                ((passed_tests++))
                ;;
            "failed")
                echo -e "❌ $test_name (${duration}s)"
                ((failed_tests++))
                ;;
            "skipped")
                echo -e "⏭️  $test_name (skipped)"
                ((skipped_tests++))
                ;;
        esac
        
        ((total_tests++))
        total_duration=$((total_duration + duration))
    done
    
    echo ""
    echo "Summary:"
    echo "========"
    echo "Total tests: $total_tests"
    echo -e "Passed: ${GREEN}$passed_tests${NC}"
    echo -e "Failed: ${RED}$failed_tests${NC}"
    echo -e "Skipped: ${YELLOW}$skipped_tests${NC}"
    echo "Total duration: ${total_duration}s"
    
    # Save report to file
    local report_file="$PROJECT_ROOT/test-report-$(date +%Y%m%d-%H%M%S).txt"
    {
        echo "SEIM Test Execution Report"
        echo "Generated: $(date)"
        echo ""
        echo "Test Results:"
        echo "============="
        for test_name in "${!test_results[@]}"; do
            local result="${test_results[$test_name]}"
            local duration="${test_durations[$test_name]:-0}"
            echo "$test_name: $result (${duration}s)"
        done
        echo ""
        echo "Summary:"
        echo "========"
        echo "Total tests: $total_tests"
        echo "Passed: $passed_tests"
        echo "Failed: $failed_tests"
        echo "Skipped: $skipped_tests"
        echo "Total duration: ${total_duration}s"
    } > "$report_file"
    
    log_success "Test report saved to: $report_file"
    
    # Return exit code based on failures
    if [ $failed_tests -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

# Main execution
main() {
    local test_suite="${1:-all}"
    local backend_type="${2:-all}"
    local frontend_type="${3:-all}"
    local selenium_type="${4:-all}"
    
    log_header "SEIM Comprehensive Test Runner"
    log_info "Test suite: $test_suite"
    log_info "Backend tests: $backend_type"
    log_info "Frontend tests: $frontend_type"
    log_info "Selenium tests: $selenium_type"
    
    local exit_code=0
    
    # Check Docker environment for backend tests
    if [[ "$test_suite" =~ ^(all|backend) ]]; then
        if ! check_docker; then
            log_error "Cannot run backend tests without Docker"
            exit 1
        fi
        
        if ! check_docker_compose; then
            log_error "Cannot run backend tests without Docker Compose"
            exit 1
        fi
    fi
    
    # Run tests based on suite
    case "$test_suite" in
        "all")
            # Run all test types
            if ! run_backend_tests "$backend_type"; then
                exit_code=1
            fi
            
            if ! run_frontend_tests "$frontend_type"; then
                exit_code=1
            fi
            
            if ! run_selenium_tests "$selenium_type"; then
                exit_code=1
            fi
            ;;
        "backend")
            if ! run_backend_tests "$backend_type"; then
                exit_code=1
            fi
            ;;
        "frontend")
            if ! run_frontend_tests "$frontend_type"; then
                exit_code=1
            fi
            ;;
        "selenium")
            if ! run_selenium_tests "$selenium_type"; then
                exit_code=1
            fi
            ;;
        "quick")
            # Quick test suite - unit tests only
            if ! run_backend_tests "unit"; then
                exit_code=1
            fi
            
            if ! run_frontend_tests "unit"; then
                exit_code=1
            fi
            ;;
        "ci")
            # CI test suite - comprehensive with coverage
            if ! run_backend_tests "coverage"; then
                exit_code=1
            fi
            
            if ! run_frontend_tests "ci"; then
                exit_code=1
            fi
            
            if ! run_selenium_tests "all"; then
                exit_code=1
            fi
            ;;
        *)
            log_error "Unknown test suite: $test_suite"
            log_info "Available suites: all, backend, frontend, selenium, quick, ci"
            exit 1
            ;;
    esac
    
    # Generate report
    generate_report
    
    if [ $exit_code -eq 0 ]; then
        log_success "All tests completed successfully!"
    else
        log_error "Some tests failed!"
    fi
    
    exit $exit_code
}

# Show help
show_help() {
    echo "SEIM Comprehensive Test Runner"
    echo "=============================="
    echo ""
    echo "Usage: $0 [test_suite] [backend_type] [frontend_type] [selenium_type]"
    echo ""
    echo "Test suites:"
    echo "  all       - Run all test types (default)"
    echo "  backend   - Run backend tests only"
    echo "  frontend  - Run frontend tests only"
    echo "  selenium  - Run Selenium tests only"
    echo "  quick     - Run quick test suite (unit tests only)"
    echo "  ci        - Run CI test suite (comprehensive with coverage)"
    echo ""
    echo "Backend test types:"
    echo "  all        - All backend tests (default)"
    echo "  unit       - Unit tests only"
    echo "  integration - Integration tests only"
    echo "  api        - API tests only"
    echo "  coverage   - Tests with coverage"
    echo ""
    echo "Frontend test types:"
    echo "  all        - All frontend tests (default)"
    echo "  unit       - Unit tests only"
    echo "  integration - Integration tests only"
    echo "  e2e        - E2E tests only"
    echo "  ci         - CI mode with coverage"
    echo ""
    echo "Selenium test types:"
    echo "  all        - All Selenium tests (default)"
    echo "  e2e        - E2E tests only"
    echo "  selenium   - Core functionality tests"
    echo "  standalone - Standalone tests"
    echo "  setup      - Setup verification"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests"
    echo "  $0 quick                             # Run quick test suite"
    echo "  $0 backend unit                      # Run backend unit tests only"
    echo "  $0 frontend unit                     # Run frontend unit tests only"
    echo "  $0 selenium e2e                      # Run Selenium E2E tests only"
    echo "  $0 ci                                # Run CI test suite"
    echo ""
    echo "Environment requirements:"
    echo "  - Docker and Docker Compose for backend tests"
    echo "  - Node.js and npm for frontend tests"
    echo "  - Python with selenium/webdriver-manager for Selenium tests"
    echo "  - Django server running for Selenium tests"
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