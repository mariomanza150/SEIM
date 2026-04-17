"""
Production settings for SEIM project.

This file contains settings specific to the production environment.
"""

import os
from urllib.parse import urlparse, urlunparse

from .base import *


def _docker_compose_redis_host_to_localhost(url: str) -> str:
    """Map Compose hostname *redis* to loopback when the process runs on the host OS (not in a container)."""
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
    """Map Compose hostname *db* to loopback when the process runs on the host OS (not in a container)."""
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
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Database (rewrite Docker service hostname when running on the host; see env.example)
DATABASES = {
    "default": env.db_url_config(
        _docker_compose_postgres_service_to_localhost(env("DATABASE_URL"))
    )
}

# Redis/Celery config
REDIS_URL = _docker_compose_redis_host_to_localhost(env("REDIS_URL"))
CELERY_BROKER_URL = _docker_compose_redis_host_to_localhost(env("CELERY_BROKER_URL"))
CELERY_RESULT_BACKEND = _docker_compose_redis_host_to_localhost(env("CELERY_RESULT_BACKEND"))

# Django Caching Configuration (django_redis — matches dev; Django's RedisCache
# does not accept the same OPTIONS shape as django_redis.)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
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

# Full-page cache (optional). Disable for docker-compose.local-prod to avoid stale HTML during dev.
if not env.bool("DISABLE_PAGE_CACHE_MIDDLEWARE", default=False):
    MIDDLEWARE = (
        [
            "django.middleware.cache.UpdateCacheMiddleware",  # Must be first
        ]
        + MIDDLEWARE
        + [
            "django.middleware.cache.FetchFromCacheMiddleware",  # Must be last
        ]
    )

# AWS S3 config
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

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
if EMAIL_BACKEND == "django_ses.SESBackend":
    AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME")
    AWS_SES_ACCESS_KEY_ID = env("AWS_SES_ACCESS_KEY_ID")
    AWS_SES_SECRET_ACCESS_KEY = env("AWS_SES_SECRET_ACCESS_KEY")
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# CORS Configuration (strict for production)
CORS_ALLOW_ALL_ORIGINS = False  # Never allow all origins in production!
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[]  # Must be explicitly set in production
)

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[]  # Must be explicitly set in production
)

# Security Settings (strict for production; overridable e.g. docker-compose.local-prod)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Logging for production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/var/log/seim/django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
