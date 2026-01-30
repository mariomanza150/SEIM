# SEIM Source Tree Analysis

**Generated:** 2025-01-27  
**Project Root:** `c:\Users\mario\OneDrive\Documents\SEIM`

## Project Structure Overview

SEIM follows a standard Django project structure with clear separation of concerns:

```
SEIM/
├── accounts/              # User management and authentication
├── analytics/             # Reporting and metrics
├── api/                   # REST API endpoints and routing
├── application_forms/     # Dynamic form builder and management
├── cms/                   # Wagtail CMS pages and content
├── core/                  # Shared utilities, base models, permissions
├── dashboard/             # Admin and user dashboards
├── documents/             # Document management system
├── exchange/              # Exchange program and application logic
├── frontend/              # Django frontend views and URLs
├── grades/                # Grade translation system
├── internacional/         # Internationalization utilities
├── notifications/         # Email and notification system
├── plugins/               # Modular plugin system
├── seim/                  # Django project settings and configuration
├── static/                # Static files (CSS, JavaScript, images)
├── templates/             # HTML templates
├── tests/                 # Test suites
├── docs/                  # Project documentation (BMAD generated)
├── documentation/         # Existing project documentation
└── scripts/               # Utility scripts
```

## Critical Directories

### Backend Applications (`*/`)

#### `accounts/`
**Purpose:** User management, authentication, authorization, and user profiles
- **Models:** User (custom), Profile, Role, Permission, UserSettings, UserSession
- **Views:** Registration, login, profile management, user management (admin)
- **Services:** Account management, authentication workflows
- **Features:** Email verification, password reset, account lockout, role-based access

#### `exchange/`
**Purpose:** Core business logic for exchange programs and applications
- **Models:** Program, Application, ApplicationStatus, Comment, TimelineEvent, SavedSearch
- **Views:** Program and application CRUD, eligibility checking, status transitions
- **Services:** ApplicationService (workflow management, eligibility validation)
- **Filters:** Advanced filtering for programs and applications
- **Features:** Program cloning, eligibility validation with grade translation, saved searches

#### `documents/`
**Purpose:** Document upload, validation, and management
- **Models:** Document, DocumentType, DocumentValidation, DocumentResubmissionRequest, DocumentComment
- **Views:** Document CRUD, validation, resubmission requests
- **Services:** Document processing, virus scanning integration
- **Features:** File upload, validation workflow, comments, resubmission requests

#### `notifications/`
**Purpose:** Email and in-app notification system
- **Models:** Notification, NotificationType, NotificationPreference, Reminder
- **Views:** Notification management, preferences
- **Services:** NotificationService (sending notifications, WebSocket broadcasting)
- **Tasks:** Async email sending via Celery
- **Consumers:** WebSocket consumers for real-time notifications
- **Features:** Email notifications, in-app notifications, real-time WebSocket updates, reminders

#### `grades/`
**Purpose:** International grade scale conversion system
- **Models:** GradeScale, GradeValue, GradeTranslation
- **Services:** GradeTranslationService (grade conversion logic)
- **Features:** Support for multiple grading scales (US GPA, ECTS, UK, German, French, Canadian), automatic conversion

#### `analytics/`
**Purpose:** Reporting, metrics, and dashboard data
- **Models:** Analytics models for tracking
- **Views:** Dashboard metrics, reports, analytics endpoints
- **Services:** Analytics calculations and aggregations
- **Features:** Real-time metrics, program-specific analytics, admin dashboard

#### `application_forms/`
**Purpose:** Dynamic form builder and form submission management
- **Models:** FormType, FormSubmission
- **Views:** Form builder UI, form list, submission management
- **Features:** JSON schema-based forms, form submissions, integration with exchange programs

#### `cms/`
**Purpose:** Wagtail CMS integration for public landing pages
- **Models:** Wagtail page models (HomePage, StandardPage, BlogPost, ProgramPage, etc.)
- **Templates:** CMS page templates and content blocks
- **Features:** Rich content management, SEO optimization, blog posts, program pages, FAQs

#### `api/`
**Purpose:** REST API routing and organization
- **Views:** API endpoint aggregation
- **URLs:** Main API router configuration
- **Features:** Centralized API endpoint registration

#### `frontend/`
**Purpose:** Django frontend views and URL routing
- **Views:** Frontend page views
- **URLs:** Frontend URL routing
- **Features:** Dashboard, programs, applications, documents pages

