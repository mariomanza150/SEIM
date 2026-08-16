# SEIM Environment Variables Reference

## Overview
This document provides a comprehensive reference for all environment variables used in SEIM (Student Exchange Information Manager). These variables control application behavior, security, and external service connections.

---

## 🚀 **Quick Setup**

### **Copy Environment Template:**
```bash
# Copy the example file
cp env.example .env

# Edit with your values
nano .env
```

### **Required Variables:**
```bash
# Minimum required for development
DJANGO_ENV=dev
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/seim_db
REDIS_URL=redis://localhost:6379/0
```

---

## 📋 **Environment Variables by Category**

### **🔧 Django Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_ENV` | ✅ | `dev` | Environment type: `dev`, `test`, `production` |
| `SECRET_KEY` | ✅ | - | Django secret key for cryptographic signing |
| `DEBUG` | ❌ | `True` (dev) | Enable Django debug mode |
| `ALLOWED_HOSTS` | ❌ | `localhost,127.0.0.1` | Comma-separated list of allowed hosts |
| `CSRF_TRUSTED_ORIGINS` | ❌ | - | Comma-separated list of trusted origins for CSRF |

#### **Examples:**
```bash
# Development
DJANGO_ENV=dev
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Production
DJANGO_ENV=production
SECRET_KEY=your-super-secure-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### **🗄️ Database Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection string |
| `DB_HOST` | ❌ | `localhost` | Database host |
| `DB_PORT` | ❌ | `5432` | Database port |
| `DB_NAME` | ❌ | `seim_db` | Database name |
| `DB_USER` | ❌ | `postgres` | Database username |
| `DB_PASSWORD` | ❌ | `postgres` | Database password |

#### **Database URL Format:**
```bash
# PostgreSQL URL format
DATABASE_URL=postgresql://username:password@host:port/database_name

# Examples:
DATABASE_URL=postgresql://seim_user:password123@localhost:5432/seim_db
DATABASE_URL=postgresql://postgres:postgres@db:5432/seim_db
```

#### **Individual Database Variables:**
```bash
# Alternative to DATABASE_URL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=seim_db
DB_USER=seim_user
DB_PASSWORD=secure_password
```

### **🔴 Redis Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | ✅ | - | Redis connection string |
| `REDIS_HOST` | ❌ | `localhost` | Redis host |
| `REDIS_PORT` | ❌ | `6379` | Redis port |
| `REDIS_DB` | ❌ | `0` | Redis database number |
| `REDIS_PASSWORD` | ❌ | - | Redis password (if required) |

#### **Redis URL Format:**
```bash
# Redis URL format
REDIS_URL=redis://[:password@]host[:port][/db-number]

# Examples:
REDIS_URL=redis://localhost:6379/0
REDIS_URL=redis://:password@redis:6379/1
REDIS_URL=redis://redis:6379/0
```

### **📧 Email Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_BACKEND` | ❌ | `console` | Email backend: `console`, `smtp`, `ses` |
| `EMAIL_HOST` | ❌ | - | SMTP server host |
| `EMAIL_PORT` | ❌ | `587` | SMTP server port |
| `EMAIL_USE_TLS` | ❌ | `True` | Use TLS encryption |
| `EMAIL_HOST_USER` | ❌ | - | SMTP username |
| `EMAIL_HOST_PASSWORD` | ❌ | - | SMTP password |
| `DEFAULT_FROM_EMAIL` | ❌ | `noreply@seim.local` | Default sender email |

#### **Email Backend Examples:**

**Console Backend (Development):**
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**SMTP Backend (Gmail):**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**AWS SES Backend:**
```bash
EMAIL_BACKEND=django_ses.SESBackend
AWS_SES_REGION_NAME=us-east-1
AWS_SES_ACCESS_KEY_ID=your-access-key
AWS_SES_SECRET_ACCESS_KEY=your-secret-key
```

### **☁️ AWS Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | ❌ | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | ❌ | - | AWS secret key |
| `AWS_STORAGE_BUCKET_NAME` | ❌ | - | S3 bucket for file storage |
| `AWS_S3_REGION_NAME` | ❌ | `us-east-1` | AWS region |
| `AWS_S3_CUSTOM_DOMAIN` | ❌ | - | Custom S3 domain |
| `AWS_DEFAULT_ACL` | ❌ | `private` | Default ACL for S3 objects |

#### **AWS S3 Configuration:**
```bash
# For file storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=seim-media-bucket
AWS_S3_REGION_NAME=us-east-1
AWS_DEFAULT_ACL=private
```

### **🔧 Celery Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CELERY_BROKER_URL` | ❌ | `REDIS_URL` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | ❌ | `REDIS_URL` | Celery result backend |
| `CELERY_TASK_ALWAYS_EAGER` | ❌ | `False` | Run tasks synchronously (dev) |
| `CELERY_TASK_EAGER_PROPAGATES` | ❌ | `True` | Propagate exceptions in eager mode |

