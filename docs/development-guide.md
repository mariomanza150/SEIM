# SEIM Development Guide

**Generated:** 2025-01-27

## Prerequisites

### Required
- **Docker and Docker Compose** - Core development must use Docker
- **Git** - Version control
- **Python 3.12+** - For E2E testing and local development tools (host OS only)

### Optional (Host OS Development Tools)
- **Node.js** - For frontend testing (Jest)
- **Chrome/Chromium** - For Selenium E2E tests

## Development Environment Setup

### Docker Setup (Required for Core Development)

> **⚠️ Core development outside Docker is not supported. All backend development, testing, and documentation generation must be performed inside Docker containers.**

#### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd SEIM

# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# (See Environment Configuration section)
```

#### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Or with logs visible
docker-compose up
```

#### 3. Initialize Database

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create initial system data (statuses, roles, document types, etc.)
docker-compose exec web python manage.py create_initial_data

# Restore CMS content (Wagtail landing page)
docker-compose exec web python manage.py restore_cms

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

#### 4. Access Application

- **Web Application**: http://localhost:8000/
- **Django Admin**: http://localhost:8000/seim/admin/
- **Wagtail CMS Admin**: http://localhost:8000/cms/
- **API Documentation**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/

#### 5. Default Credentials

- **Admin User:**
  - Username: `admin`
  - Password: `admin123`
  - Email: `admin@seim.local`

- **Demo Student:**
  - Username: `student`
  - Password: `student123`
  - Email: `student@university.edu`

### Virtual Environment Setup (E2E Testing & Local Tools)

> **⚠️ Virtual environments are required for Selenium E2E tests and some local development tools that run from the host OS.**

#### When to Use Virtual Environment

**✅ Required for:**
- Selenium E2E tests (browser automation from host OS)
- Local development tools (code quality checks)
- Frontend testing (Jest tests)
- CI/CD script testing

**❌ Not Required for:**
- Backend development (use Docker)
- Database operations (use `docker-compose exec web`)
- Django management commands (use `docker-compose exec web python manage.py`)

#### Setup Virtual Environment

```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Environment Configuration

### Environment Variables

Create `.env` file from `env.example`:

```bash
# Django Configuration
DJANGO_ENV=dev
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://seimuser:seimpass@db:5432/seim

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# For SMTP: django.core.mail.backends.smtp.EmailBackend
# For AWS SES: django_ses.SESBackend

# Feature Flags
FEATURE_WEBSOCKET_NOTIFICATIONS=true
FEATURE_ADVANCED_SEARCH=true
FEATURE_CALENDAR_VIEW=true
FEATURE_NOTIFICATION_CENTER=true
```

### Settings Structure

The project uses modular settings:
- `seim/settings/base.py` - Common settings
- `seim/settings/development.py` - Development overrides
- `seim/settings/production.py` - Production overrides
- `seim/settings/test.py` - Test environment

Settings are selected via `DJANGO_SETTINGS_MODULE` environment variable.

## Development Workflow

### Daily Development

```bash
# Start services
docker-compose up -d

# Run migrations (if needed)
docker-compose exec web python manage.py migrate

# Access Django shell
docker-compose exec web python manage.py shell

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run security checks
make security-check

# Run all quality checks
make quality-check
```

### Running Tests

```bash
# Run all tests (Docker)
make test

# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run E2E tests (host OS, requires virtualenv)
# 1. Activate virtualenv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Ensure Django server is running
docker-compose up -d

# 3. Run Selenium tests
make test-selenium

# Run frontend tests (host OS, requires virtualenv)
make test-frontend

# Run with coverage
make test-coverage
```

### Frontend Development

```bash
# Build frontend assets
npm run build

# Development build with watch
npm run dev

# Run frontend tests
npm run test

# Run tests with coverage
npm run test:coverage

# Lint JavaScript
npm run lint

# Format JavaScript
npm run format
```

### Database Operations

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create migration
docker-compose exec web python manage.py makemigrations

# Access database shell
docker-compose exec db psql -U seimuser -d seim

# Backup database
docker-compose exec db pg_dump -U seimuser seim > backup.sql

# Restore database
docker-compose exec -T db psql -U seimuser seim < backup.sql
```

## Development Commands

### Docker Commands

```bash
# Start services
make docker-up

# Stop services
make docker-down

# View logs
make docker-logs

# Open shell in web container
make docker-shell

# Open database shell
make docker-db-shell

# Reset Docker environment (WARNING: deletes data)
make docker-reset
```

