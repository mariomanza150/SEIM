# SEIM - Student Exchange Information Manager

[![CI](https://github.com/mariomanza150/SEIM/actions/workflows/ci.yml/badge.svg)](https://github.com/mariomanza150/SEIM/actions/workflows/ci.yml)

Student Exchange Information Manager: Django 5.1 + DRF + Vue 3 SPA + Wagtail CMS for student exchange programs.

**SPA:** `/seim/` (`frontend-vue/`) · **CMS:** `/` and `/cms/` · **API:** `/api/` · [Contributing](CONTRIBUTING.md) · [Issues](https://github.com/mariomanza150/SEIM/issues) · [License](LICENSE)

## 🎉 Project Status

**✅ Backend + Vue SPA application UI**  
**✅ Wagtail CMS for the public site**  
**✅ JWT API, Docker, and CI**

SEIM is a Django 5.1 + DRF backend with a Vue 3 SPA (`frontend-vue/`, served at `/seim/`), JWT authentication, and role-based dashboards. Wagtail CMS owns the public site at `/`. The Django template frontend has been removed. Remaining operator leftovers (dynforms builder, data-management UI) are listed in [docs/SPA_VS_LEGACY.md](docs/SPA_VS_LEGACY.md).

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
1. **Coverage depth** — unit+integration already enforce `--cov-fail-under=80` on first-party apps; remaining work is CMS/operator leftovers and Vue slices in [docs/SPA_VS_LEGACY.md](docs/SPA_VS_LEGACY.md)
2. **White-labeling** — UAdeC is the default theme; override `INSTITUTION_*` / `BRAND_*` (see [documentation/white_labeling.md](documentation/white_labeling.md))
3. **Internationalization** — expand beyond the current SPA/CMS split

**Note**: Backend unit+integration coverage is gated at 80%. Historical “34%” figures in older notes are stale.

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
- **Public Landing Page**: http://localhost:8001/
- **CMS Admin**: http://localhost:8001/cms/
- **Django Admin**: http://localhost:8001/seim/admin/

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

# Create deterministic demo-ready data
docker-compose exec web python manage.py seed_demo_readiness

# Restore CMS content (Wagtail landing page)
docker-compose exec web python manage.py restore_cms

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Access the application
# Web: http://localhost:8001/
# Admin: http://localhost:8001/seim/admin/  # /admin/ redirects here
# API Docs: http://localhost:8001/api/docs/
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

# Install all development dependencies (includes requirements.txt)
pip install -r requirements-dev.txt
```

Runtime pins live in `requirements.txt`. `pyproject.toml` reads that file so the two cannot drift. Docker and CI install `requirements*.txt`, not a second dependency list.

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

### **Demo-Ready Credentials**
These accounts are created by `docker-compose exec web python manage.py seed_demo_readiness`.

- **Admin**
  - Email: `admin@test.com`
  - Password: `admin123`
- **Coordinator**
  - Email: `coordinator@test.com`
  - Password: `coordinator123`
- **Student**
  - Email: `student@test.com`
  - Password: `student123`

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

# 2. Run Vue tests
npm --prefix frontend-vue run test:run

# 3. Run with coverage
npm --prefix frontend-vue run test:run -- --coverage

# 4. Watch mode
npm --prefix frontend-vue run test

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

# Run Vue frontend tests (from project root)
npm --prefix frontend-vue run test:run

# View frontend test coverage report
npm --prefix frontend-vue run test:run -- --coverage
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
- Vue tests live in `frontend-vue/` and run with Vitest (`npm --prefix frontend-vue run test:run`).
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

**Start here:** [documentation/README.md](documentation/README.md) (canonical guides + Sphinx).

`documents/` at the repo root is the **Django document-upload app**, not a third docs tree.

| Tree | Role |
| --- | --- |
| [`documentation/`](documentation/README.md) | **Canonical** manuals (install, architecture, testing, white-labeling, Sphinx) |
| [`docs/`](docs/README.md) | Generated notes, status reports, Vue/CMS working papers. Index: [docs/index.md](docs/index.md) |

### **`documentation/` - Manual/Maintained Documentation**
**Authoritative source** for development guidelines, user guides, and planning documents. Manually maintained by the team.

- **[Documentation Index](documentation/README.md)** - Complete documentation index
- **[Developer Guide](documentation/developer_guide.md)** - Complete development documentation
- **[Installation Guide](documentation/installation.md)** - Setup and deployment instructions
- **[Architecture](documentation/architecture.md)** - System design and architecture
- **[Business Rules](documentation/business_rules.md)** - Business logic and rules
- **[Form Builder Guide](documentation/form_builder_guide.md)** - Dynamic form creation system
- **[White-labeling](documentation/white_labeling.md)** - Institution branding (UAdeC default)
- **[Grade Translation Guide](documentation/grade_translation_user_guide.md)** - Grade scale conversion system
- **[Roadmap](documentation/roadmap.md)** - Development roadmap and upcoming features
- **[Backlog](documentation/backlog.md)** - Current development tasks and priorities
- **[User Stories](documentation/user_stories.md)** - User requirements and acceptance criteria
- **[Deployment Guide](documentation/deployment.md)** - Production deployment instructions
- **[Architectural Decisions](documentation/architectural_decisions.md)** - Key design decisions and rationale

### **`docs/` - Generated/Auto-Generated Documentation**
**Auto-generated** documentation from code analysis and tools. Regenerated periodically.

- **[docs/ README](docs/README.md)** - How this folder relates to `documentation/`
- **[SPA vs leftover Django](docs/SPA_VS_LEGACY.md)** - Current Vue vs Django split
- **[Documentation Index](docs/index.md)** - Index of generated documentation
- **[Project Structure Guide](docs/PROJECT_STRUCTURE.md)** - Comprehensive project structure guide
- **[API Contracts](docs/api-contracts.md)** - Auto-generated API documentation
- **[Data Models](docs/data-models.md)** - Auto-generated database schema
- **[Component Inventory](docs/component-inventory.md)** - Auto-generated component catalog
- **[Status Reports](docs/status/)** - Project status and progress tracking
- **[Quick Guides](docs/guides/)** - Quick reference guides

### **API Documentation**
- **[Interactive API Docs](http://localhost:8001/api/docs/)** - Swagger UI (auto-generated, Docker)
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

SEIM follows a modular, service-oriented architecture with a Vue 3 SPA:

```
┌─────────────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend              │    │   API Layer     │    │   Business      │
│   (Vue 3 SPA at /seim/  │◄──►│   (DRF)         │◄──►│   Logic Layer   │
│   + Wagtail CMS at /)   │    │                 │    │   (Services)    │
│                         │    │                 │    │                 │
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
- **`api/`** - REST API gateway (viewsets live in domain apps)
- **`frontend-vue/`** - Vue 3 SPA served at `/seim/`
- **`cms/`** - Wagtail CMS pages and public site

---

## 🔧 Technology Stack

### **Backend**
- **Django 5.1.4** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Database (production)
- **Redis** - Caching and background tasks
- **Celery** - Background task processing
- **JWT** - Authentication

### **Frontend**
- **Vue 3 + Vite + Pinia** - SPA at `/seim/`
- **Vue Router** - Client-side routes under `/seim/`
- **Bootstrap 5 + Bootstrap Icons** - SPA and CMS styling
- **Wagtail templates** - Public/CMS pages at `/`

### **Development & Deployment**
- **Docker & Docker Compose** - Containerization
- **drf-spectacular** - API documentation
- **django-dynforms** - Dynamic forms
- **django-compressor** - Static file optimization
- **whitenoise** - Static file serving
- **Gunicorn** - WSGI server (production)

---

## 📋 Frontend Pages

### **Public / CMS**
- **Home** (`/`) - Wagtail marketing site
- **Login** (`/seim/login/`) - SPA authentication (legacy `/login/` redirects here)
- **Register** (`/seim/register/`) - SPA registration

### **Student Pages**
- **Dashboard** (`/seim/dashboard/`) - Personal overview and quick actions
- **Programs** (`/seim/programs/compare`) - Browse available exchange programs
- **Applications** (`/seim/applications/`) - Manage applications
- **Documents** (`/seim/documents/`) - Upload and manage documents

### **Coordinator Pages**
- **Review queue** (`/seim/review-queue/`) - Application review
- **Applications** (`/seim/applications/`) - Review and process applications
- **Documents** (`/seim/documents/`) - Document validation and comments

### **Admin Pages**
- **Programs** (`/seim/admin/programs`) - Program management
- **Form Builder** (`/seim/admin/forms`) - Dynamic form creation
- **Django admin** (`/seim/django-admin/`) - System admin
- **CMS admin** (`/cms/`) - Wagtail admin

---

## 🧪 Testing

Backend unit + integration tests enforce **80%** coverage (`pytest --cov-fail-under=80`). Vue Vitest coverage is collected in CI for stores/services. Historical trends upload to [Codecov](https://codecov.io/gh/mariomanza150/SEIM) when the `CODECOV_TOKEN` GitHub Actions secret is set — see [`.github/README.md`](.github/README.md). A README badge can be added after the first successful upload.

Commands: `make test-coverage` (backend) and `npm --prefix frontend-vue run test:coverage` (Vue).

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
- **Issues**: [GitHub Issues](https://github.com/mariomanza150/SEIM/issues)
- **Security**: [Security Policy](SECURITY.md) — report vulnerabilities privately
- **Email**: support@seim.local

---

**SEIM** - Making student exchange programs accessible and efficient for everyone.