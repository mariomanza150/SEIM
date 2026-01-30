"""
Test settings for SEIM project.

This file contains settings specific to the test environment.
"""

import os
import tempfile

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Use DATABASE_URL if available (for E2E tests in Docker), otherwise SQLite for unit tests
import environ
env = environ.Env()

if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL for E2E tests
    DATABASES = {
        'default': env.db()
    }
else:
    # Use in-memory SQLite for unit tests
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# Disable caching for tests
CACHES = {
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

# Disable django-cacheops for tests (compatibility with Django 5.1)
CACHEOPS_ENABLED = False

# Disable Wagtail and other non-essential apps for E2E tests
DISABLED_APPS = [
    'cacheops',
    'wagtail',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtailseo',
    'wagtail_markdown',
    'cms',  # Our CMS app that depends on Wagtail
]

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in DISABLED_APPS and not app.startswith('wagtail')]

# Use console email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable Celery tasks for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"

# Use temporary file storage for tests
MEDIA_ROOT = tempfile.mkdtemp()
STATIC_ROOT = tempfile.mkdtemp()

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable middleware that might interfere with tests
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Disable static files collection
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Disable logging for tests
LOGGING = {
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
}

# Test-specific settings
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Disable CSRF for API tests
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

# Disable JWT token expiration for tests
SIMPLE_JWT = {
    **SIMPLE_JWT,
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# Disable AWS settings for tests
AWS_ACCESS_KEY_ID = "test-key"
AWS_SECRET_ACCESS_KEY = "test-secret"
AWS_STORAGE_BUCKET_NAME = "test-bucket"

# Disable virus scanning for tests
VIRUS_SCAN_ENABLED = False

# Test data settings
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, "tests", "fixtures"),
]

# Disable rate limiting for tests
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/hour",
        "user": "10000/hour",
        "burst": "1000/minute",  # Keep burst rate definition to avoid KeyError
    },
}