### Django Management Commands

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create initial data
docker-compose exec web python manage.py create_initial_data

# Restore CMS
docker-compose exec web python manage.py restore_cms

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Makefile Commands

See `Makefile` for comprehensive command list:

```bash
# Show all available commands
make help

# Development workflow
make setup              # Full development setup
make dev-workflow       # Complete dev workflow (setup, docs, tests)

# Testing
make test               # Run all tests
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-coverage      # Tests with coverage

# Documentation
make docs-all           # Generate all documentation
make docs-api           # API docs only
make docs-code          # Code docs only
make docs-sphinx-docker # Sphinx HTML docs

# Code Quality
make quality-check      # All quality checks
make format             # Format code
make lint               # Lint code

# Cache Management
make cache-test         # Test cache
make cache-clear        # Clear cache

# Cleanup
make clean              # Clean cache files
make clean-all          # Full cleanup (including Docker volumes)
```

## Code Organization

### Project Structure

```
SEIM/
├── accounts/          # User management
├── exchange/          # Exchange programs & applications
├── documents/         # Document management
├── notifications/     # Notifications system
├── grades/            # Grade translation
├── analytics/         # Analytics & reporting
├── application_forms/ # Dynamic forms (deprecated)
├── cms/               # Wagtail CMS
├── api/               # API routing
├── frontend/          # Frontend views
├── core/              # Shared utilities
├── dashboard/         # Dashboard views
├── plugins/           # Plugin system
├── seim/              # Django settings
├── static/            # Static files
├── templates/         # HTML templates
├── tests/             # Test suites
└── scripts/           # Utility scripts
```

### Coding Standards

#### Python
- Follow PEP 8
- Use type hints where appropriate
- Django best practices
- Service layer pattern for business logic

#### JavaScript
- ES6+ standards
- Module-based organization
- Consistent formatting (Prettier)
- ESLint compliance

#### CSS
- Bootstrap 5 utilities first
- Custom CSS for specific needs
- CSS custom properties for theming
- Mobile-first responsive design

#### Templates
- Django template best practices
- Reusable components
- Semantic HTML
- Accessibility considerations

## Service Layer Pattern

All business logic should be in service classes, not views or models.

### Example Service Usage

```python
# ✅ Good: Service handles business logic
from exchange.services import ApplicationService

def submit_application_view(request, application_id):
    application = Application.objects.get(id=application_id)
    ApplicationService.submit_application(application, request.user)
    return Response({"status": "submitted"})

# ❌ Bad: Business logic in view
def submit_application_view(request, application_id):
    application = Application.objects.get(id=application_id)
    # Business logic here - DON'T DO THIS
    if application.status.name != "draft":
        raise ValueError("...")
    # ... more logic
```

### Service Method Guidelines

1. **Static methods** - For stateless operations
2. **Transaction management** - Use `@transaction.atomic` for data consistency
3. **Error handling** - Raise appropriate exceptions
4. **Notifications** - Trigger notifications from services
5. **Validation** - Business rule validation in services

## Permission System

### Using Permissions

```python
# In views
from core.permissions import PermissionManager

if PermissionManager.user_has_permission(request.user, 'edit_application'):
    # Allow edit

# In DRF ViewSets
from core.permissions import HasPermission

class ApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [HasPermission('edit_application')]
```

### Permission Registry

All permissions are defined in `core/permissions.py` in `PERMISSION_REGISTRY`.

## Caching

### API Response Caching

```python
from core.cache import cache_api_response

@cache_api_response(timeout=600)
def list(self, request, *args, **kwargs):
    return super().list(request, *args, **kwargs)
```

### Cache Invalidation

```python
from core.cache import invalidate_cache_pattern

# Invalidate all program-related cache
invalidate_cache_pattern("api:ProgramViewSet:*")
```

## Background Tasks

### Creating Celery Tasks

```python
from celery import shared_task

@shared_task
def my_background_task(param1, param2):
    # Long-running operation
    pass
```

### Calling Tasks

```python
from .tasks import my_background_task

# Execute asynchronously
my_background_task.delay(param1, param2)

# Execute synchronously (testing)
my_background_task(param1, param2)
```

## Database Migrations

### Creating Migrations

```bash
# Create migration
docker-compose exec web python manage.py makemigrations

# Create migration for specific app
docker-compose exec web python manage.py makemigrations accounts
```

