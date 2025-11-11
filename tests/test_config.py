"""
Test configuration and utilities for SEIM.

This module provides centralized test configuration, utilities for test management,
and common test patterns that can be used across all test modules.
"""

import os

from django.conf import settings
from django.test import override_settings

# Test configuration constants
TEST_CONFIG = {
    "DATABASE": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "CACHE": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "EMAIL": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
    "CELERY": {
        "TASK_ALWAYS_EAGER": True,
        "TASK_EAGER_PROPAGATES": True,
        "BROKER_URL": "memory://",
    },
    "MEDIA": {
        "ROOT": "/tmp/seim_test_media",
        "STORAGE": "django.core.files.storage.FileSystemStorage",
    },
    "STATIC": {
        "ROOT": "/tmp/seim_test_static",
        "STORAGE": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "SECURITY": {
        "PASSWORD_HASHERS": [
            "django.contrib.auth.hashers.MD5PasswordHasher",
        ],
        "CSRF_COOKIE_SECURE": False,
        "SESSION_COOKIE_SECURE": False,
    },
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "null": {
                "class": "logging.NullHandler",
            },
        },
        "root": {
            "handlers": ["null"],
        },
    },
}


# Test markers configuration
pytest_plugins = []


# Test settings override decorator
def test_settings(**kwargs):
    """Decorator to override test settings."""

    def decorator(func):
        return override_settings(**kwargs)(func)

    return decorator


# Test database configuration
def configure_test_database():
    """Configure test database settings."""
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "OPTIONS": {
                "timeout": 20,
            },
        }
    }


# Test cache configuration
def configure_test_cache():
    """Configure test cache settings."""
    return {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
        "sessions": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
        "api": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
        "analytics": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
    }


# Test email configuration
def configure_test_email():
    """Configure test email settings."""
    return {
        "EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
        "EMAIL_HOST": "localhost",
        "EMAIL_PORT": 1025,
        "EMAIL_USE_TLS": False,
        "EMAIL_HOST_USER": "",
        "EMAIL_HOST_PASSWORD": "",
    }


# Test Celery configuration
def configure_test_celery():
    """Configure test Celery settings."""
    return {
        "CELERY_TASK_ALWAYS_EAGER": True,
        "CELERY_TASK_EAGER_PROPAGATES": True,
        "CELERY_BROKER_URL": "memory://",
        "CELERY_RESULT_BACKEND": "memory://",
    }


# Test file storage configuration
def configure_test_storage():
    """Configure test file storage settings."""
    import tempfile

    media_root = tempfile.mkdtemp(prefix="seim_test_media_")
    static_root = tempfile.mkdtemp(prefix="seim_test_static_")

    return {
        "MEDIA_ROOT": media_root,
        "STATIC_ROOT": static_root,
        "MEDIA_URL": "/media/",
        "STATIC_URL": "/static/",
        "DEFAULT_FILE_STORAGE": "django.core.files.storage.FileSystemStorage",
        "STATICFILES_STORAGE": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }


# Test security configuration
def configure_test_security():
    """Configure test security settings."""
    return {
        "PASSWORD_HASHERS": [
            "django.contrib.auth.hashers.MD5PasswordHasher",
        ],
        "CSRF_COOKIE_SECURE": False,
        "SESSION_COOKIE_SECURE": False,
        "SECURE_SSL_REDIRECT": False,
        "SECURE_BROWSER_XSS_FILTER": False,
        "SECURE_CONTENT_TYPE_NOSNIFF": False,
        "X_FRAME_OPTIONS": "DENY",
    }


# Test logging configuration
def configure_test_logging():
    """Configure test logging settings."""
    return {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "simple": {
                "format": "%(levelname)s %(message)s",
            },
        },
        "handlers": {
            "null": {
                "class": "logging.NullHandler",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
        },
        "root": {
            "handlers": ["null"],
            "level": "CRITICAL",
        },
        "loggers": {
            "django": {
                "handlers": ["null"],
                "level": "CRITICAL",
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["null"],
                "level": "CRITICAL",
                "propagate": False,
            },
        },
    }


