# Student Exchange Information Manager (SEIM)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A comprehensive Django web application for managing international student exchange programs, from application submission to final grade reporting.

---

## Project Overview
SEIM streamlines the complete student exchange workflow, including applications, document verification, approvals, tracking, and reporting.

## Key Features
- Student application management with dynamic forms
- Secure document upload/verification with integrity checking
- Multi-stage workflow system with email notifications
- PDF generation for official documents
- Analytics dashboard and reporting
- RESTful API with comprehensive endpoints
- Internationalization support
- Batch processing capabilities

## Tech Stack
- **Backend**: Django 5.2.1 (Python 3.12)
- **Database**: PostgreSQL 17 (production), SQLite (development)
- **Frontend**: Bootstrap 5 + Django Templates (with AJAX/API for partial reloads)
- **Background Tasks**: Celery 5.5 + Redis
- **Web Server**: Gunicorn
- **Authentication**: Django Auth + JWT for API
- **Document Processing**: ReportLab (PDF generation), libmagic (file validation)
- **Deployment**: Docker + Docker Compose

## Codebase Structure
```
SGII/
├── SEIM/                    # Django project directory
│   ├── seim/               # Project configuration
│   ├── exchange/           # Main application module
│   ├── manage.py           # Django management
│   └── db.sqlite3          # Development database
├── docker/                 # Container configuration
├── scripts/                # Deployment/utility scripts
├── docs/                   # Comprehensive documentation
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Git

### Development Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd SGII

# Copy environment variables template
cp .env.example .env

# Start containers
docker-compose up

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```
- Access the app: http://localhost:8000
- Access the database: localhost:5432 (seim/seim_user/seim_pass)

## Environment Variables
- `DJANGO_ENV`: dev/prod
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Celery broker
- `SECRET_KEY`: Django security
- `AWS_*`: S3 storage configuration

## Documentation
- See `docs/README.md` for full documentation, guides, and API references.

## Contributing
- Follow Django best practices and project structure
- Use modular models and services architecture
- Ensure comprehensive test coverage
- Security-first approach for file handling
- API-first design with DRF
- Docker-first development environment
- Git workflow with pre-commit hooks

## Changelog
See `docs/CHANGELOG.md` for version history.

## License
MIT License. See [LICENSE](LICENSE) for details.

---
For more details, see the documentation in the `docs/` directory.
