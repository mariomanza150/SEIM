"""
Test settings for SEIM project.

This file contains settings specific to the test environment.
"""

import copy
import os
import tempfile
from urllib.parse import urlparse, urlunparse

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Use DATABASE_URL if available (for E2E tests in Docker), otherwise SQLite for unit tests
import environ

env = environ.Env()


def _docker_compose_postgres_service_to_localhost(url: str) -> str:
    """Map Compose Postgres hostname *db* to loopback when tests run on the host OS."""
    if not url or os.path.exists("/.dockerenv"):
        return url
    u = urlparse(url)
    scheme = (u.scheme or "").lower()
    if scheme not in ("postgres", "postgresql", "pgsql", "postgis"):
        return url
    if u.hostname != "db":
        return url
    published = env.int("DATABASE_PUBLISHED_PORT", default=5434)
    inner_port = u.port or 5432
    port_on_host = published if inner_port == 5432 else inner_port
    auth = ""
    if u.username or u.password:
        if u.username:
            auth = u.username
            if u.password:
                auth += f":{u.password}"
        else:
            auth = f":{u.password}"
        auth += "@"
    return urlunparse(
        (
            u.scheme,
            f"{auth}127.0.0.1:{port_on_host}",
            u.path,
            u.params,
            u.query,
            u.fragment,
        )
    )


if os.environ.get("DATABASE_URL"):
    # Use PostgreSQL (rewrite Compose hostname when running outside Docker)
    DATABASES = {
        "default": env.db_url_config(
            _docker_compose_postgres_service_to_localhost(os.environ["DATABASE_URL"])
        )
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

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# Disable Wagtail and other non-essential apps for E2E tests
DISABLED_APPS = [
    "cacheops",
    "wagtail",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtailseo",
    "wagtail_markdown",
    "cms",  # Our CMS app that depends on Wagtail
]

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS
    if app not in DISABLED_APPS and not app.startswith("wagtail")
]

# Wagtail is stripped from INSTALLED_APPS but base TEMPLATES still reference its context
# processors; remove them so Django template rendering (e.g. admin dashboard) works in tests.
TEMPLATES = copy.deepcopy(TEMPLATES)
for _tpl in TEMPLATES:
    processors = _tpl.get("OPTIONS", {}).get("context_processors", [])
    _tpl.setdefault("OPTIONS", {})["context_processors"] = [
        p for p in processors if not p.startswith("wagtail.")
    ]

# Prefer a real Vue build when present (Playwright E2E). Only inject the minimal
# shell fixture when ``frontend-vue/dist`` is missing (unit/CI without npm build).
_TEST_TEMPLATE_DIR = BASE_DIR / "tests" / "fixtures" / "templates"
_VUE_DIST_INDEX = BASE_DIR / "frontend-vue" / "dist" / "index.html"
if not _VUE_DIST_INDEX.is_file():
    for _tpl in TEMPLATES:
        _tpl["DIRS"] = [_TEST_TEMPLATE_DIR] + list(_tpl.get("DIRS", []))

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
    "core.middleware.PrefetchUserRolesMiddleware",
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
