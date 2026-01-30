"""
Playwright configuration for SEIM E2E tests.

This configuration supports both Docker and host machine execution,
with parallel test execution, screenshots, and video recording.
"""

import os
from typing import Any, Dict

# Detect execution environment
IS_DOCKER = os.environ.get('DOCKER_ENV', 'false').lower() == 'true'
BASE_URL = os.environ.get('BASE_URL', 'http://web:8000' if IS_DOCKER else 'http://localhost:8000')

# Browser configuration
BROWSERS = ['chromium', 'firefox', 'webkit']
DEFAULT_BROWSER = 'chromium'

# Timeout configuration (in milliseconds)
TIMEOUTS = {
    'default': 30000,  # 30 seconds
    'navigation': 30000,
    'action': 10000,
}

# Screenshot configuration
SCREENSHOT_CONFIG = {
    'only_on_failure': True,
    'full_page': True,
    'path': 'tests/e2e_playwright/screenshots',
}

# Video configuration
VIDEO_CONFIG = {
    'enabled': os.environ.get('RECORD_VIDEO', 'on_failure'),  # 'on', 'off', 'on_failure'
    'path': 'tests/e2e_playwright/videos',
    'size': {'width': 1920, 'height': 1080},
}

# Parallel execution configuration
PARALLEL_CONFIG = {
    'workers': int(os.environ.get('WORKERS', os.cpu_count() or 4)),
    'max_failures': int(os.environ.get('MAX_FAILURES', 10)),
}

# Retry configuration
RETRY_CONFIG = {
    'retries': int(os.environ.get('RETRIES', 2)),
    'retry_on_timeout': True,
}

# Browser launch configuration
BROWSER_CONFIG: Dict[str, Any] = {
    'headless': os.environ.get('HEADLESS', 'true').lower() == 'true',
    'slow_mo': int(os.environ.get('SLOWMO', 0)),  # Slow down actions (for debugging)
    'args': [
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
    ],
}

# Context configuration
CONTEXT_CONFIG: Dict[str, Any] = {
    'viewport': {'width': 1920, 'height': 1080},
    'ignore_https_errors': True,
    'record_video_dir': VIDEO_CONFIG['path'] if VIDEO_CONFIG['enabled'] != 'off' else None,
    'record_video_size': VIDEO_CONFIG['size'],
}

# Visual regression configuration
VISUAL_REGRESSION_CONFIG = {
    'threshold': float(os.environ.get('VISUAL_THRESHOLD', 0.1)),  # 10% difference allowed
    'baseline_dir': 'tests/e2e_playwright/visual/snapshots',
    'diff_dir': 'tests/e2e_playwright/visual/diffs',
    'update_baseline': os.environ.get('UPDATE_BASELINE', 'false').lower() == 'true',
}

# Test data configuration
TEST_DATA_CONFIG = {
    'users': {
        'admin': {'username': 'admin', 'password': 'admin123'},
        'coordinator': {'username': 'coordinator', 'password': 'coord123'},
        'student1': {'username': 'student1', 'password': 'student123'},
        'student2': {'username': 'student2', 'password': 'student123'},
    },
}


def get_browser_config(browser_name: str = DEFAULT_BROWSER) -> Dict[str, Any]:
    """Get browser-specific configuration."""
    config = BROWSER_CONFIG.copy()
    
    # Browser-specific overrides
    if browser_name == 'firefox':
        config['args'].append('--disable-gpu')
    elif browser_name == 'webkit':
        # WebKit doesn't support some chromium args
        config['args'] = []
    
    return config


def get_context_config(**overrides) -> Dict[str, Any]:
    """Get browser context configuration with optional overrides."""
    config = CONTEXT_CONFIG.copy()
    config.update(overrides)
    return config


def get_mobile_context_config(device: str = 'iPhone 12') -> Dict[str, Any]:
    """Get mobile device context configuration."""
    mobile_devices = {
        'iPhone 12': {
            'viewport': {'width': 390, 'height': 844},
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'has_touch': True,
            'is_mobile': True,
        },
        'iPad Pro': {
            'viewport': {'width': 1024, 'height': 1366},
            'user_agent': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'has_touch': True,
            'is_mobile': True,
        },
        'Samsung Galaxy S21': {
            'viewport': {'width': 360, 'height': 800},
            'user_agent': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36',
            'has_touch': True,
            'is_mobile': True,
        },
    }
    
    device_config = mobile_devices.get(device, mobile_devices['iPhone 12'])
    config = CONTEXT_CONFIG.copy()
    config.update(device_config)
    return config