#### **Celery Configuration Examples:**
```bash
# Development (synchronous tasks)
CELERY_TASK_ALWAYS_EAGER=True
CELERY_TASK_EAGER_PROPAGATES=True

# Production (asynchronous tasks)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### **🔐 Security Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECURE_SSL_REDIRECT` | ❌ | `False` | Redirect HTTP to HTTPS |
| `SESSION_COOKIE_SECURE` | ❌ | `False` | Secure session cookies |
| `CSRF_COOKIE_SECURE` | ❌ | `False` | Secure CSRF cookies |
| `SECURE_BROWSER_XSS_FILTER` | ❌ | `False` | Enable XSS filter |
| `SECURE_CONTENT_TYPE_NOSNIFF` | ❌ | `False` | Prevent MIME sniffing |
| `X_FRAME_OPTIONS` | ❌ | `DENY` | X-Frame-Options header |

#### **Security Configuration Examples:**
```bash
# Development
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Production
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
```

### **🏛 Institution branding (white-label)**

UAdeC is the default/example theme. Override to run SEIM for another institution. Full guide: [white_labeling.md](white_labeling.md).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `INSTITUTION_SLUG` | ❌ | `uadec` | Branding pack folder under `branding\` |
| `INSTITUTION_NAME` | ❌ | Universidad Autónoma de Coahuila | Footer / legal name |
| `INSTITUTION_SHORT_NAME` | ❌ | UAdeC | Short label in CMS chrome |
| `INSTITUTION_TAGLINE` | ❌ | Intercambio Académico | Title suffix |
| `INSTITUTION_DEPARTMENT` | ❌ | Dirección de Intercambio Académico | Footer + homepage hero |
| `INSTITUTION_LOCATION` | ❌ | Saltillo, Coahuila, México | Footer location |
| `INSTITUTION_WEBSITE` | ❌ | https://www.uadec.mx/ | Footer link and asset download source |
| `INSTITUTION_EMAIL` | ❌ | intercambio@uadec.edu.mx | Seed / contact email |
| `INSTITUTION_PHONE` | ❌ | +52 (844) 412-8800 ext. 2345 | Seed / contact phone |
| `INSTITUTION_ADDRESS` | ❌ | Saltillo address HTML | Seed postal address |
| `INSTITUTION_LOGO_URL` | ❌ | (empty) | Optional navbar logo URL |
| `INSTITUTION_THEME_CSS` | ❌ | `uadec/theme.css` | CMS theme stylesheet under `branding\` |
| `INSTITUTION_CONFIG_FILE` | ❌ | `branding/institution.json` | JSON overlay (env still wins) |
| `TENANT_CONFIG_FILE` | ❌ | `tenant_config.json` | Root tenant overlay (wins over institution.json) |
| `BRAND_PRIMARY` | ❌ | `#2E5090` | CMS primary color |
| `BRAND_ACCENT` | ❌ | `#C7A162` | CMS accent color |
| `WAGTAIL_SITE_NAME` | ❌ | `SEIM - {short name}` | Wagtail admin site name |

### **🎨 Frontend Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STATIC_URL` | ❌ | `/static/` | Static files URL prefix |
| `STATIC_ROOT` | ❌ | `staticfiles/` | Static files collection directory |
| `MEDIA_URL` | ❌ | `/media/` | Media files URL prefix |
| `MEDIA_ROOT` | ❌ | `media/` | Media files storage directory |

#### **Static/Media Configuration:**
```bash
# Development
STATIC_URL=/static/
STATIC_ROOT=staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=media/

# Production (with CDN)
STATIC_URL=https://cdn.yourdomain.com/static/
MEDIA_URL=https://cdn.yourdomain.com/media/
```

### **📊 Logging Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |
| `LOG_FILE` | ❌ | - | Log file path |
| `SENTRY_DSN` | ❌ | - | Sentry error tracking DSN |

#### **Logging Examples:**
```bash
# Development
LOG_LEVEL=DEBUG
LOG_FILE=logs/seim.log

# Production with Sentry
LOG_LEVEL=WARNING
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

---

## 🌍 **Environment-Specific Configurations**

### **Development Environment**
```bash
# .env.development
DJANGO_ENV=dev
DEBUG=True
SECRET_KEY=django-insecure-dev-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/seim_dev
REDIS_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CELERY_TASK_ALWAYS_EAGER=True
LOG_LEVEL=DEBUG
```

### **Testing Environment**
```bash
# .env.test
DJANGO_ENV=test
DEBUG=False
SECRET_KEY=test-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/seim_test
REDIS_URL=redis://localhost:6379/1
EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend
CELERY_TASK_ALWAYS_EAGER=True
LOG_LEVEL=WARNING
```

### **Production Environment**
```bash
# .env.production
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=your-super-secure-production-secret-key
DATABASE_URL=postgresql://seim_user:secure_password@db:5432/seim_prod
REDIS_URL=redis://redis:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
LOG_LEVEL=WARNING
```

---

## 🔧 **Configuration Management**

### **Loading Environment Variables**

#### **Using python-dotenv:**
```python
# settings/base.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
```

#### **Using django-environ:**
```python
# settings/base.py
import environ

