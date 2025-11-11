# Implementation Plan: Fix CORS Configuration for Production

**Priority:** 🔴 Critical Security Issue  
**Effort:** 30 minutes  
**Risk:** High - Allows any domain to access API in production  
**Dependencies:** None  

---

## Problem Statement

The current CORS configuration allows **all origins** to access the API, even in production. This is a security vulnerability that could allow malicious websites to make unauthorized requests to your API.

### Current Code

**File:** `seim/settings/base.py` (Line 269)

```python
# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True  # ❌ DANGEROUS!
```

### Security Risks

1. **CSRF Attacks:** Malicious sites can make requests on behalf of authenticated users
2. **Data Theft:** Attackers can steal user data via XSS + CORS
3. **API Abuse:** Any website can consume your API resources
4. **Compliance Issues:** Violates security best practices

---

## Proposed Solution

### Step 1: Create Environment-Specific CORS Settings

We'll keep permissive CORS for development but restrict it in production.

#### Update base.py

**File:** `seim/settings/base.py`

**Remove or comment out:**
```python
# CORS Configuration
# CORS_ALLOW_ALL_ORIGINS = True  # ❌ Remove this
```

**Add:**
```python
# CORS Configuration (environment-specific)
# See development.py and production.py for actual settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
```

#### Update development.py

**File:** `seim/settings/development.py`

```python
"""
Development settings for SEIM project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database
# Development uses PostgreSQL via Docker
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgresql://seimuser:seimpass@db:5432/seim")
}

# CORS - Allow all origins in development for easier testing
CORS_ALLOW_ALL_ORIGINS = True  # ✅ OK in development
CORS_ALLOW_CREDENTIALS = True

# Celery
CELERY_BROKER_URL = env("REDIS_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://redis:6379/0")

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Debug toolbar
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
    INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
```

#### Update production.py

**File:** `seim/settings/production.py`

```python
"""
Production settings for SEIM project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Security settings
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# HSTS Security Headers
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL/HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# CORS - STRICT in production ✅
CORS_ALLOW_ALL_ORIGINS = False  # ✅ Explicit False
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://app.yourdomain.com",
    ]
)
CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://app.yourdomain.com",
    ]
)

# Database
DATABASES = {
    "default": env.db("DATABASE_URL")
}

# Celery
CELERY_BROKER_URL = env("REDIS_URL")
CELERY_RESULT_BACKEND = env("REDIS_URL")

# Email backend for production (AWS SES or SMTP)
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@yourdomain.com")

# Static files (production)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "/var/log/seim/error.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
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
    },
}

# Optional: Sentry for error tracking
SENTRY_DSN = env("SENTRY_DSN", default=None)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=env("DJANGO_ENV", default="production"),
    )
```

---

### Step 2: Update Environment Files

#### Development Environment

**File:** `env.example` (or `.env` for local development)

```bash
# Django Configuration
DJANGO_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://seimuser:seimpass@db:5432/seim

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Email Configuration (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# CORS Configuration (Development - Permissive)
# CORS_ALLOWED_ORIGINS=  # Not needed in development, CORS_ALLOW_ALL_ORIGINS=True
```

#### Production Environment

**File:** `env.prod.example`

```bash
# Django Configuration
DJANGO_ENV=production
SECRET_KEY=CHANGE_THIS_TO_SECURE_RANDOM_STRING
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,app.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://production_user:secure_password@db-host:5432/seim_production

# Redis Configuration
REDIS_URL=redis://redis-host:6379/0

# Email Configuration (Production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# CORS Configuration (Production - STRICT)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com

# CSRF Configuration (Production)
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com

# Optional: Error Tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

---

### Step 3: Update Docker Configuration

**File:** `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: gunicorn seim.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env.prod  # Use production env file
    environment:
      - DJANGO_SETTINGS_MODULE=seim.settings.production  # ✅ Use production settings
    depends_on:
      - db
      - redis
    expose:
      - 8000

  nginx:
    build: ./nginx
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web

  db:
    image: postgres:15
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    env_file:
      - .env.prod
    environment:
      - POSTGRES_DB=seim_production
      - POSTGRES_USER=production_user
      - POSTGRES_PASSWORD=secure_password

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data_prod:/data

  celery:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A seim worker -l info
    volumes:
      - media_volume:/app/media
    env_file:
      - .env.prod
    environment:
      - DJANGO_SETTINGS_MODULE=seim.settings.production
    depends_on:
      - db
      - redis

