# SEIM Architecture Documentation

**Generated:** 2025-01-27  
**Project:** SEIM - Student Exchange Information Manager  
**Architecture Pattern:** Service-Oriented Layered Architecture (Clean Architecture principles)

## Executive Summary

SEIM is a comprehensive Django-based web application for managing student exchange programs. The system follows Clean Architecture principles with clear separation between presentation, application, domain, and infrastructure layers. It uses a service-oriented design where business logic is encapsulated in service modules, keeping views thin and models focused on data representation.

## Architecture Pattern

### Clean Architecture Layers

**1. Presentation Layer:**
- Django templates (server-side rendering)
- JavaScript modules (client-side interactivity)
- REST API endpoints (DRF ViewSets)
- WebSocket consumers (real-time notifications)

**2. Application Layer:**
- Service classes (business logic encapsulation)
- Workflow management (ApplicationService, DocumentService, etc.)
- Permission management (PermissionManager)
- Cache management (CacheManager, APICacheMiddleware)

**3. Domain Layer:**
- Django models (data representation)
- Business rules validation
- Domain-specific logic in model methods

**4. Infrastructure Layer:**
- Database (PostgreSQL)
- Cache (Redis)
- Message broker (Redis for Celery)
- File storage (local or cloud)
- External services (email, virus scanning)

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                             │
│  ┌──────────────────────┐         ┌───────────────────────────┐    │
│  │  Public Pages        │         │  Authenticated Pages      │    │
│  │  (Wagtail CMS)       │         │  (Django Templates +      │    │
│  │  - Home, Blog        │         │   Bootstrap 5 +           │    │
│  │  - Program Pages     │         │   ES6+ JavaScript)        │    │
│  │  - Info Pages        │         │  - Dashboard              │    │
│  └──────────────────────┘         │  - Applications           │    │
│                                    │  - Documents              │    │
│                                    └───────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Admin Interfaces                               │
│  ┌──────────────────────┐         ┌───────────────────────────┐    │
│  │  Wagtail CMS Admin   │         │  Django Admin             │    │
│  │  - Content Pages     │         │  - System Config          │    │
│  │  - Blog Management   │         │  - User Management        │    │
│  │  - Forms             │         │  - Exchange Workflows     │    │
│  └──────────────────────┘         └───────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│   API Layer (DRF) ◄──────────────────────────────────────┐        │
│   - REST API                                              │        │
│   - JWT Authentication                                    │        │
│   - OpenAPI Documentation                                 │        │
│   - WebSocket (Django Channels)                          │        │
└───────────────────────────────────────────────────────────┼────────┘
                                     │                      │
                                     ▼                      ▼
┌────────────────────────────────────────┐   ┌──────────────────────┐
│   Business Logic Layer (Services)      │   │  External Services   │
│   - ApplicationService                 │   │  - Email (Celery)    │
│   - DocumentService                    │   │  - Redis (Cache)     │
│   - NotificationService                │   │  - File Storage      │
│   - GradeTranslationService            │   │  - Virus Scanning    │
│   - AnalyticsService                   │   │  - WebSocket         │
└────────────────────────────────────────┘   └──────────────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │   Data Layer (ORM)       │
                       │   - Django Models        │
                       │   - Wagtail Pages        │
                       │   - Query Optimization   │
                       └──────────────────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │   Database               │
                       │   (PostgreSQL 15+)       │
                       └──────────────────────────┘
