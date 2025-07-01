---
applyTo: '**'
---
# SGII Project Knowledge - LLM Instructions

## Project Overview
**Student Exchange Information Manager (SEIM)** - A comprehensive Django web application for managing international student exchange programs from application submission to final grade reporting.

**Primary Purpose**: Streamline the complete student exchange workflow including applications, document verification, approvals, tracking, and reporting.

## High-Level Architecture

### Tech Stack
- **Backend**: Django 5.2.1 (Python 3.12)
- **Database**: PostgreSQL 17 (production), SQLite (development)
- **Frontend**: Bootstrap 5 + Django Templates
- **Background Tasks**: Celery 5.5 + Redis
- **Web Server**: Gunicorn
- **Authentication**: Django Auth + JWT for API
- **Document Processing**: ReportLab (PDF generation), libmagic (file validation)
- **Deployment**: Docker + Docker Compose

### Key Features
- Student application management with dynamic forms
- Secure document upload/verification with integrity checking
- Multi-stage workflow system with email notifications
- PDF generation for official documents
- Analytics dashboard and reporting
- RESTful API with comprehensive endpoints
- Internationalization support
- Batch processing capabilities

## Codebase Structure

### Project Root: `E:\mario\Documents\SGII`
```
SGII/
├── SEIM/                    # Django project directory
│   ├── seim/               # Project configuration
│   │   ├── settings.py     # Main settings
│   │   ├── custom_settings/ # Environment-specific configs
│   │   ├── urls.py         # Root URL routing
│   │   └── celery.py       # Celery configuration
│   ├── exchange/           # Main application module
│   │   ├── models/         # Database models (modular)
│   │   ├── services/       # Business logic layer
│   │   ├── views.py        # View controllers
│   │   ├── serializers.py  # API serializers
│   │   ├── permissions.py  # Access control
│   │   ├── forms.py        # Django forms
│   │   ├── templates/      # HTML templates
│   │   ├── static/         # CSS/JS assets
│   │   └── tests/          # Test suite
│   ├── manage.py           # Django management
│   └── db.sqlite3          # Development database
├── docker/                 # Container configuration
│   ├── Dockerfile          # Multi-stage Python build
│   ├── docker-compose.yml  # Services orchestration
│   └── .env.dev           # Development environment vars
├── scripts/                # Deployment/utility scripts
├── docs/                   # Comprehensive documentation
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

### Core Models (exchange/models/)
- **Exchange**: Main application record
- **Document**: File attachments with validation
- **Course**: Academic course information  
- **Comment**: Workflow comments/notes
- **Timeline**: Application progress tracking
- **UserProfile**: Extended user information

### Key Services (exchange/services/)
- **workflow.py**: Application state management
- **document_generator.py**: PDF creation
- **email_service.py**: Notification system
- **batch_processor.py**: Bulk operations
- **analytics.py**: Reporting and metrics

## Container Information

### Docker Setup
- **Multi-stage build**: Separates build dependencies from runtime
- **Base image**: python:3.12-slim
- **Services**: 
  - `web`: Django application (port 8000)
  - `db`: PostgreSQL 17 (port 5432)
- **Volumes**: 
  - Code mounted for development
  - Persistent data for database, logs, media
- **Dependencies**: libpq5, libmagic1, postgresql-client

### Development Workflow
```bash
# Start containers
docker-compose up

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access application: http://localhost:8000
# Access database: localhost:5432 (seim/seim_user/seim_pass)
```

### Key Environment Variables
- `DJANGO_ENV`: dev/prod environment
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Celery broker
- `SECRET_KEY`: Django security
- `AWS_*`: S3 storage configuration

### File Locations
- **Media files**: `/app/media/exchanges/`
- **Static files**: `/app/staticfiles/`
- **Logs**: `/app/logs/`
- **Application code**: `/app/` (mounted in dev)

## Development Guidelines
- Follow Django best practices and project structure
- Use modular models and services architecture
- Comprehensive test coverage expected
- Security-first approach for file handling
- API-first design with DRF
- Docker-first development environment
- Git workflow with pre-commit hooks

## Security Considerations
- File validation with MIME type checking
- SHA-256 hash verification for documents
- Content scanning for malicious files
- Django's built-in CSRF protection
- Permission-based access control
- Secure authentication with password hashing

---
*This knowledge base provides essential context for understanding and working with the SEIM project codebase.*