volumes:
  postgres_data_prod:
  redis_data_prod:
  static_volume:
  media_volume:
```

---

## Implementation Steps

### Step 1: Update Settings Files (10 minutes)

1. Edit `seim/settings/base.py` - remove CORS_ALLOW_ALL_ORIGINS
2. Edit `seim/settings/development.py` - add permissive CORS
3. Edit `seim/settings/production.py` - add strict CORS

### Step 2: Update Environment Files (5 minutes)

1. Update `env.example` with development CORS settings
2. Update `env.prod.example` with production CORS settings
3. Create/update `.env.prod` with actual production domains

### Step 3: Test in Development (5 minutes)

```bash
# Verify development still works
docker-compose down
docker-compose up -d
docker-compose exec web python manage.py check

# Test CORS in development
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/programs/
# Should return CORS headers allowing the origin
```

### Step 4: Test Production Configuration Locally (10 minutes)

```bash
# Use production settings locally for testing
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Test CORS with allowed origin
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/programs/
# Should return CORS headers

# Test CORS with non-allowed origin (should fail)
curl -H "Origin: https://malicious-site.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/programs/
# Should NOT return CORS headers allowing the origin
```

---

## Verification Checklist

Before deploying to production:

- [ ] CORS_ALLOW_ALL_ORIGINS removed from base.py
- [ ] Development settings allow all origins
- [ ] Production settings restrict to specific domains
- [ ] CORS_ALLOWED_ORIGINS set in .env.prod
- [ ] CSRF_TRUSTED_ORIGINS set in .env.prod
- [ ] ALLOWED_HOSTS set in .env.prod
- [ ] All domains use HTTPS in production
- [ ] SSL/HTTPS settings enabled in production
- [ ] Test with allowed origin (works)
- [ ] Test with disallowed origin (blocked)
- [ ] Documentation updated

---

## Testing

### Manual Testing

**Test 1: Development - All Origins Allowed**
```bash
# Start development server
docker-compose up -d

# Test from any origin
curl -i -H "Origin: http://any-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/programs/

# Expected: CORS headers present
# Access-Control-Allow-Origin: *
```

**Test 2: Production - Only Allowed Origins**
```bash
# Test with allowed origin
curl -i -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://api.yourdomain.com/api/programs/

# Expected: CORS headers present
# Access-Control-Allow-Origin: https://yourdomain.com

# Test with disallowed origin
curl -i -H "Origin: https://malicious.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://api.yourdomain.com/api/programs/

# Expected: No CORS headers or error
```

### Automated Testing

**Create:** `core/tests/test_cors_configuration.py`

```python
from django.test import TestCase, override_settings
from django.test.client import Client


class CORSConfigurationTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    @override_settings(
        CORS_ALLOW_ALL_ORIGINS=False,
        CORS_ALLOWED_ORIGINS=['https://allowed-domain.com']
    )
    def test_cors_allows_configured_origin(self):
        """Test that configured origins are allowed."""
        response = self.client.options(
            '/api/programs/',
            HTTP_ORIGIN='https://allowed-domain.com',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='GET'
        )
        
        self.assertEqual(
            response['Access-Control-Allow-Origin'],
            'https://allowed-domain.com'
        )
    
    @override_settings(
        CORS_ALLOW_ALL_ORIGINS=False,
        CORS_ALLOWED_ORIGINS=['https://allowed-domain.com']
    )
    def test_cors_blocks_non_configured_origin(self):
        """Test that non-configured origins are blocked."""
        response = self.client.options(
            '/api/programs/',
            HTTP_ORIGIN='https://malicious.com',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='GET'
        )
        
        # Should not have CORS header or should deny
        self.assertNotIn(
            'Access-Control-Allow-Origin',
            response
        )