```

## Technology Stack

### Backend Framework
- **Django 5.1.4** - Web framework with ORM
- **Django REST Framework 3.16.1** - RESTful API framework
- **Wagtail 6.3** - CMS for content management

### Database & Caching
- **PostgreSQL 15+** - Primary database (production)
- **Redis 7.2+** - Cache and Celery message broker
- **Django ORM** - Database abstraction layer

### Background Processing
- **Celery 5.5.3** - Async task queue
- **django-celery-beat 2.8.1** - Scheduled tasks
- **django-celery-results 2.6.0** - Task results backend

### Authentication & Security
- **JWT (djangorestframework-simplejwt 5.5.1)** - Token-based API authentication
- **Django Sessions** - Web-based authentication
- **Account lockout policy** - Brute force protection
- **Email verification** - User account verification

### Frontend Technologies
- **Bootstrap 5** - CSS framework
- **JavaScript ES6+** - Client-side logic
- **Webpack 5** - JavaScript bundling
- **Django Templates** - Server-side rendering

### WebSocket & Real-time
- **Django Channels 4.3.1** - WebSocket support
- **channels-redis 4.3.0** - Channel layer backend
- **Daphne 4.2.1** - ASGI server

### API Documentation
- **drf-spectacular 0.29.0** - OpenAPI/Swagger documentation

### Development & Deployment
- **Docker & Docker Compose** - Containerization
- **Gunicorn** - WSGI server (production)
- **WhiteNoise** - Static file serving
- **Nginx** - Reverse proxy (production)

## Application Structure

### Core Django Apps

#### `accounts/` - User Management
**Purpose:** User authentication, authorization, and profile management

**Key Components:**
- **Models:** User (custom), Profile, Role, Permission, UserSettings, UserSession
- **Views:** Registration, login, profile management, user CRUD (admin)
- **Services:** AccountService (registration, authentication, password reset)
- **Serializers:** User, Profile, Registration, Login, Password Reset serializers
- **Permissions:** Role-based access control (Student, Coordinator, Admin)

**Key Features:**
- Email verification workflow
- Password reset functionality
- Account lockout policy (5 failed attempts = 30 min lockout)
- Multi-role support (users can have multiple roles)
- User settings (theme, notifications, privacy)
- Session management and tracking

#### `exchange/` - Exchange Programs
**Purpose:** Core business logic for exchange programs and applications

**Key Components:**
- **Models:** Program, Application, ApplicationStatus, Comment, TimelineEvent, SavedSearch
- **Views:** ProgramViewSet, ApplicationViewSet, CommentViewSet, TimelineEventViewSet, SavedSearchViewSet
- **Services:** ApplicationService (workflow management, eligibility validation)
- **Filters:** ProgramFilter, ApplicationFilter (advanced filtering)
- **Serializers:** Program, Application, Comment, TimelineEvent, SavedSearch serializers

**Key Features:**
- Program management with eligibility criteria (GPA, language, age)
- Application workflow state machine (draft → submitted → under_review → approved/rejected → completed/cancelled)
- Eligibility validation with grade translation support
- Program cloning functionality
- Saved searches for coordinators/admins
- Timeline events for audit logging
- Comments on applications (internal/visible)

#### `documents/` - Document Management
**Purpose:** Document upload, validation, and management

**Key Components:**
- **Models:** Document, DocumentType, DocumentValidation, DocumentResubmissionRequest, DocumentComment
- **Views:** DocumentViewSet, DocumentTypeViewSet, DocumentValidationViewSet, DocumentResubmissionRequestViewSet, DocumentCommentViewSet
- **Services:** DocumentService (upload, validation, resubmission)
- **Tasks:** scan_document_virus (async virus scanning)

**Key Features:**
- File upload with drag-and-drop support
- File type and size validation (PDF, JPEG, PNG; max 10MB)
- Virus scanning integration (ClamAV, mock for development)
- Document validation workflow
- Resubmission requests (max 3 per document)
- Document comments (internal/visible to students)

#### `notifications/` - Notification System
**Purpose:** Email and in-app notification system

**Key Components:**
- **Models:** Notification, NotificationType, NotificationPreference, Reminder
- **Views:** NotificationViewSet, NotificationPreferenceViewSet, ReminderViewSet
- **Services:** NotificationService (sending notifications, WebSocket broadcasting)
- **Tasks:** send_notification_by_id, send_deadline_reminders (async email sending)
- **Consumers:** NotificationConsumer (WebSocket for real-time notifications)

**Key Features:**
- Email notifications (SMTP or AWS SES)
- In-app notifications
- Real-time WebSocket notifications
- Notification preferences per user
- Reminders for deadlines and events
- Action links in notifications (direct links to related resources)

#### `grades/` - Grade Translation System
**Purpose:** International grade scale conversion

**Key Components:**
- **Models:** GradeScale, GradeValue, GradeTranslation
- **Services:** GradeTranslationService (grade conversion logic)
- **Views:** Grade scale and value management (admin)

**Key Features:**
- Support for multiple grading scales:
  - US GPA 4.0
  - ECTS (European Credit Transfer System)
  - UK (First Class, Upper Second, etc.)
  - German (1.0-5.0, reverse scale)
  - French (0-20)
  - Canadian (0-4.33)
- Automatic grade conversion between scales
- GPA equivalent calculation for cross-scale comparison
- Direct translation mappings
- Confidence levels for translations

#### `analytics/` - Analytics & Reporting
**Purpose:** Reporting, metrics, and dashboard data

**Key Components:**
- **Models:** Report, Metric, DashboardConfig
- **Views:** ReportViewSet, MetricViewSet, DashboardConfigViewSet, AdminDashboardViewSet
- **Services:** AnalyticsService (metrics calculation, report generation)

**Key Features:**
- Admin dashboard metrics
- Program-specific analytics
- Application status breakdowns
- User activity tracking
- Custom dashboard configurations
- System performance metrics
- Activity timeline

#### `application_forms/` - Dynamic Form Builder
**Purpose:** Dynamic form builder and form submission management

**Key Components:**
- **Models:** FormType, FormSubmission
- **Views:** FormTypeViewSet, FormSubmissionViewSet, EnhancedFormBuilderView
- **Services:** FormSubmissionService (form validation, submission handling)

**Key Features:**
- JSON schema-based forms
- Visual form builder UI
- Integration with exchange programs
- Form submission tracking
- Response validation

**Note:** This app is being deprecated in favor of Wagtail FormPage migration.

#### `cms/` - Wagtail CMS Integration
**Purpose:** Content management for public landing pages

**Key Components:**
- **Models:** Wagtail page models (HomePage, StandardPage, BlogPost, ProgramPage, FAQPage, etc.)
- **Templates:** CMS page templates and content blocks
- **Blocks:** Rich content blocks (hero, cards, forms, embeds, etc.)

**Key Features:**
- Rich content management with StreamField
- Blog system
- Program listing pages
- FAQ system
- SEO optimization
- Publishing workflows
- Multi-language support

#### `api/` - REST API Organization
**Purpose:** Centralized API routing and organization

**Key Components:**
- **Views:** API endpoint aggregation
- **URLs:** Main API router configuration
- **Documentation:** OpenAPI/Swagger integration

#### `frontend/` - Frontend Views
**Purpose:** Django frontend views and URL routing

**Key Components:**
- **Views:** Frontend page views
- **URLs:** Frontend URL routing

#### `core/` - Shared Utilities
**Purpose:** Project-wide shared utilities and base classes

**Key Components:**
- **Models:** UUIDModel, TimeStampedModel (base classes)
- **Permissions:** PermissionManager, unified permission registry
- **Cache:** CacheManager, APICacheMiddleware, caching decorators
- **Management Commands:** create_initial_data, test_urls

**Key Features:**
- UUID primary keys for all domain models
- Automatic timestamping (created_at, updated_at)
- Unified permission system (PERMISSION_REGISTRY)
- API response caching
- Cache invalidation patterns

#### `dashboard/` - Dashboard Views
**Purpose:** Admin and user dashboard interfaces

**Key Components:**
- **Views:** Dashboard views
- **Models:** Dashboard-specific models

#### `plugins/` - Plugin System
**Purpose:** Modular plugin system for custom workflows

**Key Components:**
- **Models:** Plugin models
- **Views:** Plugin views

**Status:** Extensibility architecture in place

## Data Architecture

### Database Schema

**Core Tables:**
- `accounts_user` - Custom user model
- `accounts_profile` - User profiles with GPA, language, grade scale
- `accounts_role` - User roles
- `accounts_permission` - Custom permissions
- `accounts_usersettings` - User preferences
- `accounts_usersession` - Session tracking

- `exchange_program` - Exchange programs
- `exchange_application` - Student applications
- `exchange_applicationstatus` - Status workflow states
- `exchange_comment` - Application comments
- `exchange_timelineevent` - Audit trail
- `exchange_savedsearch` - Saved search filters

- `documents_document` - Uploaded documents
- `documents_documenttype` - Document types
- `documents_documentvalidation` - Validation records
- `documents_documentresubmissionrequest` - Resubmission requests
- `documents_documentcomment` - Document comments

- `notifications_notification` - Notification instances
- `notifications_notificationtype` - Notification types
- `notifications_notificationpreference` - User preferences
- `notifications_reminder` - Event reminders

- `grades_gradescale` - Grade scales
- `grades_gradevalue` - Grade values within scales
- `grades_gradetranslation` - Direct translation mappings

- `application_forms_formtype` - Dynamic form definitions
- `application_forms_formsubmission` - Form submissions

- `analytics_report` - Analytics reports
- `analytics_metric` - Individual metrics
- `analytics_dashboardconfig` - Dashboard configurations

### Relationships

**User → Profile:** One-to-One  
**User → Roles:** Many-to-Many  
**User → Applications:** One-to-Many (as student)  
**User → Documents:** One-to-Many (as uploaded_by)  
**User → Notifications:** One-to-Many (as recipient)  
**User → Saved Searches:** One-to-Many

**Program → Applications:** One-to-Many  
**Application → Documents:** One-to-Many  
**Application → Comments:** One-to-Many  
**Application → Timeline Events:** One-to-Many  
**Application → Form Submissions:** One-to-Many

**Document → Validations:** One-to-Many  
**Document → Resubmission Requests:** One-to-Many  
**Document → Comments:** One-to-Many

**Profile → Grade Scale:** Foreign Key (nullable)

**Grade Scale → Grade Values:** One-to-Many  
**Grade Value → Translations:** One-to-Many (as source or target)

### Indexes

Strategic indexes for performance:
- User/Application relationships (student, status, withdrawn)
- Document lookups (application, type, uploaded_by, validation status)
- Notification queries (recipient, read status, sent date)
- Saved searches (user, type, default)
- Grade lookups (scale, code, active status, GPA equivalents)
- Timeline/audit queries (created_at descending)

## Service Layer Architecture

### Service Classes

**ApplicationService:**
- `check_eligibility()` - Comprehensive eligibility validation
- `submit_application()` - Submit application with validation
- `transition_status()` - Status workflow transitions
- `withdraw_application()` - Application withdrawal
- `add_comment()` - Add comments to applications
- `process_dynamic_form_submission()` - Handle dynamic form data

**DocumentService:**
- `validate_file_type_and_size()` - File validation
- `virus_scan()` - Virus scanning
- `upload_document()` - Document upload workflow
- `validate_document()` - Document validation
- `request_resubmission()` - Request document resubmission
- `can_replace_document()` - Check replacement permissions

**NotificationService:**
- `send_notification()` - Send notification with action links
- `_broadcast_notification()` - WebSocket broadcasting
- `is_enabled()` - Check user preferences
- `set_preference()` - Update user preferences

**GradeTranslationService:**
- `translate_grade()` - Translate between grade scales
- `_get_direct_translation()` - Direct translation lookup
- `_translate_by_gpa_equivalent()` - GPA-based translation

**AccountService:**
- `register_user()` - User registration
- `authenticate_user()` - User authentication
- `verify_email()` - Email verification
- `reset_password()` - Password reset
- `change_password()` - Password change

**AnalyticsService:**
- `get_dashboard_metrics()` - Admin dashboard metrics
- `get_program_metrics()` - Program-specific analytics
- `trigger_report()` - Generate reports

### Permission System

**Unified Permission Registry (PERMISSION_REGISTRY):**
- Centralized permission definitions
- Role-based permission mapping
- Permission categories:
  - Application permissions
  - Document permissions
  - Program permissions
  - User management permissions
  - Analytics & reporting permissions
  - System administration permissions
  - Notifications permissions
  - Comments & communication permissions

**PermissionManager:**
- `user_has_permission()` - Check user permission
- `get_user_permissions()` - Get all user permissions
- `get_role_permissions()` - Get role permissions
- `validate_permission()` - Validate permission exists

**DRF Permission Classes:**
- `HasPermission` - Generic permission class
- `IsOwnerOrAdmin` - Ownership-based access
- `IsCoordinatorOrAdmin` - Role-based access
- `IsAdminOrReadOnly` - Admin write, all read
- `IsStudentOrReadOnly` - Student write restrictions

## API Architecture

### REST API Design

**Base URL:** `/api/`

**Authentication:**
- JWT tokens via `/api/token/`
- Session authentication for web views
- Token refresh via `/api/token/refresh/`

**Pagination:**
- PageNumberPagination (default: 20 items/page)
- Query parameters: `page`, `page_size`

**Filtering:**
- Django Filter Backend
- Search filtering on specified fields
- Ordering via `ordering` parameter

**Caching:**
- API response caching (5-10 minutes for read operations)
- Cache invalidation on mutations
- User-specific cache keys

**Rate Limiting:**
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Burst rate (login/register): 10 requests/minute

### WebSocket Architecture

**Connection:** `ws://localhost:8000/ws/notifications/`