# Test performance configuration
def configure_test_performance():
    """Configure test performance settings."""
    return {
        "DEBUG": False,
        "TEMPLATE_DEBUG": False,
        "COMPRESS_ENABLED": False,
        "CACHE_MIDDLEWARE_SECONDS": 0,
        "CACHE_MIDDLEWARE_KEY_PREFIX": "test",
    }


# Test API configuration
def configure_test_api():
    """Configure test API settings."""
    return {
        "REST_FRAMEWORK": {
            "TEST_REQUEST_DEFAULT_FORMAT": "json",
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_THROTTLE_CLASSES": [],
            "DEFAULT_THROTTLE_RATES": {},
        },
        "SIMPLE_JWT": {
            "ACCESS_TOKEN_LIFETIME": "1 day",
            "REFRESH_TOKEN_LIFETIME": "7 days",
            "ROTATE_REFRESH_TOKENS": False,
            "BLACKLIST_AFTER_ROTATION": False,
        },
    }


# Test environment setup
def setup_test_environment():
    """Set up complete test environment."""
    from django.conf import settings

    # Create test directories
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(settings.STATIC_ROOT, exist_ok=True)

    # Configure test settings
    settings.DATABASES = configure_test_database()
    settings.CACHES = configure_test_cache()
    settings.update(configure_test_email())
    settings.update(configure_test_celery())
    settings.update(configure_test_storage())
    settings.update(configure_test_security())
    settings.LOGGING = configure_test_logging()
    settings.update(configure_test_performance())
    settings.update(configure_test_api())


# Test cleanup utilities
def cleanup_test_environment():
    """Clean up test environment."""
    import shutil
    import tempfile

    # Clean up test directories
    test_dirs = [
        settings.MEDIA_ROOT,
        settings.STATIC_ROOT,
        tempfile.gettempdir(),
    ]

    for test_dir in test_dirs:
        if os.path.exists(test_dir) and "seim_test_" in test_dir:
            try:
                shutil.rmtree(test_dir)
            except OSError:
                pass  # Ignore cleanup errors


# Test data utilities
def create_test_data():
    """Create comprehensive test data."""
    from tests.utils import generate_test_data

    return generate_test_data()


# Test assertion utilities
def assert_model_count(model_class, expected_count, **filters):
    """Assert that a model has the expected number of instances."""
    actual_count = model_class.objects.filter(**filters).count()
    assert (
        actual_count == expected_count
    ), f"Expected {expected_count} {model_class.__name__} instances, got {actual_count}"


def assert_response_contains(response, expected_content):
    """Assert that response contains expected content."""
    if hasattr(response, "content"):
        assert expected_content in response.content.decode(
            "utf-8"
        ), f"Response does not contain '{expected_content}'"
    elif hasattr(response, "data"):
        assert expected_content in str(
            response.data
        ), f"Response data does not contain '{expected_content}'"


def assert_response_not_contains(response, unexpected_content):
    """Assert that response does not contain unexpected content."""
    if hasattr(response, "content"):
        assert unexpected_content not in response.content.decode(
            "utf-8"
        ), f"Response contains unexpected '{unexpected_content}'"
    elif hasattr(response, "data"):
        assert unexpected_content not in str(
            response.data
        ), f"Response data contains unexpected '{unexpected_content}'"


# Test performance utilities
def measure_response_time(client, url, method="get", **kwargs):
    """Measure response time for an API call."""
    import time

    start_time = time.time()
    if method.lower() == "get":
        response = client.get(url, **kwargs)
    elif method.lower() == "post":
        response = client.post(url, **kwargs)
    elif method.lower() == "put":
        response = client.put(url, **kwargs)
    elif method.lower() == "patch":
        response = client.patch(url, **kwargs)
    elif method.lower() == "delete":
        response = client.delete(url, **kwargs)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    end_time = time.time()
    response_time = end_time - start_time

    return response, response_time


def assert_response_time_under(response_time, max_time=1.0):
    """Assert that response time is under the maximum allowed time."""
    assert (
        response_time < max_time
    ), f"Response time {response_time}s exceeded limit {max_time}s"