#### `core/`
**Purpose:** Shared utilities, base models, and project-wide logic
- **Models:** UUIDModel, TimeStampedModel (base classes)
- **Permissions:** PermissionManager for role-based permissions
- **Cache:** API response caching middleware and utilities
- **Management Commands:** Utility commands (create_initial_data, etc.)
- **Features:** Common base classes, shared utilities, caching infrastructure

#### `dashboard/`
**Purpose:** Admin and user dashboard interfaces
- **Views:** Dashboard views
- **Models:** Dashboard-specific models
- **Features:** Role-based dashboards

#### `plugins/`
**Purpose:** Modular plugin system for custom workflows
- **Models:** Plugin models
- **Views:** Plugin views
- **Features:** Extensible plugin architecture

### Configuration (`seim/`)

#### `seim/settings/`
**Purpose:** Django settings split by environment
- **base.py** - Common settings for all environments
- **development.py** - Development-specific settings
- **production.py** - Production-specific settings
- **test.py** - Test environment settings

**Key Configuration Areas:**
- Installed apps (Django apps, third-party, local apps)
- Database configuration (PostgreSQL)
- Cache configuration (Redis)
- Celery configuration
- REST Framework settings
- JWT settings
- Wagtail CMS settings
- Channels/WebSocket settings
- Security settings
- Internationalization (i18n) settings

#### Root URL Configuration (`seim/urls.py`)
**Purpose:** Main URL routing
- Wagtail CMS routes (`/cms/`)
- SEIM application routes (`/seim/`)
- API routes (`/api/`)
- Health check endpoint
- Internationalization routes

### Frontend Assets

#### `static/js/`
**Purpose:** Client-side JavaScript modules and entry points

**Entry Points:**
- `main.js` - Main application initialization
- `dashboard.js` - Dashboard functionality
- `applications.js` - Application management
- `programs.js` - Program browsing
- `documents.js` - Document management
- `auth_entry.js` - Authentication entry point

**Modules (`static/js/modules/`):**
- **API:** `api.js`, `api-enhanced.js` - API client utilities
- **Auth:** `auth.js`, `auth-unified.js` - Authentication handling
- **UI:** `ui.js`, `ui-enhanced.js`, `bootstrap_helpers.js` - UI utilities
- **Notifications:** `notifications.js`, `notification-center.js`, `toast-notifications.js`
- **WebSocket:** `websocket-client.js` - Real-time communication
- **Features:** `applications_list.js`, `applications_actions.js`, `programs_list.js`, `documents_list.js`
- **Forms:** `dynamic-forms.js`, `dynamic-loader.js` - Dynamic form handling
- **File Upload:** `file_upload.js` - File upload functionality
- **Utilities:** `utils.js`, `logger.js`, `error-handler.js`, `performance.js`, `security.js`, `validators.js`
- **Accessibility:** `accessibility.js`, `accessibility-tester.js`
- **Features:** `advanced-search.js`, `calendar.js`, `saved-searches.js`, `preferences.js`

#### `static/css/`
**Purpose:** Stylesheets organized by purpose

**Main Stylesheets:**
- `main.css` - Main application styles
- `accessibility.css` - Accessibility enhancements
- `dark-mode.css` - Dark mode theme
- `critical.css` - Critical above-the-fold styles
- `uadec-styles.css` - UAdeC branding styles
- `wagtail_admin_custom.css` - Wagtail admin customizations

**Organized Stylesheets:**
- **Components** (`components/`): `buttons.css`, `cards.css`, `forms.css`, `tables.css`
- **Layouts** (`layouts/`): `base.css`, `navigation.css`
- **Utilities** (`utilities/`): `colors.css`, `spacing.css`, `typography.css`

### Templates

#### `templates/`
**Purpose:** HTML templates for Django views

**Base Templates:**
- `base.html` - Base template with navigation, footer, common includes

**Frontend Templates** (`templates/frontend/`):
- **Auth:** `auth/login.html`, `auth/register.html`, `auth/password_reset.html`
- **Dashboard:** `dashboard.html`, `admin/dashboard.html`, `coordinator/dashboard.html`
- **Applications:** `applications/list.html`, `applications/detail.html`, `applications/form.html`
- **Programs:** `programs/list.html`, `programs/form.html`
- **Documents:** `documents/list.html`, `documents/detail.html`, `documents/form.html`
- **Profile:** `profile.html`
- **Settings:** `sessions.html`, `settings.html`

