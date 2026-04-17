"""
Development settings for SEIM project.

This file contains settings specific to the development environment.
"""

import os
import sys
import warnings
from copy import deepcopy
from urllib.parse import urlunparse, urlparse

from .base import *


def _docker_compose_redis_host_to_localhost(url: str) -> str:
    """Map Compose service hostname *redis* to loopback when the process runs on the host OS.

    The name ``redis`` is only resolvable on Docker's embedded DNS. Using *env.example* on the
    host with ``redis://redis:...`` causes ``Name or service not known`` unless we rewrite.
    """
    if not url or os.path.exists("/.dockerenv"):
        return url
    u = urlparse(url)
    if (u.scheme or "").lower() not in ("redis", "rediss"):
        return url
    if u.hostname != "redis":
        return url
    port = u.port or 6379
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
        (u.scheme, f"{auth}127.0.0.1:{port}", u.path, u.params, u.query, u.fragment)
    )


def _docker_compose_postgres_service_to_localhost(url: str) -> str:
    """Map Compose Postgres hostname *db* to loopback when the process runs on the host OS.

    Same pattern as Redis: ``db`` only resolves on Docker's network. ``docker-compose.yml``
    publishes Postgres as host port 5434 → container 5432; use ``DATABASE_PUBLISHED_PORT``
    if your mapping differs.
    """
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


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ``/seim/*`` uses ``TemplateView`` + ``index.html`` from ``frontend-vue/dist``. If dist was never built
# (common on host without ``npm run build``), serve a help page instead of ``TemplateDoesNotExist``.
_vue_dist_index = BASE_DIR / "frontend-vue" / "dist" / "index.html"
if not _vue_dist_index.is_file():
    _dev_templates = deepcopy(TEMPLATES)
    for _tpl in _dev_templates:
        _tpl["DIRS"] = [
            BASE_DIR / "templates" / "vue_spa_missing_dist",
            *list(_tpl.get("DIRS", [])),
        ]
    TEMPLATES = _dev_templates

ALLOWED_HOSTS = ["*"]

# Database (rewrite Docker service hostname when running on the host; see env.example)
DATABASES = {
    "default": env.db_url_config(
        _docker_compose_postgres_service_to_localhost(env("DATABASE_URL"))
    )
}

# Enforce PostgreSQL for development
if "sqlite" in DATABASES["default"]["ENGINE"]:
    warnings.warn(
        "SQLite is not supported for development. Please set DATABASE_URL to a PostgreSQL connection string.",
        RuntimeWarning, stacklevel=2,
    )
    print(
        "ERROR: SQLite is not supported for development. Please set DATABASE_URL to a PostgreSQL connection string.",
        file=sys.stderr,
    )
    sys.exit(1)

# Redis/Celery — broker/backends set after email block (see Celery Configuration).
REDIS_URL = _docker_compose_redis_host_to_localhost(env("REDIS_URL"))

# Django Caching Configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Use PickleSerializer to support caching of HttpResponse objects (required for cache_page)
            "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "seim",
        "TIMEOUT": 300,  # 5 minutes default
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "seim_session",
        "TIMEOUT": 3600,  # 1 hour for sessions
    },
    "api": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "seim_api",
        "TIMEOUT": 600,  # 10 minutes for API responses
    },
    "analytics": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "seim_analytics",
        "TIMEOUT": 1800,  # 30 minutes for analytics data
    },
}

# ``base`` set ``CHANNEL_LAYERS`` while importing; align with rewritten ``REDIS_URL``.
CHANNEL_LAYERS["default"]["CONFIG"]["hosts"] = [REDIS_URL]

# Session Configuration with Redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Cache Middleware Configuration
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = "seim"
CACHE_MIDDLEWARE_ALIAS = "default"

# Add cache middleware to the beginning of middleware stack
# Temporarily disabled due to Redis connection issues
# MIDDLEWARE = [
#     'django.middleware.cache.UpdateCacheMiddleware',  # Must be first
# ] + MIDDLEWARE + [
#     'django.middleware.cache.FetchFromCacheMiddleware',  # Must be last
# ]

# AWS S3 config stub
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

# Development tools
# INSTALLED_APPS += ['livereload']  # Uncomment to enable livereload.js injection for hot reloading
# MIDDLEWARE += ['livereload.middleware.LiveReloadScript']  # Uncomment to enable livereload.js injection for hot reloading

# Email Configuration
EMAIL_BACKEND = env("EMAIL_BACKEND")

if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = env.int("EMAIL_PORT")
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# For AWS SES (production)
if env("EMAIL_BACKEND") == "django_ses.SESBackend":
    AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME")
    AWS_SES_ACCESS_KEY_ID = env("AWS_SES_ACCESS_KEY_ID")
    AWS_SES_SECRET_ACCESS_KEY = env("AWS_SES_SECRET_ACCESS_KEY")
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# Celery Configuration
CELERY_BROKER_URL = _docker_compose_redis_host_to_localhost(env("CELERY_BROKER_URL"))
CELERY_RESULT_BACKEND = _docker_compose_redis_host_to_localhost(env("CELERY_RESULT_BACKEND"))

# CORS Configuration for Vue.js SPA Development
CORS_ALLOW_ALL_ORIGINS = False  # More secure - specify origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server (Vue.js)
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Alternative port
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# Allow all HTTP methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow common headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Security Settings (relaxed for development)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Static files configuration for development
# Use simple storage backend that doesn't require manifest files
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Logging for development (container-friendly: stdout, formatted)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Disable throttle for E2E (set DISABLE_THROTTLE_E2E=1 when running API for Playwright)
if os.environ.get("DISABLE_THROTTLE_E2E"):
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
