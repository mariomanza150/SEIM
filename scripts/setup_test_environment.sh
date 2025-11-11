#!/bin/bash
set -e

# SEIM Test Environment Setup
# Sets up the environment for running all test types

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

log_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_header "SEIM Test Environment Setup"

# Check and setup Docker environment
setup_docker() {
    log_info "Setting up Docker environment for backend tests..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is not installed"
        log_warning "Please install Docker Desktop from https://www.docker.com/products/docker-desktop/"
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running"
        log_warning "Please start Docker Desktop or Docker daemon"
        return 1
    fi
    
    log_success "Docker is available"
    
    # Check if .env file exists
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning ".env file not found, creating from template..."
        if [ -f "$PROJECT_ROOT/env.example" ]; then
            cp "$PROJECT_ROOT/env.example" "$PROJECT_ROOT/.env"
            log_success ".env file created from template"
        else
            log_error "env.example template not found"
            return 1
        fi
    fi
    
    # Start Docker services
    log_info "Starting Docker services..."
    cd "$PROJECT_ROOT"
    if docker-compose up -d; then
        log_success "Docker services started"
    else
        log_error "Failed to start Docker services"
        return 1
    fi
    
    return 0
}

# Check and setup Node.js environment
setup_node() {
    log_info "Setting up Node.js environment for frontend tests..."
    
    if ! command -v node >/dev/null 2>&1; then
        log_error "Node.js is not installed"
        log_warning "Please install Node.js from https://nodejs.org/"
        return 1
    fi
    
    if ! command -v npm >/dev/null 2>&1; then
        log_error "npm is not installed"
        log_warning "Please install npm"
        return 1
    fi
    
    log_success "Node.js $(node --version) and npm $(npm --version) are available"
    
    # Install npm dependencies
    log_info "Installing npm dependencies..."
    cd "$PROJECT_ROOT"
    if npm install; then
        log_success "npm dependencies installed"
    else
        log_error "Failed to install npm dependencies"
        return 1
    fi
    
    return 0
}

# Check and setup Python environment for Selenium
setup_python() {
    log_info "Setting up Python environment for Selenium tests..."
    
    if ! command -v python >/dev/null 2>&1; then
        log_error "Python is not installed"
        log_warning "Please install Python 3.8+ from https://www.python.org/"
        return 1
    fi
    
    log_success "Python $(python --version) is available"
    
    # Install Python dependencies for Selenium
    log_info "Installing Python dependencies for Selenium..."
    local selenium_deps=("selenium" "webdriver-manager" "pytest-selenium" "requests")
    
    for dep in "${selenium_deps[@]}"; do
        if ! python -c "import ${dep//-/_}" 2>/dev/null; then
            log_info "Installing $dep..."
            if pip install "$dep"; then
                log_success "$dep installed"
            else
                log_error "Failed to install $dep"
                return 1
            fi
        else
            log_success "$dep already installed"
        fi
    done
    
    return 0
}

# Check Chrome browser
check_chrome() {
    log_info "Checking Chrome browser installation..."
    
    local system=$(uname -s | tr '[:upper:]' '[:lower:]')
    local chrome_found=false
    
    case "$system" in
        "darwin")  # macOS
            if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
                chrome_found=true
            fi
            ;;
        "linux")
            if command -v google-chrome >/dev/null 2>&1 || command -v google-chrome-stable >/dev/null 2>&1; then
                chrome_found=true
            fi
            ;;
        "msys"*|"cygwin"*|"mingw"*)  # Windows
            if [ -f "/c/Program Files/Google/Chrome/Application/chrome.exe" ] || [ -f "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" ]; then
                chrome_found=true
            fi
            ;;
    esac
    
    if [ "$chrome_found" = true ]; then
        log_success "Chrome browser found"
    else
        log_warning "Chrome browser not found"
        log_info "Please install Chrome browser for Selenium tests:"
        log_info "  https://www.google.com/chrome/"
    fi
    
    return 0
}

