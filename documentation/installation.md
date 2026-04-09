# SEIM Installation Guide

## Overview
SEIM (Student Exchange Information Manager) is a Django-based web application for managing student exchange programs. This guide covers installation and setup for both development and production environments.

---

## 🚀 Quick Start (Docker - Required)

> **⚠️ Core development outside Docker is not supported, except for Selenium E2E tests which run from the host OS. All other development, testing, and documentation generation must be performed inside Docker containers to avoid host OS issues.**

### **1. Clone and Setup:**
```bash
git clone <repository-url>
cd SEIM
```

### **2. Start the Application:**
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create initial data
docker-compose exec web python manage.py create_initial_data

# Create demo-ready data (optional)
docker-compose exec web python manage.py seed_demo_readiness
```

### **3. Access the Application:**
- **Web Application**: http://localhost:8000/
- **Admin Interface**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/

### **4. Demo-Ready Credentials:**
These accounts are created by `seed_demo_readiness`.

- **Admin**: `admin@test.com` / `admin123`
- **Coordinator**: `coordinator@test.com` / `coordinator123`
- **Student**: `student@test.com` / `student123`

### **5. Demo Data (Optional):**
For demonstration and testing purposes, you can populate the system with sample data:

```bash
# Create deterministic demo data
docker-compose exec web python manage.py seed_demo_readiness
```

This creates:
- Canonical admin, coordinator, and student demo users
- Active exchange programs
- Applications in every major workflow status
- Documents, comments, timeline events, and notifications

### **6. Cleanup Demo Data (Optional):**
To remove all demo data:
docker-compose exec web python manage.py cleanup_demo_data

---

## 🐍 Virtual Environment Setup (E2E Testing & Local Development)

> **⚠️ Virtual environments are required for Selenium E2E tests and some local development tools that run from the host OS.**

### **Virtual Environment Setup:**

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

### **Virtual Environment Workflow:**

#### **For E2E Testing:**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Ensure Django server is running in Docker
docker-compose up -d

# 3. Run Selenium E2E tests
make test-selenium

# 4. Deactivate when done
deactivate
```

#### **For Local Development Tools:**
```bash
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Run code quality checks
make quality-check

# 3. Run frontend tests
npx jest --config=jest.config.js

# 4. Generate documentation
python manage.py generate_docs

# 5. Deactivate when done
deactivate
```

### **Troubleshooting Virtual Environment:**

#### **Common Issues:**
```bash
# Issue: "No module named 'celery'" or similar import errors
# Solution: Ensure virtual environment is activated and dependencies are installed
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Issue: Permission errors on Windows
# Solution: Run PowerShell as Administrator or use:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Issue: Virtual environment not found
# Solution: Recreate the virtual environment
rm -rf .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

---

## 🛑 Unsupported: Manual/Host-Based Development

> **Manual setup using virtual environments, pip, or SQLite is not supported for core development.**
> All contributors must use Docker Compose and PostgreSQL as described above. This avoids common host OS issues and ensures a consistent environment for all developers.
> 
> **Exception**: Virtual environments are required for Selenium E2E tests and some local development tools that run from the host OS.

---

## 🏭 Production Setup

### **1. Environment Variables:**
Create a `.env` file in the project root:

```bash
# Django Settings
DJANGO_ENV=production
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/seim_db

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379/0

# Static Files
STATIC_ROOT=/path/to/static/files
MEDIA_ROOT=/path/to/media/files

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### **2. Database Setup:**
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Create database
sudo -u postgres createdb seim_db
sudo -u postgres createuser seim_user
sudo -u postgres psql -c "ALTER USER seim_user PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE seim_db TO seim_user;"
```

### **3. Static Files:**
```bash
# Collect static files
python manage.py collectstatic

# Configure web server (nginx example)
# See deployment documentation for details
```

### **4. Background Tasks:**
```bash
# Install Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Start Celery worker
celery -A seim worker -l info --detach

# Start Celery beat
celery -A seim beat -l info --detach
```

---

## 📧 Email Configuration

### **Development (Console Output):**
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### **Production - SMTP (Gmail):**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### **Production - AWS SES:**
```bash
# Install AWS SES package
pip install django-ses

# Environment variables
AWS_SES_ACCESS_KEY_ID=your-access-key
AWS_SES_SECRET_ACCESS_KEY=your-secret-key
AWS_SES_REGION_NAME=us-east-1
```

---

## 🔒 Security Configuration

### **Production Security Settings:**
```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### **Environment Variables:**
```bash
# Required for production
DJANGO_ENV=production
SECRET_KEY=your-secret-key
```

---

## 🐳 Docker Configuration

### **Development:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Production:**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📚 Documentation Generation (Docker Only)

All documentation (API, code, Sphinx HTML) should be generated inside Docker containers for consistency.

- **API Docs (Swagger/OpenAPI):**
  ```bash
  make docs-api
  # or for all docs:
  make docs-workflow
  ```
- **Sphinx HTML Docs:**
  ```bash
  make docs-sphinx-docker
  # Open documentation/sphinx/build/html/index.html
  ```
- **Full Workflow:**
  ```bash
  make docs-workflow
  ```

See the [README](../README.md) and [documentation/README.md](README.md) for more details.

---

## 🔍 Troubleshooting

> **Note:** All troubleshooting steps below assume you are using Docker-based development as required. Development outside Docker is unsupported and may result in environment-specific issues that are not covered here. Using Docker ensures consistency and avoids common host OS problems with dependencies, database, and services.

### **Common Issues:**

#### **Database Connection Errors:**
- Check database service is running
- Verify connection credentials
- Ensure database exists

#### **Static Files Not Loading:**
- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` configuration
- Verify web server configuration

#### **Email Not Sending:**
- Check SMTP credentials
- Verify email backend configuration
- Test with console backend first

#### **Celery Tasks Not Running:**
- Ensure Redis is running
- Check Celery worker is started
- Verify broker URL configuration

---

## 📚 Additional Resources

- **[Developer Guide](developer_guide.md)** - Development workflow and standards
- **[Architecture](architecture.md)** - System architecture overview
- **[Deployment Guide](deployment.md)** - Production deployment details
- **[API Documentation](http://localhost:8000/api/docs/)** - Interactive API docs

---

**For additional help, see the [Support & Contact](../README.md#support--contact) section.** 

### **Python Dependencies**
- The project now uses pylibmagic (instead of python-magic-bin) to provide file type detection support for Python 3.12+ and all platforms. This is required for document upload validation. 