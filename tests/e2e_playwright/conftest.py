"""
Shared fixtures and configuration for Playwright E2E tests.

This module provides fixtures for authenticated contexts, database seeding,
screenshot management, and test data setup.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

# Note: Django imports removed for E2E tests
# E2E tests should interact with the application via HTTP/API, not direct ORM
# This avoids async/sync conflicts and better represents real user interactions

# Base configuration
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
DEFAULT_BROWSER = os.environ.get("BROWSER", "chromium")
HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"

# Browser configuration
BROWSER_CONFIG = {
    "headless": HEADLESS,
    "slow_mo": int(os.environ.get("SLOWMO", 0)),
}

# Context configuration
CONTEXT_CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
    "ignore_https_errors": True,
}

# Test data configuration
TEST_DATA_CONFIG = {
    "users": {
        "admin": {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123"
        },
        "coordinator": {
            "username": "coordinator",
            "email": "coordinator@example.com",
            "password": "coord123"
        },
        "student1": {
            "username": "student1",
            "email": "student1@example.com",
            "password": "student123"
        }
    }
}

def get_browser_config():
    return BROWSER_CONFIG.copy()

def get_context_config():
    return CONTEXT_CONFIG.copy()

def get_mobile_context_config():
    return {
        "viewport": {"width": 375, "height": 667},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        "is_mobile": True,
        "has_touch": True,
    }


# ============================================================================
# Session-scoped fixtures
# ============================================================================

@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up test database with initial data."""
    with django_db_blocker.unblock():
        # Create roles
        for role_name in ['student', 'coordinator', 'admin']:
            Role.objects.get_or_create(name=role_name)
        
        # Create application statuses
        statuses = ['draft', 'submitted', 'under_review', 'approved', 'rejected', 'completed', 'cancelled']
        for i, status_name in enumerate(statuses):
            ApplicationStatus.objects.get_or_create(name=status_name, defaults={'order': i})
        
        # Load test data
        call_command('create_test_users')
        call_command('populate_test_data')


@pytest.fixture(scope="session")
def browser_type_launch_args() -> Dict[str, Any]:
    """Browser launch arguments."""
    return get_browser_config()


@pytest.fixture(scope="session")
def browser_context_args() -> Dict[str, Any]:
    """Browser context arguments."""
    return get_context_config()


# ============================================================================
# Function-scoped fixtures
# ============================================================================

# Note: base_url is provided by pytest-base-url plugin, configured via BASE_URL constant


@pytest.fixture
def context(browser: Browser, request) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    config = get_context_config()
    
    # Enable video recording for video_demo tests
    video_demo_markers = [mark.name for mark in request.node.iter_markers()]
    videos_dir = None
    if "video_demo" in video_demo_markers:
        # Create videos directory if it doesn't exist
        videos_dir = Path("tests/e2e_playwright/videos")
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Enable video recording - Playwright Python API
        # record_video_dir should be a string path
        config["record_video_dir"] = str(videos_dir)
        # record_video_size is optional but recommended
        if "record_video_size" not in config:
            config["record_video_size"] = {"width": 1280, "height": 720}
    
    context = browser.new_context(**config)
    yield context
    
    # Video is automatically saved by Playwright when context closes
    if "video_demo" in video_demo_markers and videos_dir:
        test_name = request.node.name.replace("[", "_").replace("]", "").replace("::", "_")
        print(f"📹 Video recording enabled for: {test_name}")
        print(f"   Videos will be saved to: {videos_dir}")
    
    context.close()
    
    # Rename video file to match test name for better organization
    if "video_demo" in video_demo_markers and videos_dir:
        # Get the most recently created video file (should be the one just saved)
        video_files = list(videos_dir.glob("*.webm"))
        if video_files:
            # Sort by modification time, most recent first
            video_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            latest_video = video_files[0]
            
            # Create human-readable name from test name
            # Extract demo number and description from test name
            test_name_clean = test_name.replace("test_", "").replace("TestStudentVideoDemos_", "").replace("TestCoordinatorVideoDemos_", "").replace("TestAdminVideoDemos_", "").replace("TestCrossRoleVideoDemos_", "")
            
            # If it matches the pattern demo_X_description, use it directly
            if test_name_clean.startswith("demo_"):
                new_name = f"{test_name_clean}.webm"
            else:
                # Otherwise, create a sanitized version
                new_name = f"{test_name_clean}.webm"
            
            new_path = videos_dir / new_name
            
            # Only rename if the new name is different and doesn't already exist
            if latest_video.name != new_name and not new_path.exists():
                try:
                    latest_video.rename(new_path)
                    print(f"   ✓ Video renamed to: {new_name}")
                except Exception as e:
                    print(f"   ⚠️  Could not rename video: {e}")


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


# ============================================================================
# Authentication fixtures
# ============================================================================

@pytest.fixture
def login_as_student(page: Page, base_url: str) -> Generator[Page, None, None]:
    """Login as a student user."""
    from tests.e2e_playwright.utils.auth_helpers import login
    credentials = TEST_DATA_CONFIG['users']['student1']
    login(page, base_url, credentials['username'], credentials['password'])
    yield page


@pytest.fixture
def login_as_coordinator(page: Page, base_url: str) -> Generator[Page, None, None]:
    """Login as a coordinator user."""
    from tests.e2e_playwright.utils.auth_helpers import login
    credentials = TEST_DATA_CONFIG['users']['coordinator']
    login(page, base_url, credentials['username'], credentials['password'])
    yield page