# Test the setup
test_setup() {
    log_info "Testing the setup..."
    
    local all_good=true
    
    # Test Docker
    if docker info >/dev/null 2>&1; then
        log_success "Docker: OK"
    else
        log_error "Docker: FAILED"
        all_good=false
    fi
    
    # Test Node.js
    if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
        log_success "Node.js: OK"
    else
        log_error "Node.js: FAILED"
        all_good=false
    fi
    
    # Test Python
    if command -v python >/dev/null 2>&1; then
        log_success "Python: OK"
    else
        log_error "Python: FAILED"
        all_good=false
    fi
    
    # Test Selenium dependencies
    if python -c "import selenium, webdriver_manager" 2>/dev/null; then
        log_success "Selenium dependencies: OK"
    else
        log_error "Selenium dependencies: FAILED"
        all_good=false
    fi
    
    if [ "$all_good" = true ]; then
        log_success "All components are ready!"
        return 0
    else
        log_error "Some components are not ready"
        return 1
    fi
}

# Show next steps
show_next_steps() {
    log_header "Setup Complete!"
    echo ""
    echo "Next steps:"
    echo "==========="
    echo ""
    echo "1. Start Django server:"
    echo "   docker-compose up web"
    echo ""
    echo "2. Run tests:"
    echo "   make test-quick          # Quick test suite"
    echo "   make test-frontend       # Frontend tests"
    echo "   make test-selenium       # Selenium tests"
    echo "   make test-all            # All tests"
    echo ""
    echo "3. Or use the comprehensive test runner:"
    echo "   ./scripts/run_tests.sh all"
    echo ""
    echo "4. For development:"
    echo "   make dev-workflow        # Complete development setup"
    echo ""
    echo "Documentation:"
    echo "============="
    echo "  - Testing guide: documentation/testing.md"
    echo "  - Development guide: documentation/developer_guide.md"
    echo ""
}

# Main execution
main() {
    local setup_docker_result=0
    local setup_node_result=0
    local setup_python_result=0
    
    # Setup Docker
    if setup_docker; then
        setup_docker_result=0
    else
        setup_docker_result=1
        log_warning "Docker setup failed, backend tests will not work"
    fi
    
    # Setup Node.js
    if setup_node; then
        setup_node_result=0
    else
        setup_node_result=1
        log_warning "Node.js setup failed, frontend tests will not work"
    fi
    
    # Setup Python
    if setup_python; then
        setup_python_result=0
    else
        setup_python_result=1
        log_warning "Python setup failed, Selenium tests will not work"
    fi
    
    # Check Chrome
    check_chrome
    
    # Test the setup
    if test_setup; then
        log_success "Test environment setup completed successfully!"
    else
        log_warning "Test environment setup completed with some issues"
    fi
    
    # Show next steps
    show_next_steps
    
    # Return appropriate exit code
    if [ $setup_docker_result -eq 0 ] && [ $setup_node_result -eq 0 ] && [ $setup_python_result -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Show help
show_help() {
    echo "SEIM Test Environment Setup"
    echo "==========================="
    echo ""
    echo "This script sets up the environment for running all SEIM tests:"
    echo "  - Backend tests (Docker)"
    echo "  - Frontend tests (Node.js/Jest)"
    echo "  - Selenium tests (Python/Chrome)"
    echo ""
    echo "Usage: $0"
    echo ""
    echo "The script will:"
    echo "  1. Check and setup Docker environment"
    echo "  2. Check and setup Node.js environment"
    echo "  3. Check and setup Python environment"
    echo "  4. Install required dependencies"
    echo "  5. Test the setup"
    echo ""
    echo "Requirements:"
    echo "  - Docker Desktop or Docker daemon"
    echo "  - Node.js 14+ and npm"
    echo "  - Python 3.8+ and pip"
    echo "  - Chrome browser (for Selenium tests)"
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