**Consumer:** NotificationConsumer
- Authenticated connections only
- Personal notification channels (`notifications_{user_id}`)
- Real-time notification delivery
- Mark as read via WebSocket

**Channel Layer:** Redis (channels-redis)
- Group messaging
- Broadcast to user groups

## Frontend Architecture

### JavaScript Module System

**Entry Points:**
- `main.js` - Main initialization
- `dashboard.js`, `applications.js`, `programs.js`, `documents.js` - Feature-specific entry points

**Module Organization:**
- Core modules (API, auth, UI, utils)
- Feature modules (applications, programs, documents)
- Utility modules (logger, error-handler, performance)
- Specialized modules (notifications, calendar, search)

**Build System:**
- Webpack 5 with code splitting
- Production optimizations (minification, compression)
- Development source maps

### CSS Architecture

**Organization:**
- Main stylesheets (core, accessibility, dark mode)
- Component styles (buttons, cards, forms, tables)
- Layout styles (base, navigation)
- Utility classes (colors, spacing, typography)

**Theming:**
- CSS custom properties for colors
- Dark/light mode support
- High contrast mode
- Reduced motion support

### Template System

**Base Template:**
- Common structure (navigation, footer)
- Theme initialization
- WebSocket connection
- CSRF protection

**Component Templates:**
- Reusable UI components
- Navigation components
- Form components