# Test security utilities
def assert_no_sql_injection(client, url, payload, method="post"):
    """Assert that SQL injection attempts are properly handled."""
    response = getattr(client, method.lower())(url, data=payload)

    # Should not return 500 (internal server error)
    assert (
        response.status_code != 500
    ), f"SQL injection vulnerability detected: {payload}"

    # Should either return 400 (bad request) or 403 (forbidden)
    assert response.status_code in [
        400,
        403,
        404,
    ], f"Unexpected response to SQL injection attempt: {response.status_code}"


def assert_no_xss_vulnerability(client, url, payload, method="post"):
    """Assert that XSS attempts are properly handled."""
    response = getattr(client, method.lower())(url, data=payload)

    if response.status_code == 200:
        # If successful, check that payload is not reflected in response
        response_content = response.content.decode("utf-8")
        assert (
            "<script>" not in response_content
        ), f"XSS vulnerability detected: {payload}"
        assert (
            "javascript:" not in response_content.lower()
        ), f"XSS vulnerability detected: {payload}"


# Test configuration for different test types
TEST_CONFIGS = {
    "unit": {
        "description": "Unit tests for individual components",
        "settings": {
            "DEBUG": True,
            "TEMPLATE_DEBUG": True,
        },
        "markers": ["unit"],
    },
    "integration": {
        "description": "Integration tests for cross-module workflows",
        "settings": {
            "DEBUG": False,
            "TEMPLATE_DEBUG": False,
        },
        "markers": ["integration"],
    },
    "api": {
        "description": "API endpoint tests",
        "settings": {
            "DEBUG": False,
            "TEMPLATE_DEBUG": False,
        },
        "markers": ["api"],
    },
    "e2e": {
        "description": "End-to-end browser tests",
        "settings": {
            "DEBUG": False,
            "TEMPLATE_DEBUG": False,
        },
        "markers": ["e2e"],
    },
    "performance": {
        "description": "Performance and load tests",
        "settings": {
            "DEBUG": False,
            "TEMPLATE_DEBUG": False,
            "CACHE_MIDDLEWARE_SECONDS": 300,
        },
        "markers": ["performance"],
    },
    "security": {
        "description": "Security-focused tests",
        "settings": {
            "DEBUG": False,
            "TEMPLATE_DEBUG": False,
            "SECURE_SSL_REDIRECT": True,
            "SECURE_BROWSER_XSS_FILTER": True,
        },
        "markers": ["security"],
    },
}


# Test execution utilities
def run_test_suite(test_type="all", coverage=True, parallel=False):
    """Run a specific test suite."""
    import subprocess
    import sys

    cmd = [sys.executable, "-m", "pytest"]

    if test_type != "all":
        if test_type in TEST_CONFIGS:
            markers = TEST_CONFIGS[test_type]["markers"]
            cmd.extend(["-m", " or ".join(markers)])
        else:
            cmd.extend(["-k", test_type])

    if coverage:
        cmd.extend(
            [
                "--cov=.",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=80",
            ]
        )

    if parallel:
        cmd.extend(["-n", "auto"])

    cmd.extend(["--tb=short", "--maxfail=10", "--durations=10"])

    return subprocess.run(cmd, check=True)


# Test reporting utilities
def generate_test_report():
    """Generate a comprehensive test report."""
    from datetime import datetime

    report = {
        "timestamp": datetime.now().isoformat(),
        "test_suites": {},
        "coverage": {},
        "performance": {},
        "security": {},
        "summary": {},
    }

    # This would be populated by actual test execution
    # For now, return a template

    return report


# Export commonly used functions
__all__ = [
    "TEST_CONFIG",
    "test_settings",
    "configure_test_database",
    "configure_test_cache",
    "configure_test_email",
    "configure_test_celery",
    "configure_test_storage",
    "configure_test_security",
    "configure_test_logging",
    "configure_test_performance",
    "configure_test_api",
    "setup_test_environment",
    "cleanup_test_environment",
    "create_test_data",
    "assert_model_count",
    "assert_response_contains",
    "assert_response_not_contains",
    "measure_response_time",
    "assert_response_time_under",
    "assert_no_sql_injection",
    "assert_no_xss_vulnerability",
    "TEST_CONFIGS",
    "run_test_suite",
    "generate_test_report",
]
