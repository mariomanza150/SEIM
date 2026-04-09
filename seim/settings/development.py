"""
Development settings for SEIM project.

This file contains settings specific to the development environment.
"""

import os
import sys
import warnings
from copy import deepcopy

from .base import *

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

# Database
DATABASES = {"default": env.db("DATABASE_URL")}

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

# Redis/Celery config
REDIS_URL = env("REDIS_URL")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

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
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")

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