@pytest.fixture
def login_as_admin(page: Page, base_url: str) -> Generator[Page, None, None]:
    """Login as an admin user."""
    from tests.e2e_playwright.utils.auth_helpers import login
    credentials = TEST_DATA_CONFIG['users']['admin']
    login(page, base_url, credentials['username'], credentials['password'])
    yield page


@pytest.fixture
def authenticated_student_context(browser: Browser, base_url: str) -> Generator[BrowserContext, None, None]:
    """Create an authenticated context as a student."""
    from tests.e2e_playwright.utils.auth_helpers import create_authenticated_context
    credentials = TEST_DATA_CONFIG['users']['student1']
    context = create_authenticated_context(
        browser, 
        base_url, 
        credentials['username'], 
        credentials['password']
    )
    yield context
    context.close()


@pytest.fixture
def authenticated_coordinator_context(browser: Browser, base_url: str) -> Generator[BrowserContext, None, None]:
    """Create an authenticated context as a coordinator."""
    from tests.e2e_playwright.utils.auth_helpers import create_authenticated_context
    credentials = TEST_DATA_CONFIG['users']['coordinator']
    context = create_authenticated_context(
        browser, 
        base_url, 
        credentials['username'], 
        credentials['password']
    )
    yield context
    context.close()


@pytest.fixture
def authenticated_admin_context(browser: Browser, base_url: str) -> Generator[BrowserContext, None, None]:
    """Create an authenticated context as an admin."""
    from tests.e2e_playwright.utils.auth_helpers import create_authenticated_context
    credentials = TEST_DATA_CONFIG['users']['admin']
    context = create_authenticated_context(
        browser, 
        base_url, 
        credentials['username'], 
        credentials['password']
    )
    yield context
    context.close()


# ============================================================================
# Screenshot and visual regression fixtures
# ============================================================================

@pytest.fixture
def screenshot_on_failure(request: pytest.FixtureRequest, page: Page):
    """Automatically take screenshot on test failure."""
    yield
    if request.node.rep_call.failed:
        test_name = request.node.nodeid.replace("::", "_").replace("/", "_")
        screenshot_dir = Path(SCREENSHOT_CONFIG['path'])
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"{test_name}_failure.png"
        page.screenshot(path=str(screenshot_path), full_page=SCREENSHOT_CONFIG['full_page'])
        print(f"\nScreenshot saved to: {screenshot_path}")


@pytest.fixture
def take_screenshot(page: Page):
    """Fixture to manually take screenshots during tests."""
    def _take_screenshot(name: str, full_page: bool = True):
        screenshot_dir = Path(SCREENSHOT_CONFIG['path'])
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"{name}.png"
        page.screenshot(path=str(screenshot_path), full_page=full_page)
        return screenshot_path
    
    return _take_screenshot


@pytest.fixture
def assert_visual_match(page: Page):
    """Fixture for visual regression testing."""
    from tests.e2e_playwright.utils.visual_regression import compare_screenshot
    
    def _assert_visual_match(name: str, threshold: float = None):
        """Compare current page with baseline screenshot."""
        threshold = threshold or VISUAL_REGRESSION_CONFIG['threshold']
        baseline_dir = Path(VISUAL_REGRESSION_CONFIG['baseline_dir'])
        baseline_dir.mkdir(parents=True, exist_ok=True)
        
        baseline_path = baseline_dir / f"{name}.png"
        
        # Take current screenshot
        current_screenshot = page.screenshot()
        
        # Compare or create baseline
        if VISUAL_REGRESSION_CONFIG['update_baseline'] or not baseline_path.exists():
            baseline_path.write_bytes(current_screenshot)
            return True
        
        return compare_screenshot(
            current_screenshot,
            baseline_path.read_bytes(),
            name,
            threshold
        )
    
    return _assert_visual_match


# ============================================================================
# Mobile device fixtures
# ============================================================================

@pytest.fixture
def mobile_page(browser: Browser) -> Generator[Page, None, None]:
    """Create a mobile browser context."""
    context = browser.new_context(**get_mobile_context_config('iPhone 12'))
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def tablet_page(browser: Browser) -> Generator[Page, None, None]:
    """Create a tablet browser context."""
    context = browser.new_context(**get_mobile_context_config('iPad Pro'))
    page = context.new_page()
    yield page
    context.close()


# ============================================================================
# Test data fixtures
# ============================================================================

@pytest.fixture
def test_users() -> Dict[str, Dict[str, str]]:
    """Get test user credentials."""
    return TEST_DATA_CONFIG['users']


@pytest.fixture
def sample_program(db):
    """Create a sample program for testing."""
    program, created = Program.objects.get_or_create(
        name="Test Exchange Program",
        defaults={
            'description': 'A test exchange program for E2E testing',
            'is_active': True,
            'min_gpa': 3.0,
            'required_language': 'English',
        }
    )
    return program


# ============================================================================
# Pytest hooks
# ============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make test result available to fixtures."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_configure(config):
    """Configure pytest for E2E tests."""
    # Create output directories
    for directory in [
        'tests/e2e_playwright/screenshots',
        'tests/e2e_playwright/videos',
        'tests/e2e_playwright/reports',
        'tests/e2e_playwright/visual/snapshots',
        'tests/e2e_playwright/visual/diffs',
        'tests/e2e_playwright/visual/reports',
    ]:
        Path(directory).mkdir(parents=True, exist_ok=True)


def pytest_addoption(parser):
    """Add custom command-line options."""
    # Note: --headed, --browser, --slowmo are provided by pytest-playwright
    # Only add custom options that don't conflict
    parser.addoption(
        "--update-baseline",
        action="store_true",
        default=False,
        help="Update visual regression baselines"
    )