env = environ.Env()

# Read .env file
environ.Env.read_env()

# Use environment variables
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
DATABASE_URL = env.db('DATABASE_URL')
```

### **Environment File Priority**
1. `.env.local` (highest priority)
2. `.env.{environment}` (e.g., `.env.production`)
3. `.env` (default)
4. System environment variables

### **Secret Management**

#### **Generate Secret Key:**
```bash
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Or use Django shell
docker-compose exec web python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### **Secure Secret Storage:**
```bash
# Use environment-specific files
cp .env .env.production
# Edit .env.production with production values

# Use .env.local for local overrides
cp .env .env.local
# Edit .env.local with local changes
```

---

## 🚨 **Security Best Practices**

### **Required for Production**
```bash
# These variables MUST be set in production
SECRET_KEY=your-super-secure-production-secret-key
DJANGO_ENV=production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### **Sensitive Variables**
Never commit these to version control:
- `SECRET_KEY`
- `EMAIL_HOST_PASSWORD`
- `AWS_SECRET_ACCESS_KEY`
- `DB_PASSWORD`
- `REDIS_PASSWORD`

### **Environment File Security**
```bash
# Add to .gitignore
.env
.env.local
.env.production
.env.staging

# Keep example file in version control
env.example
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Variable Not Found:**
```bash
# Check if variable is set
echo $VARIABLE_NAME

# Check .env file
cat .env | grep VARIABLE_NAME

# Check Django settings
docker-compose exec web python manage.py shell -c "
from django.conf import settings
print(getattr(settings, 'VARIABLE_NAME', 'Not set'))
"
```

#### **Database Connection Issues:**
```bash
# Test database connection
docker-compose exec web python manage.py dbshell

# Check database URL
echo $DATABASE_URL

# Test connection manually
docker-compose exec web python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1;')
print('Database connection successful')
"
```

#### **Email Configuration Issues:**
```bash
# Test email configuration
docker-compose exec web python manage.py shell -c "
from django.core.mail import send_mail
try:
    send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
    print('Email sent successfully')
except Exception as e:
    print('Email error:', e)
"
```

### **Validation Script**
```bash
#!/bin/bash
# validate_env.sh

echo "Validating environment variables..."

# Check required variables
required_vars=("DJANGO_ENV" "SECRET_KEY" "DATABASE_URL" "REDIS_URL")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required variable: $var"
        exit 1
    else
        echo "✅ $var is set"
    fi
done

echo "✅ All required variables are set"
```

---

## 📚 **Reference Examples**

### **Complete Development Environment**
```bash
# .env.development
DJANGO_ENV=dev
SECRET_KEY=django-insecure-dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/seim_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@seim.local

# Celery (synchronous for development)
CELERY_TASK_ALWAYS_EAGER=True
CELERY_TASK_EAGER_PROPAGATES=True

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/seim_dev.log

# Static/Media
STATIC_URL=/static/
STATIC_ROOT=staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=media/
```

### **Complete Production Environment**
```bash
# .env.production
DJANGO_ENV=production
SECRET_KEY=your-super-secure-production-secret-key-generated-securely
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgresql://seim_user:secure_password@db:5432/seim_prod

# Redis
REDIS_URL=redis://redis:6379/0

# Email (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Celery (asynchronous)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=seim-media-bucket
AWS_S3_REGION_NAME=us-east-1

# Logging
LOG_LEVEL=WARNING
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Static/Media (with CDN)
STATIC_URL=https://cdn.yourdomain.com/static/
STATIC_ROOT=staticfiles/
MEDIA_URL=https://cdn.yourdomain.com/media/
MEDIA_ROOT=media/
```

---

### **CI secrets (GitHub Actions, not `.env`)**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CODECOV_TOKEN` | Maintainers on `mariomanza150/SEIM` | (unset) | Codecov upload token. Set as a **GitHub Actions secret** only. Coverage XML/LCOV is always generated. Upload runs when the secret is present; a missing secret warns and skips upload (CI stays green). See [`.github/README.md`](../.github/README.md). |

Do not put `CODECOV_TOKEN` in `.env` or `env.example`.

---

## 🔗 **Related Documentation**

- [Installation Guide](installation.md)
- [Deployment Guide](deployment.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Admin Guide](admin_guide.md)
- [White-labeling](white_labeling.md)

---

**Last Updated**: December 2024  
**Version**: 1.0 