**Page Templates:**
- Feature-specific pages
- Role-based dashboards
- CMS pages (Wagtail)

## Security Architecture

### Authentication & Authorization

**Multi-Factor Authentication Support:**
- Email verification required for registration
- Password reset via email token
- Session management with tracking

**Account Security:**
- Account lockout after 5 failed login attempts (30 minutes)
- Password validation (Django validators)
- Secure password storage (Django's PBKDF2)

**API Security:**
- JWT token expiration (60 minutes access, 1 day refresh)
- Token rotation on refresh
- Token blacklisting support
- CSRF protection for web views

### Permission Model

**Role-Based Access Control (RBAC):**
- Three primary roles: Student, Coordinator, Admin
- Multi-role support (users can have multiple roles)
- Permission registry for centralized management
- Object-level permissions (ownership checks)

**Permission Categories:**
- View permissions (own vs all)
- Edit permissions (own vs any)
- Delete permissions
- Admin-only permissions

### Data Security

**File Upload Security:**
- File type validation (MIME type checking)
- File size limits (10MB)
- Virus scanning integration
- Secure file storage

**Input Validation:**
- Serializer-level validation
- Model-level validation
- Service-level business rule validation
- XSS prevention in templates

## Caching Strategy

### Cache Layers

**1. API Response Caching:**
- Cache timeout: 5-10 minutes (read operations)
- Cache invalidation on mutations
- User-specific cache keys
- Pattern-based invalidation

**2. Database Query Caching:**
- Selective query caching
- CacheManager for programmatic caching
- Redis backend

**3. Static File Caching:**
- WhiteNoise for static files
- Browser caching headers
- CDN-ready (production)

### Cache Management

**CacheManager:**
- Centralized cache operations
- Cache key generation
- Timeout management
- Pattern-based clearing

**Cache Decorators:**
- `@cache_api_response` - API endpoint caching
- `@cache_user_data` - User-specific caching
- `invalidate_cache_pattern()` - Pattern invalidation

## Background Tasks Architecture

### Celery Configuration

**Message Broker:** Redis  
**Result Backend:** django-celery-results  
**Task Serialization:** JSON

**Task Categories:**
- Email sending (async)
- Virus scanning (async)
- Deadline reminders (scheduled)
- Report generation (async)

### Task Definitions

**Email Tasks:**
- `send_notification_by_id` - Send email notification
- `send_deadline_reminders` - Scheduled reminder notifications

**Document Tasks:**
- `scan_document_virus` - Async virus scanning

## Deployment Architecture

### Container Architecture

**Services:**
- `web` - Django application (Daphne ASGI server)
- `db` - PostgreSQL database
- `redis` - Cache and message broker
- `celery` - Background task worker
- `celery-beat` - Scheduled task scheduler

**Production Stack:**
- Gunicorn (WSGI) or Daphne (ASGI)
- Nginx (reverse proxy)
- PostgreSQL (database)
- Redis (cache/broker)
- WhiteNoise (static files)

### Environment Configuration

**Settings Modules:**
- `base.py` - Common settings
- `development.py` - Development environment
- `production.py` - Production environment
- `test.py` - Test environment

**Environment Variables:**
- Database configuration
- Redis configuration
- Email configuration (SMTP/AWS SES)
- Secret keys
- Feature flags

## Testing Architecture

### Test Organization

**Unit Tests:**
- Model tests
- Service tests
- Serializer tests
- Utility tests

**Integration Tests:**
- API endpoint tests
- Workflow tests
- Database integration tests

**E2E Tests:**
- Selenium tests (host OS)
- Playwright tests (modern E2E with video)

**Frontend Tests:**
- Jest unit tests
- Component tests
- Integration tests

### Test Infrastructure

**Test Settings:**
- Separate test database
- Test fixtures
- Mock external services
- Test data factories

**Coverage:**
- Code coverage tracking
- Coverage reports (HTML, XML)

## Performance Optimization

### Backend Optimizations

**Database:**
- Strategic indexes
- Query optimization (select_related, prefetch_related)
- Connection pooling

**Caching:**
- API response caching
- Database query caching
- Template fragment caching

**Background Processing:**
- Async email sending
- Async virus scanning
- Scheduled tasks

### Frontend Optimizations

**Code Splitting:**
- Entry point splitting
- Vendor chunk separation
- Module lazy loading

**Asset Optimization:**
- JavaScript minification
- CSS minification
- Image optimization
- Gzip compression

**Loading Strategies:**
- Critical CSS inline
- Lazy loading for non-critical features
- Progressive loading

## Internationalization (i18n)

### Supported Languages
- English (en)
- Spanish (es)
- French (fr)
- German (de)

### Implementation
- Django i18n framework
- Locale paths configured
- Language switcher component
- Translation files (`.po` files)

## Extensibility

### Plugin System
- Modular plugin architecture
- Plugin models and views
- Custom workflow support

### Settings Extension
- Modular settings structure
- Environment-specific configurations
- Feature flags

---

_Generated using BMAD Method `document-project` workflow (Exhaustive Scan)_
