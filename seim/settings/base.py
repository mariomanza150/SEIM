"""
Base settings for SEIM project.

This file contains settings that are common to all environments.
Environment-specific settings should be in separate files.
"""

import os
from pathlib import Path

import environ

from core.branding import DEFAULT_INSTITUTION, merge_institution_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# Used by django.core.mail.send_mail and Celery notification tasks (From: header).
# SMTP/SES settings files may override this when those backends are selected.
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@seim.local")

# Public origin for SPA links in emails (no trailing slash). Paths use /seim/...
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:8001").rstrip(
    "/"
)

# Google Calendar OAuth (optional). When unset, connect/sync APIs return 503.
GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID", default="")
GOOGLE_OAUTH_CLIENT_SECRET = env("GOOGLE_OAUTH_CLIENT_SECRET", default="")
GOOGLE_OAUTH_REDIRECT_URI = env("GOOGLE_OAUTH_REDIRECT_URI", default="")

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
    # Wagtail CMS
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
    "wagtail",
    "wagtail.contrib.settings",
    "wagtail.contrib.table_block",
    "wagtail.contrib.routable_page",
    "wagtail.api.v2",
    "wagtailseo",
    "wagtailmarkdown",
    "modelcluster",
    "taggit",
    # DRF and API
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_js_reverse",
    "channels",
]

LOCAL_APPS = [
    "cms",  # Wagtail CMS pages and content
    "exchange",
    "notifications",
    "documents",
    "accounts",
    "core",
    "analytics",
    "api",
    "grades",
    "application_forms",  # Custom form types and submissions (separate from dynforms package)
    "workflows",
    "data_management",
]

INSTALLED_APPS = (
    DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
    + [
        "crispy_forms",
        "crispy_bootstrap5",
        "crisp_modals",
        "itemlist",
        "dynforms",
        "django_celery_beat",
    ]
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # For i18n language detection
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Wagtail Middleware
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    # API Response Caching Middleware
    "core.cache.APICacheMiddleware",
]

ROOT_URLCONF = "seim.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",  # Keep for Django admin/Wagtail
            BASE_DIR / "frontend-vue" / "dist",  # Vue.js SPA build output
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
                "wagtail.contrib.settings.context_processors.settings",
                "core.context_processors.institution",
            ],
        },
    },
]

WSGI_APPLICATION = "seim.wsgi.application"
ASGI_APPLICATION = "seim.asgi.application"

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

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "UTC"

# Supported languages
LANGUAGES = [
    ("en", "English"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
]

# Locale paths
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
_branding_dir = BASE_DIR / "branding"
if _branding_dir.is_dir():
    STATICFILES_DIRS.append(_branding_dir)

# If the Vue SPA has been built, include its compiled assets so `collectstatic`
# can serve them via WhiteNoise in production(-like) containers.
_vue_dist_dir = BASE_DIR / "frontend-vue" / "dist"
if _vue_dist_dir.is_dir():
    # Include dist (not dist/assets) so collected files keep the `assets/` path
    # Vite emits in production HTML.
    STATICFILES_DIRS.append(_vue_dist_dir)

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# WhiteNoise configuration for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
FORMS_URLFIELD_ASSUME_HTTPS = True

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Authentication settings
LOGIN_URL = "/seim/login/"
LOGIN_REDIRECT_URL = "/seim/dashboard/"
LOGOUT_REDIRECT_URL = "/seim/login/"

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
        "anon": "100/hour",  # Anonymous users: 100 requests per hour
        "user": "1000/hour",  # Authenticated users: 1000 requests per hour
        "burst": "10/minute",  # Burst rate for login/register endpoints
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
        "url": "http://localhost:8000/docs/",
    },
    "SERVERS": [
        {
            "url": "/",
            "description": "This host (Try it out uses the same origin as the docs page)",
        },
        {
            "url": "http://localhost:8001",
            "description": "Local Docker Compose (default web port)",
        },
        {"url": "http://localhost:8000", "description": "Alternate local port"},
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
VIRUS_SCANNER_TYPE = env(
    "VIRUS_SCANNER_TYPE", default="mock"
)  # Options: 'clamav', 'clamav_cli', 'mock'
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

# Channels Configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL", default="redis://redis:6379/2")],
        },
    },
}

