"""
Base settings for SEIM project.

This file contains settings that are common to all environments.
Environment-specific settings should be in separate files.
"""

import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_js_reverse",
]

LOCAL_APPS = [
    "exchange",
    "notifications",
    "documents",
    "accounts",
    "core",
    "analytics",
    "api",
    "dashboard",
    "plugins",
    "frontend",
    "grades",
    "application_forms",  # Custom form types and submissions (separate from dynforms package)
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + [
    'crispy_forms',
    'crispy_bootstrap5',
    'crisp_modals',
    'itemlist',
    'dynforms',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # API Response Caching Middleware
    "core.cache.APICacheMiddleware",
]

ROOT_URLCONF = "seim.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
            ],
        },
    },
]

WSGI_APPLICATION = "seim.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# WhiteNoise configuration for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Authentication settings
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",      # Anonymous users: 100 requests per hour
        "user": "1000/hour",     # Authenticated users: 1000 requests per hour
        "burst": "10/minute",    # Burst rate for login/register endpoints
    },
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# DRF Spectacular Settings for API Documentation
SPECTACULAR_SETTINGS = {
    "TITLE": "SEIM API",
    "DESCRIPTION": """
    Student Exchange Information Manager (SEIM) API

    A comprehensive API for managing student exchange programs, applications, documents, and notifications.

    ## Features
    - **User Management**: Registration, authentication, and role-based access control
    - **Program Management**: Create and manage exchange programs with eligibility criteria
    - **Application Workflow**: Complete application lifecycle from draft to completion
    - **Document Management**: File upload, validation, and resubmission workflows
    - **Notifications**: Email and in-app notification system
    - **Analytics**: Reporting and dashboard metrics

    ## Authentication
    This API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_token>
    ```

    ## Roles
    - **Student**: Can create applications, upload documents, view their own data
    - **Coordinator**: Can review applications, validate documents, manage programs
    - **Admin**: Full system access, user management, analytics
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/",
    "CONTACT": {
        "name": "SEIM Development Team",
        "email": "support@seim.local",
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "TAGS": [
        {
            "name": "authentication",
            "description": "User authentication and authorization endpoints",
        },
        {
            "name": "accounts",
            "description": "User account management and profile operations",
        },
        {
            "name": "programs",
            "description": "Exchange program management and configuration",
        },
        {
            "name": "applications",
            "description": "Student application workflow and management",
        },
        {
            "name": "documents",
            "description": "Document upload, validation, and management",
        },
        {
            "name": "notifications",
            "description": "Email and in-app notification system",
        },
        {"name": "analytics", "description": "Reporting, metrics, and dashboard data"},
    ],
    "EXTERNAL_DOCS": {
        "description": "SEIM Documentation",
        "url": "http://localhost:8000/documentation/",
    },
    "SERVERS": [
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.seim.local", "description": "Production server"},
    ],
    "SECURITY": [{"jwtAuth": []}],
    "SECURITY_DEFINITIONS": {
        "jwtAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    },
}

# CORS Configuration (environment-specific - see development.py and production.py)
CORS_ALLOW_CREDENTIALS = True

# Celery Configuration
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Redis Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Use PickleSerializer to support caching of HttpResponse objects (required for cache_page)
            "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
        },
        "TIMEOUT": 300,  # Default: 5 minutes
    }
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Virus Scanner Configuration
VIRUS_SCANNER_TYPE = env("VIRUS_SCANNER_TYPE", default="mock")  # Options: 'clamav', 'clamav_cli', 'mock'
VIRUS_SCANNER_CONFIG = {
    "socket_path": env("VIRUS_SCANNER_SOCKET_PATH", default=None),
    "host": env("VIRUS_SCANNER_HOST", default="localhost"),
    "port": env.int("VIRUS_SCANNER_PORT", default=3310),
    "timeout": env.int("VIRUS_SCANNER_TIMEOUT", default=30),
    "clamscan_path": env("VIRUS_SCANNER_CLAMSCAN_PATH", default="clamscan"),
    "simulate_infected": env.bool("VIRUS_SCANNER_SIMULATE_INFECTED", default=False),
    "threat_name": env("VIRUS_SCANNER_THREAT_NAME", default="TestVirus"),
}
VIRUS_SCAN_FAIL_SECURE = env.bool("VIRUS_SCAN_FAIL_SECURE", default=True)