### Applying Migrations

```bash
# Apply all migrations
docker-compose exec web python manage.py migrate

# Apply migrations for specific app
docker-compose exec web python manage.py migrate accounts
```

## API Development

### Creating API Endpoints

```python
from rest_framework import viewsets
from core.permissions import HasPermission

class MyViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
    permission_classes = [HasPermission('view_model')]
    
    @cache_api_response(timeout=600)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

### Serializers

```python
from rest_framework import serializers

class MySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = "__all__"
    
    def validate(self, data):
        # Validation logic
        return data
```

## Frontend Development

### JavaScript Modules

```javascript
// Import from modules
import { SEIM_API } from './modules/api-enhanced.js';
import { SEIM_LOGGER } from './modules/logger.js';

// Use modules
SEIM_API.get('/api/programs/').then(data => {
    SEIM_LOGGER.info('Programs loaded', data);
});
```

### Adding New Components

1. Create component template in `templates/components/`
2. Add JavaScript in `static/js/modules/` if needed
3. Add CSS in `static/css/components/` if needed
4. Import in relevant entry point

## Testing

### Writing Tests

```python
# Unit test example
from django.test import TestCase
from exchange.services import ApplicationService

class ApplicationServiceTest(TestCase):
    def test_submit_application(self):
        # Test implementation
        pass
```

### Test Organization

- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/e2e_playwright/` - Playwright E2E tests
- `tests/selenium/` - Selenium E2E tests
- `tests/frontend/` - Frontend JavaScript tests

### Running Specific Tests

```bash
# Test specific app
docker-compose exec web pytest tests/unit/accounts/

# Test specific file
docker-compose exec web pytest tests/unit/accounts/test_models.py

# Test with coverage
docker-compose exec web pytest --cov=accounts tests/unit/accounts/
```

## Debugging

### Django Debugging

```bash
# Django shell with imports
docker-compose exec web python manage.py shell_plus

# View Django logs
docker-compose logs -f web

# Check database queries
# Add to settings: DEBUG = True, then check Django Debug Toolbar
```

### Frontend Debugging

```javascript
// Use logger module
import { SEIM_LOGGER } from './modules/logger.js';

SEIM_LOGGER.debug('Debug message', { data });
SEIM_LOGGER.error('Error occurred', error);
```

## Git Workflow

### Branching

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push branch
git push origin feature/your-feature-name
```

### Commit Messages

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Common Tasks

### Adding a New Model

1. Create model in appropriate app
2. Create migration: `python manage.py makemigrations`
3. Run migration: `python manage.py migrate`
4. Create serializer
5. Create service (if business logic needed)
6. Create ViewSet
6. Register in API router
7. Add tests

### Adding a New API Endpoint

1. Create/update serializer
2. Create/update ViewSet
3. Register in `api/urls.py` or app `urls.py`
4. Add permission class
5. Add caching if appropriate
6. Add tests
7. Update API documentation

### Adding Frontend Features

1. Create JavaScript module (if needed)
2. Add template (if needed)
3. Add CSS (if needed)
4. Import in entry point
5. Add tests

## Troubleshooting

### Common Issues

**Issue: Database connection errors**
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

**Issue: Redis connection errors**
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

**Issue: Static files not loading**
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check static files volume
docker-compose ps web
```

**Issue: Migration conflicts**
```bash
# Show migration status
docker-compose exec web python manage.py showmigrations

# Fake migration (if needed, be careful)
docker-compose exec web python manage.py migrate --fake
```

**Issue: Celery tasks not running**
```bash
# Check Celery worker
docker-compose logs celery

# Restart Celery
docker-compose restart celery celery-beat
```

## Production Deployment

### Deployment Checklist

1. Update environment variables for production
2. Set `DJANGO_ENV=production`
3. Set `DEBUG=False`
4. Configure production database
5. Set up email backend (SMTP or AWS SES)
6. Configure static file serving (WhiteNoise or CDN)
7. Set up SSL certificates
8. Configure domain in `ALLOWED_HOSTS`
9. Run migrations
10. Collect static files
11. Create superuser
12. Set up monitoring

### Production Commands

```bash
# Build production images
make build-prod

# Deploy to production
make deploy-prod

# Check production status
make prod-status

# View production logs
make prod-logs

# Backup production
make prod-backup
```

---

_Generated using BMAD Method `document-project` workflow (Exhaustive Scan)_
