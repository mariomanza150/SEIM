# SGII Project Knowledge – LLM Context

## Project Overview
**Student Exchange Information Manager (SEIM)** is a comprehensive Django web application for managing international student exchange programs, covering the entire workflow from application submission to final grade reporting.

**Business Rules & Purpose:**
- Streamline student exchange processes: application, document verification, approvals, tracking, and reporting.
- Enforce strict workflow transitions and permissions for each user role (Student, Coordinator, Manager, Admin).
- Ensure document integrity, security, and compliance with institutional requirements.
- Provide analytics and reporting for program oversight and improvement.

---

## Architecture

### High-Level System Design
- **Frontend Layer:** Bootstrap 5 + Django Templates (optionally React/Vue/Angular for API clients)
- **API Gateway Layer:** Django REST Framework (DRF), JWT authentication, input validation, rate limiting
- **Business Logic Layer:** Modular services for workflow, document generation, forms, notifications, file management
- **Data Layer:** PostgreSQL (production), SQLite (development), Redis (cache/session), S3/local file storage

### Key Design Patterns
- **Service-Oriented Architecture:** Each major feature is a separate service (loose coupling, testable, scalable)
- **Repository Pattern:** Data access via model managers, business logic separated from data access
- **State Machine Pattern:** Strict workflow transitions, permission-based, with audit trail
- **Factory Pattern:** Document generation uses a factory for extensibility

### Data Flow (Typical Operations)
- **User registration/login:** JWT-based, session stored in Redis
- **Application creation:** Multi-step dynamic forms, validated and stored
- **Document upload:** File validated (type, size, hash), stored securely, integrity checked
- **Workflow transitions:** State machine enforces allowed transitions, logs all changes
- **Notifications:** Email/in-app, triggered by workflow events
- **Analytics/reporting:** Aggregated via analytics service, exportable as CSV/PDF

---

## Key Features & Workflow Rules
- **Dynamic Forms:** JSON-configured, multi-step, conditional fields, validation
- **Document Management:** Secure upload, SHA-256 hash, virus scan, file type/size enforcement
- **Workflow Engine:** State machine for application lifecycle (draft → submitted → under_review → approved/rejected → completed/cancelled)
- **Role-Based Permissions:** Object-level access for Students, Coordinators, Managers, Admins
- **Notifications:** Email and in-app, template-based, queued via Celery
- **Admin Interface:** Django admin with color-coded statuses, bulk actions, document tools
- **Batch Processing:** Bulk operations for managers (e.g., approve/reject multiple applications)
- **Analytics Dashboard:** Visualizes KPIs, workflow bottlenecks, document stats, exportable reports
- **RESTful API:** CRUD for exchanges, documents, forms, workflow, authentication
- **Internationalization:** Multi-language support, localized documents

#### Example Workflow Transitions
```python
WORKFLOW_TRANSITIONS = {
    'draft': ['submitted', 'cancelled'],
    'submitted': ['under_review', 'cancelled'],
    'under_review': ['approved', 'rejected'],
    'approved': ['completed', 'cancelled'],
    'rejected': ['draft'],
    'completed': [],
    'cancelled': []
}
```

---

## Core Models & Services
- **Exchange:** Main application record
- **Document:** File uploads with validation and integrity
- **FormStep/FormSubmission:** Dynamic form config and responses
- **WorkflowLog:** Audit trail for state changes
- **UserProfile:** Extended user info, roles
- **Services:**
  - `workflow.py`: State machine logic
  - `document_generator.py`: PDF creation (ReportLab)
  - `form_handler.py`: Dynamic forms
  - `notification.py`: Email/in-app notifications
  - `analytics.py`: Reporting and metrics
  - `batch_processor.py`: Bulk operations

---

## Used Libraries & Dependencies
**Core:**
- Django 5.2.1, djangorestframework, django-filter, django-cors-headers, django-redis, django-viewflow
- PostgreSQL, psycopg2-binary, Redis, celery, amqp, kombu
- Pillow, python-magic, libmagic, reportlab (PDF)
- boto3 (S3), whitenoise (static files)

**Dev/Test/Quality:**
- pytest, pytest-django, pytest-cov, factory-boy, faker
- black, isort, flake8, pylint, bandit, safety, mypy, django-stubs
- sphinx (docs), django-debug-toolbar, django-extensions

---

## Security Best Practices
- Passwords hashed (PBKDF2/bcrypt)
- JWT for API, Django Auth for web
- File validation (type, size, hash, virus scan)
- Files stored outside web root
- Role-based and object-level permissions
- CSRF protection, CORS configuration
- Never commit secrets; use .env or secret manager
- Regular dependency and security scans (Bandit, Safety)

---

## Deployment & Operations
- **Docker-first:** Multi-stage build, Docker Compose for orchestration
- **Environment:** Set via .env (DJANGO_ENV, DATABASE_URL, REDIS_URL, SECRET_KEY, AWS_*)
- **Production:** DEBUG=False, HTTPS, strong SECRET_KEY, ALLOWED_HOSTS set
- **Monitoring:** Sentry for errors, health endpoints, log monitoring
- **Backups:** Regular DB and media backups
- **Scaling:** Nginx load balancer, PostgreSQL replicas, Redis cluster, S3 for files

---

## Analytics & Reporting
- Dashboard for managers/admins: application stats, workflow bottlenecks, document verification
- Exportable reports (CSV, PDF)
- Batch processing for large exports (Celery)
- Extensible via analytics service and dashboard templates

---

## API Endpoints & Integration
- `/api/auth/`: JWT login/logout/refresh
- `/api/exchanges/`: CRUD, workflow transitions, history, form progress
- `/api/documents/`: Upload, download, verify integrity
- `/api/forms/`: Dynamic form config and submission
- `/api/workflow/`: Status transitions
- **External:** Email (SendGrid/AWS SES), S3/Cloud Storage, Sentry, Google Analytics

---

## Contribution & Coding Standards
- Follow PEP8 (Python), Django style, and project structure
- Use modular models/services, keep views thin
- Write tests for all features, aim for >80% coverage
- Use pre-commit hooks (black, isort, flake8, bandit, mypy)
- Commit messages: imperative, <72 chars, reference issues/PRs
- Update docs and changelog for all changes
- Pull request checklist: tests, style, docs, clear description, no conflicts

---

## Maintenance & Future Enhancements
- **Daily:** Monitor logs, check health, review security alerts
- **Weekly:** Verify backups, review performance, update security
- **Monthly:** Update dependencies, clean storage, review feedback
- **Planned:** Real-time notifications (WebSocket), advanced analytics, mobile app, AI integration (OCR, predictive analytics), microservices, enhanced security (2FA, biometrics), GraphQL API

---

*This file provides essential, up-to-date context for LLMs and developers working with the SEIM project. For details, see the `docs/` directory and codebase.*