# WebSocket Configuration
WEBSOCKET_ENABLED = env.bool("WEBSOCKET_ENABLED", default=True)
WEBSOCKET_RECONNECT_INTERVAL = env.int("WEBSOCKET_RECONNECT_INTERVAL", default=5000)

# Feature Flags
FEATURE_FLAGS = {
    "WEBSOCKET_NOTIFICATIONS": env.bool(
        "FEATURE_WEBSOCKET_NOTIFICATIONS", default=True
    ),
    "ADVANCED_SEARCH": env.bool("FEATURE_ADVANCED_SEARCH", default=True),
    "CALENDAR_VIEW": env.bool("FEATURE_CALENDAR_VIEW", default=True),
    "NOTIFICATION_CENTER": env.bool("FEATURE_NOTIFICATION_CENTER", default=True),
}

# Exchange agreement expiry: notify staff when end_date is exactly N days away (comma-separated).
_AGREEMENT_EXP_DAYS = env.str("AGREEMENT_EXPIRATION_REMINDER_DAYS", default="90,30,7")
AGREEMENT_EXPIRATION_REMINDER_DAYS = [
    int(x.strip()) for x in _AGREEMENT_EXP_DAYS.split(",") if x.strip().isdigit()
] or [90, 30, 7]

_AGREEMENT_EXP_STATUSES = env.str(
    "AGREEMENT_EXPIRATION_REMINDER_STATUSES",
    default="active,renewal_pending",
)
AGREEMENT_EXPIRATION_REMINDER_STATUSES = [
    s.strip() for s in _AGREEMENT_EXP_STATUSES.split(",") if s.strip()
] or ["active", "renewal_pending"]

# Institution branding (UAdeC is the default/example production theme).
# Precedence: env vars > tenant_config.json > branding/institution.json
# > branding/<slug>/config.json > defaults. See docs/white_labeling.md.
TENANT_CONFIG_FILE = env(
    "TENANT_CONFIG_FILE",
    default=str(BASE_DIR / "tenant_config.json"),
)
INSTITUTION_CONFIG_FILE = env(
    "INSTITUTION_CONFIG_FILE",
    default=str(BASE_DIR / "branding" / "institution.json"),
)
_INSTITUTION_FILE = merge_institution_config(
    BASE_DIR,
    override_path=INSTITUTION_CONFIG_FILE,
    tenant_path=TENANT_CONFIG_FILE,
)


def _institution_env(name: str, fallback: str = "") -> str:
    return env(
        name,
        default=_INSTITUTION_FILE.get(name, DEFAULT_INSTITUTION.get(name, fallback)),
    )


INSTITUTION_SLUG = _institution_env("INSTITUTION_SLUG", "uadec")
INSTITUTION_NAME = _institution_env("INSTITUTION_NAME")
INSTITUTION_SHORT_NAME = _institution_env("INSTITUTION_SHORT_NAME")
INSTITUTION_TAGLINE = _institution_env("INSTITUTION_TAGLINE")
INSTITUTION_DEPARTMENT = _institution_env("INSTITUTION_DEPARTMENT")
INSTITUTION_LOCATION = _institution_env("INSTITUTION_LOCATION")
INSTITUTION_WEBSITE = _institution_env("INSTITUTION_WEBSITE")
INSTITUTION_EMAIL = _institution_env("INSTITUTION_EMAIL")
INSTITUTION_PHONE = _institution_env("INSTITUTION_PHONE")
INSTITUTION_ADDRESS = _institution_env("INSTITUTION_ADDRESS")
INSTITUTION_LOGO_URL = _institution_env("INSTITUTION_LOGO_URL")
INSTITUTION_NAV_BRAND = _institution_env("INSTITUTION_NAV_BRAND")
INSTITUTION_SOCIAL_FACEBOOK = _institution_env("INSTITUTION_SOCIAL_FACEBOOK")
INSTITUTION_SOCIAL_TWITTER = _institution_env("INSTITUTION_SOCIAL_TWITTER")
INSTITUTION_SOCIAL_INSTAGRAM = _institution_env("INSTITUTION_SOCIAL_INSTAGRAM")
INSTITUTION_THEME_CSS = _institution_env("INSTITUTION_THEME_CSS", "uadec/theme.css")
INSTITUTION_THEME = {
    "primary": _institution_env("BRAND_PRIMARY", "#2E5790"),
    "primary_light": _institution_env("BRAND_PRIMARY_LIGHT", "#3251AC"),
    "primary_dark": _institution_env("BRAND_PRIMARY_DARK", "#1E3A5F"),
    "accent": _institution_env("BRAND_ACCENT", "#BF9B4C"),
    "accent_light": _institution_env("BRAND_ACCENT_LIGHT", "#EDB621"),
    "accent_dark": _institution_env("BRAND_ACCENT_DARK", "#A6863D"),
    "navy": _institution_env("BRAND_NAVY", "#1E3A5F"),
    "orange": _institution_env("BRAND_ORANGE", "#E67E22"),
    "text": _institution_env("BRAND_TEXT", "#2C3E50"),
}