```

Run tests:
```bash
docker-compose exec web python manage.py test core.tests.test_cors_configuration
```

---

## Documentation Updates

**File:** `documentation/deployment.md`

Add CORS configuration section:

```markdown
## CORS Configuration

### Development
CORS is configured to allow all origins for easier development and testing.

### Production
CORS is strictly configured to only allow requests from your application's domains.

**Required Environment Variables:**
```bash
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Important:**
- All origins MUST use HTTPS in production
- Add all subdomains that need API access
- Never use wildcards or CORS_ALLOW_ALL_ORIGINS=True in production
```

**File:** `documentation/environment_variables.md`

Add:

```markdown
## CORS Configuration

### CORS_ALLOWED_ORIGINS
**Required in Production**  
**Format:** Comma-separated list of allowed origins

Specifies which domains can make cross-origin requests to the API.

**Example:**
```bash
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com
```

**Important:**
- Use HTTPS in production
- No trailing slashes
- Include all subdomains
- Separate with commas (no spaces)

### CSRF_TRUSTED_ORIGINS
**Required in Production**  
**Format:** Comma-separated list of trusted origins

Specifies which origins are trusted for CSRF validation.

**Example:**
```bash
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```
```

---

## Rollback Plan

If issues occur in production:

1. **Emergency Fix:** Temporarily allow all origins
   ```python
   # production.py (TEMPORARY ONLY!)
   CORS_ALLOW_ALL_ORIGINS = True  # TODO: FIX ASAP
   ```

2. **Restart Services:**
   ```bash
   docker-compose -f docker-compose.prod.yml restart web
   ```

3. **Investigate:** Check which origins are being blocked
   ```bash
   docker-compose -f docker-compose.prod.yml logs web | grep CORS
   ```

4. **Fix:** Add missing origins to CORS_ALLOWED_ORIGINS

5. **Redeploy:** With correct configuration

---

## Common Issues & Solutions

### Issue 1: Frontend Can't Access API

**Symptom:** CORS errors in browser console

**Solution:** Add frontend domain to CORS_ALLOWED_ORIGINS
```bash
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Issue 2: Mobile App Can't Access API

**Symptom:** Mobile app gets CORS errors

**Solution:** Mobile apps don't need CORS! CORS is browser-only. Check authentication instead.

### Issue 3: Subdomain Not Working

**Symptom:** api.yourdomain.com works but app.yourdomain.com doesn't

**Solution:** Add subdomain explicitly
```bash
CORS_ALLOWED_ORIGINS=https://api.yourdomain.com,https://app.yourdomain.com
```

---

## Estimated Time Breakdown

| Task | Time |
|------|------|
| Update base.py | 2 min |
| Update development.py | 3 min |
| Update production.py | 5 min |
| Update env files | 3 min |
| Test in development | 5 min |
| Test production config | 5 min |
| Write tests | 5 min |
| Update documentation | 2 min |

**Total:** ~30 minutes

---

## Success Criteria

✅ **Development:** All origins allowed for easy testing  
✅ **Production:** Only configured origins allowed  
✅ **Security:** CORS_ALLOW_ALL_ORIGINS=False in production  
✅ **Tests:** Automated tests verify configuration  
✅ **Documentation:** Environment variables documented  
✅ **HTTPS:** All production origins use HTTPS  

---

## Next Steps

After this fix:
1. ✅ Deploy to staging environment first
2. ✅ Test with real frontend application
3. ✅ Verify mobile apps still work (they don't use CORS)
4. ✅ Monitor for CORS errors in production
5. ✅ Move to next fix (N+1 queries)

