import os
from .base import *  # Import all base settings first

DEBUG = True  # Override DEBUG setting
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database configuration for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "seim"),
        "USER": os.getenv("POSTGRES_USER", "seim_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "seim_pass"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# Fallback to SQLite for local development without Docker
if os.getenv("USE_SQLITE", "False") == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Email backend for development (console output)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Development-specific middleware
MIDDLEWARE += [
    "django.middleware.common.BrokenLinkEmailsMiddleware",
]

# Debug toolbar configuration (optional)
if os.getenv("DJANGO_DEBUG_TOOLBAR", "False") == "True":
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.common.CommonMiddleware") + 1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

# Simplified REST Framework settings for development
REST_FRAMEWORK.update(
    {
        "DEFAULT_RENDERER_CLASSES": [
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",  # Enable browsable API in dev
        ],
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.AllowAny",  # More permissive in development
        ],
    }
)

# Logging configuration for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
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
        "exchange": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Disable some security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Development CORS settings (if needed)
if os.getenv("ENABLE_CORS_DEV", "False") == "True":
    INSTALLED_APPS += ["corsheaders"]
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
        "corsheaders.middleware.CorsMiddleware",
    )
    CORS_ALLOW_ALL_ORIGINS = True  # Only for development!

# File upload settings for development
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB for dev
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Cache configuration for development
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection._HiredisParser",  # Updated parser class
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 50,
                "timeout": 20,
            },
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",  # Added compression
            "RETRY_ON_TIMEOUT": True,  # Added retry on timeout
        },
        "KEY_PREFIX": "sgii_dev",  # Prefix for development cache keys
        "TIMEOUT": 300,  # 5 minutes default timeout
    }
}

# Configure ratelimit to use redis cache
RATELIMIT_USE_CACHE = "default"