# Wagtail CMS Configuration
WAGTAIL_SITE_NAME = env(
    "WAGTAIL_SITE_NAME",
    default=f"SEIM - {INSTITUTION_SHORT_NAME}",
)
WAGTAILADMIN_BASE_URL = env("WAGTAILADMIN_BASE_URL", default="http://localhost:8000")

# Wagtail API Configuration
WAGTAILAPI_BASE_URL = env("WAGTAILADMIN_BASE_URL", default="http://localhost:8000")
WAGTAILAPI_LIMIT_MAX = 100
WAGTAILAPI_SEARCH_ENABLED = True

# Media files configuration for Wagtail
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Wagtail search backend
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Wagtail image formats
WAGTAILIMAGES_FORMAT_CONVERSIONS = {
    "webp": "webp",
    "jpeg": "jpeg",
}

# Wagtail custom image renditions
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]

# Wagtail image max upload size (10MB)
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 10 * 1024 * 1024

# Enable Wagtail image feature detection (faces, etc.)
WAGTAILIMAGES_FEATURE_DETECTION_ENABLED = False

# Wagtail document max upload size (50MB)
WAGTAILDOCS_MAX_UPLOAD_SIZE = 50 * 1024 * 1024

# Enable Wagtail workflows and moderation
WAGTAIL_WORKFLOW_ENABLED = True
WAGTAIL_MODERATION_ENABLED = True

# Wagtail email notification settings
WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="noreply@seim.local"
)
WAGTAILADMIN_NOTIFICATION_USE_HTML = True

# Wagtail admin UI customization
WAGTAIL_ENABLE_UPDATE_CHECK = False  # Disable update check in production
WAGTAIL_GRAVATAR_PROVIDER_URL = None  # Disable Gravatar

# Wagtail user admin uses Django's AUTH_USER_MODEL (accounts.User) with the
# default UserEditForm / UserCreationForm. Do not set WAGTAIL_USER_* (deprecated
# in Wagtail 6.x, removed in 7); for custom fields/forms, subclass UserViewSet
# and set user_viewset on the Wagtail users app config.

# Wagtail automatically uses the AUTH_USER_MODEL specified above
# Both Django admin and Wagtail admin share the same authentication
# Users can access both admin interfaces based on their permissions

# Password required for private pages
WAGTAIL_PASSWORD_MANAGEMENT_ENABLED = True
WAGTAIL_PASSWORD_REQUIRED_TEMPLATE = "wagtailcore/password_required.html"

# Allowed file extensions for Wagtail documents
WAGTAILDOCS_EXTENSIONS = [
    "csv",
    "docx",
    "key",
    "odt",
    "pdf",
    "pptx",
    "rtf",
    "txt",
    "xlsx",
    "zip",
]

# Wagtail SEO Configuration
SEO_JS_ENABLED = False  # Disable JavaScript SEO checks for better performance
SEO_TWITTER_CARD_TYPE = "summary_large_image"  # Default Twitter card type
SEO_DEFAULT_IMAGE = None  # Will be set per environment if needed