**Components** (`templates/components/`):
- `navigation/navbar.html` - Main navigation
- `footer.html` - Footer component
- `notification-center.html` - Notification center UI
- `language-switcher.html` - Language selection
- `messages.html` - Django messages display
- `forms/search_form.html` - Search form component
- `tables/data_table.html` - Data table component

**CMS Templates** (`cms/templates/cms/`):
- Page templates: `home_page.html`, `standard_page.html`, `program_page.html`, `blog_post_page.html`, etc.
- Blocks: `blocks/hero_block.html`, `blocks/card_grid_block.html`, `blocks/form_block.html`, etc.

### Tests

#### `tests/`
**Purpose:** Comprehensive test suites

**Test Organization:**
- **Unit Tests** (`tests/unit/`): Test individual components
  - `accounts/` - User and authentication tests
  - `analytics/` - Analytics service tests
  - `documents/` - Document management tests
  - `exchange/` - Exchange logic tests
  - `notifications/` - Notification tests
  - etc.
- **Integration Tests** (`tests/integration/`): Test API endpoints and workflows
- **E2E Tests:**
  - **Selenium** (`tests/selenium/`): Browser automation tests (run from host OS)
  - **Playwright** (`tests/e2e_playwright/`): Modern E2E tests with video recordings
- **Frontend Tests** (`tests/frontend/`): JavaScript/React component tests

### Documentation

#### `docs/`
**Purpose:** BMAD-generated project documentation (this directory)
- Project overview, architecture, API contracts, data models, etc.

#### `documentation/`
**Purpose:** Existing project documentation
- Developer guides, API docs, architecture docs, deployment guides, etc.

### Scripts

#### `scripts/`
**Purpose:** Utility scripts for development and maintenance
- `download_uadec_assets.py` - Asset downloading
- `code_quality.py` - Code quality checks
- `dashboard_debug.py` - Debugging utilities
- `setup_demo.py` - Demo data setup
- `seed_e2e_test_data.py` - E2E test data seeding
- Frontend build and optimization scripts

## Entry Points

### Django Entry Points
- `manage.py` - Django management command entry point
- `seim/wsgi.py` - WSGI application (for Gunicorn)
- `seim/asgi.py` - ASGI application (for Daphne/WebSocket support)

### Frontend Entry Points
- `static/js/main.js` - Main JavaScript initialization
- `static/js/dashboard.js` - Dashboard entry point
- `static/js/applications.js` - Applications entry point
- `static/js/programs.js` - Programs entry point
- `static/js/documents.js` - Documents entry point
- `static/js/auth_entry.js` - Authentication entry point

### Build Configuration
- `webpack.config.js` - Webpack configuration for JavaScript bundling
- `package.json` - Node.js dependencies and scripts
- `requirements.txt` - Python dependencies

## File Organization Patterns

### Models
- All domain models extend `UUIDModel` and `TimeStampedModel` from `core.models`
- Models organized by feature/app
- Indexes defined for common query patterns

### Views
- ViewSets for API endpoints (DRF)
- Function-based and class-based views for frontend
- Service layer pattern - business logic in services, not views

### Services
- Business logic encapsulated in service classes
- Static methods for stateless operations
- Transaction management for data consistency

### Static Files
- JavaScript modules for code organization
- CSS organized by component/layout/utility
- Webpack for bundling and optimization

### Templates
- Base template with common structure
- Component templates for reusable UI elements
- App-specific templates organized by feature

## Integration Points

### Database
- PostgreSQL for production
- Django ORM for data access
- Migrations in each app's `migrations/` directory

### Cache
- Redis for caching and Celery message broker
- API response caching via middleware
- Cache invalidation on mutations

### Background Tasks
- Celery for async tasks (email sending, etc.)
- Redis as message broker
- Task definitions in app `tasks.py` files

### WebSocket
- Django Channels for WebSocket support
- Redis channel layer
- Consumers for real-time notifications

### External Services
- Email: SMTP or AWS SES
- File storage: Local or cloud (S3, etc.)
- Virus scanning: ClamAV integration (mock in development)

---

_Generated using BMAD Method `document-project` workflow (Exhaustive Scan)_
