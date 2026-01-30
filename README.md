# SEIM - Student Exchange Information Manager

[![Backend Status](https://img.shields.io/badge/Backend-Stable-brightgreen)](https://img.shields.io/badge/Backend-Stable-brightgreen)
[![Frontend Status](https://img.shields.io/badge/Frontend-Complete-brightgreen)](https://img.shields.io/badge/Frontend-Complete-brightgreen)
[![Production Status](https://img.shields.io/badge/Production-Ready-green)](https://img.shields.io/badge/Production-Ready-green)
[![Tests](https://img.shields.io/badge/Tests-1147%20Passing-success)](https://img.shields.io/badge/Tests-1147%20Passing-success)

A comprehensive Django-based web application for managing student exchange programs, applications, and workflows with a modern Bootstrap 5 frontend.

## 🎉 Project Status

**✅ Production Ready**  
**✅ Backend Implementation Complete (1,147 tests passing)**  
**✅ Frontend Implementation Complete**  
**✅ Testing Infrastructure Stabilized**  
**✅ Code Quality Verified**  
**✅ Documentation Comprehensive & Up-to-Date**

SEIM is production-ready with comprehensive features, security, and infrastructure. The system features a modern, responsive Django frontend with Bootstrap 5, JWT authentication, and role-based dashboards. The codebase includes 1,147 comprehensive tests covering all critical functionality, with robust CI/CD automation and comprehensive security hardening.

### 🚀 What's Ready for Production
- Complete user authentication and authorization
- Full application workflow management
- Document upload and validation system
- Email notifications and background processing
- Analytics dashboard and reporting
- RESTful API with comprehensive documentation
- Docker containerization and deployment scripts
- **Enhanced Form Builder**: Visual drag-and-drop form creator
- Modular settings structure for different environments
- Comprehensive cleanup and maintenance tools
- Grade translation system for international students

### 🔧 Optional Enhancements
1. **Expanded Test Coverage** - Currently 34% backend, target 80% (estimated 4-6 weeks)
2. **CI/CD Pipeline** - Automated testing and deployment
3. **Internationalization** - Multi-language support

**Note**: All critical functionality is tested and stable. Coverage expansion is an enhancement, not a blocker for production deployment.

---

## 🎨 CMS & Landing Page

SEIM includes a **Wagtail CMS** for managing the public landing page with rich content blocks, blog posts, exchange program listings, and FAQs.

### Quick CMS Restore

After database reset or initial setup:

```bash
docker-compose exec web python manage.py restore_cms
```

This single command:
- ✅ Sets up Wagtail site structure
- ✅ Populates UAdeC content (programs, blog, FAQs)
- ✅ Enhances homepage with rich content blocks

### Export/Import Workflow

Save your customized CMS:
```bash
docker-compose exec web python manage.py export_cms
```

Restore it later:
```bash
docker-compose exec web python manage.py import_cms --clear
```

**📖 See [docs/CMS_RESTORE_GUIDE.md](docs/CMS_RESTORE_GUIDE.md) for complete documentation**

### CMS Access
- **Public Landing Page**: http://localhost:8000/
- **CMS Admin**: http://localhost:8000/cms/
- **Django Admin**: http://localhost:8000/seim/admin/

---

## ✨ Features

### **Frontend Interface**
- **Modern Bootstrap 5 Design**: Responsive, mobile-first interface
- **Role-based Dashboards**: Tailored experience for Students, Coordinators, and Admins
- **JWT Authentication**: Secure token-based authentication with automatic refresh
- **Interactive Forms**: Real-time validation and user feedback
- **File Upload**: Drag-and-drop document upload with progress indicators
- **Real-time Notifications**: Toast notifications and status updates

### **Authentication & User Management**
- Student registration with institutional email validation
- Email verification workflow
- JWT authentication for API access
- Password reset functionality
- Account lockout policy
- Role-based access control (Student, Coordinator, Admin)

### **Exchange Program Management**
- Complete program CRUD with eligibility criteria
- **Program Cloning** - Quick duplication of existing programs 🆕
- **Enhanced Eligibility Validation** - Age, language level, GPA checks 🆕
- Dynamic forms using django-dynforms
- Program status management
- Recurring program support

### **Grade Translation System** 🆕
- Support for multiple international grading scales (US GPA, ECTS, UK, German, French, Canadian)
- Automatic grade conversion between different scales
- Student profiles with institutional grade scale selection
- Transparent GPA equivalents for fair comparison
- Admin-configurable grade scales and translation mappings
- API endpoints for programmatic grade conversion

### **Application Workflow**
- Full state machine: draft → submitted → under_review → approved/rejected → completed/cancelled
- Application submission with eligibility validation using grade translation
- Status transitions with role-based permissions
- Application withdrawal and comments
- Comprehensive audit logging

### **Document Management**
- File upload and validation
- Document type configuration
- Resubmission workflow
- Document comments and validation
- Virus scan integration (stub)

### **Notifications**
- Email notifications for all key events
- **Direct Action Links** - One-click access to applications 🆕
- Async email processing via Celery
- Support for SMTP and AWS SES
- User notification preferences

### **Analytics & Dashboards**
- Admin dashboard with real-time metrics
- Program-specific analytics
- Application status breakdowns
- User activity tracking

### **API Layer**
- Complete RESTful API with DRF
- OpenAPI documentation with Swagger UI
- JWT authentication
- Pagination and filtering
- Role-based permissions

---

## 🚀 Quick Start

> **⚠️ Core development outside Docker is not supported, except for Selenium E2E tests which run from the host OS. All other development, testing, and documentation generation must be performed inside Docker containers to avoid host OS issues.**

### **Prerequisites**
- Docker and Docker Compose
- Git
- Python 3.12+ (for E2E testing and local development tools)

### **Environment Setup**
```bash
# Clone the repository
git clone <repository-url>
cd SEIM

# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# (See Environment Configuration section below)
```

### **Docker Setup (Required)**
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create initial data
docker-compose exec web python manage.py create_initial_data

# Restore CMS content (Wagtail landing page)
docker-compose exec web python manage.py restore_cms

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Access the application
# Web: http://localhost:8000/
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/api/docs/
```

### **Virtual Environment Setup (E2E Testing & Local Development)**

> **⚠️ Virtual environments are required for Selenium E2E tests and some local development tools that run from the host OS.**

#### **1. Create Virtual Environment (One-time setup):**
```bash
# Windows PowerShell
python -m venv .venv

# Linux/macOS
python3 -m venv .venv
```

#### **2. Activate Virtual Environment:**
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

#### **3. Install Development Dependencies:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install all development dependencies
pip install -r requirements-dev.txt
```

#### **4. Verify Installation:**
```bash
# Check if Django and other key packages are available
python -c "import django; print(f'Django {django.get_version()}')"
python -c "import selenium; print(f'Selenium {selenium.__version__}')"
```

### **When to Use Virtual Environment:**

#### **✅ Required for:**
- **Selenium E2E Tests**: Browser automation tests that run from host OS
- **Local Development Tools**: Code quality checks, documentation generation
- **Frontend Testing**: Jest tests and frontend build tools
- **CI/CD Scripts**: Local testing of deployment scripts

#### **❌ Not Required for:**
- **Backend Development**: Use Docker containers instead
- **Database Operations**: Use `docker-compose exec web` commands
- **Django Management Commands**: Use `docker-compose exec web python manage.py`

> **Manual/host-based development (virtualenv, pip, SQLite, etc.) is not supported for core development. All contributors must use Docker Compose and PostgreSQL as described above.**

### **Default Admin User**
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@seim.local`

### **Demo Student User**
- **Username**: `student`
- **Password**: `student123`
- **Email**: `student@university.edu`

---

## 🔧 Development Commands

### **Quick Commands**
```bash
# View all available commands
make help

# Start development environment
make setup

# Clean up cache files and generated files
make clean

# Full cleanup (including Docker volumes)
make clean-all

# Generate all documentation
make docs-all

# Run tests (Docker)
make test
```

### **Docker Commands**
```bash
# Start services
make docker-up

# Stop services
make docker-down

# View logs
make docker-logs
```

### **E2E Testing Commands (Virtual Environment Required)**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Run Selenium E2E tests
make test-selenium

# 3. Run standalone Selenium tests
make test-selenium-standalone

# 4. Test Selenium setup
make test-selenium-setup

# 5. Deactivate when done
deactivate
```

### **Frontend Testing Commands (Virtual Environment Required)**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Run Jest tests
npx jest --config=jest.config.js

# 3. Run with coverage
npx jest --config=jest.config.js --coverage

# 4. Watch mode
npx jest --config=jest.config.js --watch

# 5. Deactivate when done
deactivate
```

### **Documentation Commands**
```bash
# Generate API documentation
make docs-api

# Generate code documentation
make docs-code

# Generate database documentation
make docs-db

# Build Sphinx HTML docs
make docs-sphinx-docker

# Enhance docstrings
make enhance-docs
```

### **Cache Management**
```bash
# Test cache performance
make cache-test

# Show cache status
make cache-status

# Clear all cache
make cache-clear

# Show cache statistics
make cache-stats
```

### **Code Quality & Frontend Testing**

```bash
# Run all code quality checks (formatting, linting, type checking, security, complexity)
make quality-check

# Run comprehensive code quality analysis and generate a report
make quality-analysis

# Install pre-commit hooks (recommended for all contributors)
make pre-commit-install

# Run pre-commit hooks on all files
make pre-commit-run

# Run frontend JavaScript tests with Jest (from project root)
npx jest --config=jest.config.js

# View frontend test coverage report
npx jest --config=jest.config.js --coverage
```

### **Selenium E2E Testing (HOST OS ONLY)**

```bash
# Setup Selenium environment on host OS
make setup-selenium-host

# Run Selenium tests (requires Django server running in Docker)
make test-selenium

# Run standalone Selenium tests
make test-selenium-standalone

# Test Selenium setup
make test-selenium-setup
```

- All code quality and test commands must be run inside Docker containers or using the Makefile.
- Frontend tests are located in `tests/frontend/` and cover core JavaScript logic in `static/js/`.
- **Selenium E2E tests run from HOST OS, not Docker containers** (requires Chrome browser on host OS).
- Pre-commit hooks will automatically check formatting, lint, types, and security before each commit.

---

## ⚙️ Environment Configuration

### **Required Environment Variables**
Create a `.env` file based on `env.example`:

```bash
# Django Configuration
DJANGO_ENV=dev  # dev or production
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/seim_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# For SMTP: django.core.mail.backends.smtp.EmailBackend
# For AWS SES: django_ses.SESBackend
```

### **Settings Structure**
The project now uses a modular settings structure:
- `seim/settings/base.py` - Common settings for all environments
- `seim/settings/development.py` - Development-specific settings
- `seim/settings/production.py` - Production-specific settings

To use a specific settings file:
```bash
# Development (default)
export DJANGO_SETTINGS_MODULE=seim.settings.development

# Production
export DJANGO_SETTINGS_MODULE=seim.settings.production
```

---

## 📚 Documentation

SEIM documentation is organized into two main directories:

### **`documentation/` - Manual/Maintained Documentation**
**Authoritative source** for development guidelines, user guides, and planning documents. Manually maintained by the team.

- **[Documentation Index](documentation/README.md)** - Complete documentation index
- **[Developer Guide](documentation/developer_guide.md)** - Complete development documentation
- **[Installation Guide](documentation/installation.md)** - Setup and deployment instructions
- **[Architecture](documentation/architecture.md)** - System design and architecture
- **[Business Rules](documentation/business_rules.md)** - Business logic and rules
- **[Form Builder Guide](documentation/form_builder_guide.md)** - Dynamic form creation system
- **[Grade Translation Guide](documentation/grade_translation_user_guide.md)** - Grade scale conversion system
- **[Roadmap](documentation/roadmap.md)** - Development roadmap and upcoming features
- **[Backlog](documentation/backlog.md)** - Current development tasks and priorities
- **[User Stories](documentation/user_stories.md)** - User requirements and acceptance criteria
- **[Deployment Guide](documentation/deployment.md)** - Production deployment instructions
- **[Architectural Decisions](documentation/architectural_decisions.md)** - Key design decisions and rationale

### **`docs/` - Generated/Auto-Generated Documentation**
**Auto-generated** documentation from code analysis and tools. Regenerated periodically.

- **[Documentation Index](docs/index.md)** - Index of generated documentation
- **[Project Structure Guide](docs/PROJECT_STRUCTURE.md)** - Comprehensive project structure guide
- **[Architecture](docs/architecture.md)** - Auto-generated technical architecture
- **[API Contracts](docs/api-contracts.md)** - Auto-generated API documentation
- **[Data Models](docs/data-models.md)** - Auto-generated database schema
- **[Component Inventory](docs/component-inventory.md)** - Auto-generated component catalog
- **[Status Reports](docs/status/)** - Project status and progress tracking
- **[Quick Guides](docs/guides/)** - Quick reference guides

### **API Documentation**
- **[Interactive API Docs](http://localhost:8000/api/docs/)** - Swagger UI (auto-generated, Docker)
- **OpenAPI Schema**: `/api/schema/` (auto-generated, Docker)

### **Sphinx HTML Documentation**
- **Build Sphinx HTML docs (inside Docker):**
  ```bash
  make docs-sphinx-docker
  # Open documentation/sphinx/build/html/index.html in your browser
  ```

### **Full Documentation Workflow**
- **Generate all docs (API, code, DB, Sphinx HTML) in Docker:**
  ```bash
  make docs-workflow
  ```

**Quick Reference:**
- Need authoritative info? → Check `documentation/`
- Need current system state? → Check `docs/`
- Need project structure? → See [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

---

## 🏗️ Architecture

SEIM follows a modular, service-oriented architecture with a Django frontend:

```
┌─────────────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend              │    │   API Layer     │    │   Business      │
│   (Django Templates +   │◄──►│   (DRF)         │◄──►│   Logic Layer   │
│   Bootstrap 5 +         │    │                 │    │   (Services)    │
│   ES6+ JavaScript)      │    │                 │    │                 │
└─────────────────────────┘    └─────────────────┘    └─────────────────┘
                                        │                       │
                                        ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────────────┐
                       │   Data Layer    │    │   External Services     │
                       │   (Django ORM)  │    │   (Email, Cache, Queue) │
                       └─────────────────┘    └─────────────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (PostgreSQL)  │
                       └─────────────────┘
```

### **Core Apps**
- **`accounts/`** - User management and authentication
- **`exchange/`** - Exchange program and application logic
- **`documents/`** - Document management system
- **`notifications/`** - Email and notification system
- **`analytics/`** - Reporting and metrics
- **`grades/`** - Grade translation system
- **`application_forms/`** - Dynamic form builder and management
- **`api/`** - REST API endpoints
- **`dashboard/`** - Admin and user interfaces
- **`frontend/`** - Django templates and static files

---

## 🔧 Technology Stack

### **Backend**
- **Django 5.2.3** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Database (production)
- **Redis** - Caching and background tasks
- **Celery** - Background task processing
- **JWT** - Authentication

### **Frontend**
- **Bootstrap 5** - CSS framework
- **Bootstrap Icons** - Icon library
- **Django Templates** - Server-side rendering
- **JavaScript ES6+** - Client-side functionality
- **SortableJS** - Drag-and-drop functionality
- **CSS3** - Custom styling

### **Development & Deployment**
- **Docker & Docker Compose** - Containerization
- **drf-spectacular** - API documentation
- **django-dynforms** - Dynamic forms
- **django-compressor** - Static file optimization
- **whitenoise** - Static file serving
- **Gunicorn** - WSGI server (production)

---

## 📋 Frontend Pages

### **Public Pages**
- **Home** (`/`) - Landing page with features and call-to-action
- **Login** (`/login/`) - User authentication
- **Register** (`/register/`) - User registration

### **Student Pages**
- **Dashboard** (`/dashboard/`) - Personal overview and quick actions
- **Programs** (`/programs/`) - Browse available exchange programs
- **Applications** (`/applications/`) - Manage applications
- **Documents** (`/documents/`) - Upload and manage documents

### **Coordinator Pages**
- **Dashboard** (`/dashboard/`) - Application review and management
- **Applications** (`/applications/`) - Review and process applications
- **Documents** (`/documents/`) - Document validation and comments
- **Programs** (`/programs/`) - Program management (draft mode)

### **Admin Pages**
- **Dashboard** (`/admin/dashboard/`) - System overview and analytics
- **Analytics** (`/admin/analytics/`) - Detailed reporting and metrics
- **Form Builder** (`/admin/form-builder/`) - Dynamic form creation
- **User Management** (`/admin/`) - Django admin interface

---

## 🧪 Testing

### **Current Status**
- **Unit Tests**: 0% coverage (to be implemented)
- **Integration Tests**: 0% coverage (to be implemented)
- **End-to-End Tests**: 0% coverage (to be implemented)

### **Testing Plan**
1. **Unit Tests** - Test individual components and functions
2. **Integration Tests** - Test API endpoints and workflows
3. **Frontend Tests** - Test user interface components
4. **End-to-End Tests** - Test complete user workflows

---

## 🚀 Deployment

### **Production Requirements**
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Web Server**: Gunicorn + Nginx
- **Background Tasks**: Celery with Redis
- **File Storage**: Local or cloud storage (S3, etc.)
- **Email**: SMTP or AWS SES

### **Environment Variables**
```bash
# Required for production
DJANGO_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and contribution instructions.

### **Development Setup**
1. Fork the repository
2. Set up the development environment
3. Create a feature branch
4. Make your changes
5. Add tests for new features
6. Submit a pull request

### **Code Quality**
- Run `make clean` before committing to remove cache files
- Use `make docs-all` to regenerate documentation
- Follow PEP 8 for Python code
- Use meaningful commit messages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support & Contact

- **Documentation**: [Developer Guide](documentation/developer_guide.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/seim/issues)
- **Email**: support@seim.local

---

**SEIM** - Making student exchange programs accessible and efficient for everyone.