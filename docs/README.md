# SEIM Documentation

Welcome to the SEIM (Student Exchange Information Manager) documentation. This comprehensive guide provides everything you need to understand, deploy, and maintain the SEIM platform.

**📌 Documentation Structure:**
- **`docs/`** (this directory) — **canonical** technical docs (install, architecture, testing, Sphinx). Start here.
- **`docs/notes/`** — working notes, status reports, Vue/CMS papers. Entry: [notes/README.md](notes/README.md) · index: [notes/index.md](notes/index.md).
- **`docs/sphinx/`** — Sphinx source; HTML build output is `docs/sphinx/build/` (`make docs-workflow`).
- **`docs/generated/`** — API/code/DB output from `make docs-workflow`.
- **`documents/`** — Django **document-upload app**, not a documentation tree ([documents/README.md](../documents/README.md)). Do not merge, move, or delete it.

**Quick Reference:**
- Need authoritative info? → This directory (`docs/`)
- Need current system state? → Check [`notes/`](notes/)
- Need project structure? → See [PROJECT_STRUCTURE.md](notes/PROJECT_STRUCTURE.md)

---

## 📚 Documentation Index

### **🚀 Getting Started**
- **[Installation Guide](installation.md)** - Setup and deployment instructions
- **[Developer Guide](developer_guide.md)** - Development workflow and best practices
- **[Environment Variables](environment_variables.md)** - Configuration reference

### **👨‍💻 Development**
- **[Developer Guide](developer_guide.md)** - Development workflow, standards, and best practices
- **[Architecture](architecture.md)** - System design and technical architecture
- **[Business Rules](business_rules.md)** - Business logic and rules
- **[Frontend Guide](frontend_guide.md)** - Vue SPA + CMS patterns
- **[SPA vs leftover Django](notes/SPA_VS_LEGACY.md)** - What is still Django
- **[White-labeling](white_labeling.md)** - Institution branding (UAdeC default)
- **[Form Builder Guide](form_builder_guide.md)** - Dynamic form creation and management

### **🔧 Technical Reference**
- **[API Documentation](api_documentation.md)** - API endpoints and usage
- **[Caching Guide](caching.md)** - Cache implementation and optimization
- **[Testing Guide](testing.md)** - Testing strategies and setup
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

### **⚙️ Administration**
- **[Admin Guide](admin_guide.md)** - System administration and operations
- **[Deployment Guide](deployment.md)** - Production deployment instructions
- **[CMS Restore Guide](notes/CMS_RESTORE_GUIDE.md)** - Wagtail export/import and restore
- **[Virus Scanner Setup](virus_scanner_setup.md)** - Document scanning configuration
- **[Selenium Setup](selenium_setup.md)** - Legacy E2E (deprecated; see [e2e_testing_guide.md](e2e_testing_guide.md))

### **📋 Project Information**
- **[New Features - October 2025](new_features_oct_2025.md)** - Latest enhancements ✨
- **[Roadmap](roadmap.md)** - Development roadmap and future features
- **[Changelog](changelog.md)** - Release notes and change history
- **[User Stories](user_stories.md)** - User requirements and acceptance criteria
- **[Backlog](backlog.md)** - Current development tasks

### **🎨 Design Reference**
- **[Wireframes](wireframes/)** - UI/UX wireframes and design specifications
- **[Dark Mode Implementation](dark-mode-implementation.md)** - Dark mode feature details
- **[Grade Translation Design](grade_translation_design.md)** - Grade conversion system design
- **[Grade Translation User Guide](grade_translation_user_guide.md)** - Grade scale usage guide

### **📐 Architecture & Decisions**
- **[Architectural Decisions](architectural_decisions.md)** - Key design decisions and rationale
- **[Implementation Plans](implementation_plans/)** - Feature implementation documentation

### **📦 Historical Reference**
- **[Archive](archive/)** - Historical reports and assessments
  - **[Session 2025-11](archive/session_2025_11/)** - November 2025 development session (Testing, Quality, Documentation)
  - **[Session 2025-10-18](archive/session_2025_10_18/)** - October 2025 development session (New Features + Admin UI)
  - **[Session 2025-01](archive/session_2025_01/)** - January 2025 cleanup session reports
  - **[Form Builder Development](archive/form_builder_development/)** - Form Builder feature development docs
- **[Audit Reports](audit_reports/)** - Code and documentation audits

---

## 🎯 Golden Path for New Contributors

### **For Developers:**
1. **Setup**: [Installation Guide](installation.md) - Environment setup with Docker
2. **Learn**: [Architecture](architecture.md) - Understand system design
3. **Develop**: [Developer Guide](developer_guide.md) - Coding standards and workflow
4. **API**: [API Documentation](api_documentation.md) - Integration reference
5. **Test**: [Testing Guide](testing.md) - Testing your changes

### **For System Administrators:**
1. **Deploy**: [Deployment Guide](deployment.md) - Production setup
2. **Configure**: [Environment Variables](environment_variables.md) - System configuration
3. **Operate**: [Admin Guide](admin_guide.md) - Daily administration
4. **Troubleshoot**: [Troubleshooting Guide](troubleshooting.md) - Issue resolution

### **For Project Managers:**
1. **Overview**: [Architecture](architecture.md) - System capabilities
2. **Planning**: [Roadmap](roadmap.md) - Current and future plans
3. **Requirements**: [User Stories](user_stories.md) - Feature specifications
4. **Progress**: [Changelog](changelog.md) - Recent updates

---

## 🏗️ System Overview

SEIM is a comprehensive Django-based web application for managing student exchange programs with:

### **Core Capabilities:**
- **User Management**: Role-based authentication (Student, Coordinator, Admin)
- **Program Management**: Exchange program creation and administration
- **Application Workflow**: Complete application lifecycle management
- **Document Management**: Secure file upload and validation
- **Notifications**: Email and in-app notification system
- **Analytics**: Real-time dashboards and reporting
- **API Layer**: RESTful API with comprehensive documentation
- **Form Builder**: Visual drag-and-drop dynamic form creator
- **Grade Translation**: International grade scale conversion system

### **Technology Stack:**
- **Backend**: Django 5.2.17 with PostgreSQL
- **Frontend**: Vue 3.5 + Vite 7 SPA at `/seim/` plus Wagtail 7 CMS at `/`
- **Caching**: Redis for performance optimization
- **Background Tasks**: Celery for async processing
- **Containerization**: Docker for consistent deployment
- **API**: Django REST Framework with OpenAPI documentation
- **E2E**: Playwright (primary); Selenium deprecated
- **Formatter**: Ruff (not Black)

---

## 📌 Current State (August 2026)

| Topic | Current repo state |
|-------|-------------------|
| Django | **5.2.17** (`pyproject.toml`) |
| Python | `>=3.11`; Docker/CI use **3.12** |
| Frontend | **Vue 3.5 + Vite 7** SPA at `/seim/` |
| Public site | **Wagtail 7** at `/`, admin at `/cms/` |
| Django admin | **`/seim/django-admin/`** (root `/admin/` redirects here) |
| Vue staff UI | **`/seim/admin/*`** |
| Dev URL | **`http://localhost:8001`** |
| Local-prod QA | **`http://localhost:8020`** |
| E2E | **Playwright** (`make e2e-test`); Selenium deprecated |
| Frontend tests | **Vitest** |
| Backend tests | **pytest**, **80% coverage gate**; `cms` excluded in test settings |
| Dependencies | **`pyproject.toml` only** |
| Django apps | `accounts`, `analytics`, `api`, `application_forms`, `cms`, `core`, `data_management`, `documents`, `exchange`, `grades`, `notifications`, `workflows` |

See [notes/SPA_VS_LEGACY.md](notes/SPA_VS_LEGACY.md) for remaining Django-template leftovers.

---

## 🚀 Quick Start

```bash
# Clone and start the application
git clone <repository-url>
cd SEIM
docker compose up -d

# Run migrations and create initial data
docker compose exec web python manage.py migrate
docker compose exec web python manage.py create_initial_data

# Access the application
# Web: http://localhost:8001/
# Django admin: http://localhost:8001/seim/django-admin/
# Vue staff UI: http://localhost:8001/seim/admin/
# API Docs: http://localhost:8001/api/docs/
```

**Default Admin Access:**
- Username: `admin`
- Password: `admin123`

---

## 📖 Documentation Generation & Maintenance

### **Generate All Documentation:**
```bash
# Inside Docker (recommended)
make docs-all

# This generates:
# - API documentation (OpenAPI/Swagger)
# - Code documentation
# - Database documentation
# - Sphinx HTML documentation
```

### **Sphinx HTML Documentation:**
```bash
# Build Sphinx docs
make docs-sphinx-docker

# View at: docs/sphinx/build/html/index.html
```

### **Documentation Maintenance:**

For maintaining and updating documentation, see:
- **[Documentation Maintenance Guide](documentation_maintenance.md)** - Complete guide for keeping docs up-to-date

### **Generated docs (committed reference outputs)**

Regenerate inside Docker:

```bash
make docs-workflow
```

Committed artifacts (last synced **August 2026**):

- `docs/generated/code_documentation.md`
- `docs/generated/database_schema.md`
- `api_schema.yaml`

Sphinx HTML stays in `docs/sphinx/build/` (gitignored). See **Current State** above for stack ground truth.

---

## 📁 Project Structure

### **Application Architecture:**
| App | Purpose |
|-----|---------|
| `accounts/` | User management and authentication |
| `exchange/` | Student exchange workflows |
| `documents/` | Document management |
| `notifications/` | Communication system |
| `analytics/` | Reporting and metrics |
| `grades/` | Grade translation system |
| `application_forms/` | Dynamic form builder |
| `api/` | REST API gateway (URL aggregator) |
| `core/` | Shared utilities |
| `cms/` | Wagtail CMS pages and public site |
| `workflows/` | Application workflow engine |
| `data_management/` | Data import/export operator UI |
| `frontend-vue/` | Vue 3 SPA at `/seim/` (repo root, not a Django app) |

---

## 🆘 Getting Help

### **Resources:**
1. Check this documentation first
2. Review [Troubleshooting Guide](troubleshooting.md)
3. Explore [API Documentation](api_documentation.md)
4. Check [Changelog](changelog.md) for recent updates

### **Support:**
- **Documentation**: Comprehensive guides (this folder)
- **GitHub Issues**: Bug reports and feature requests
- **Email**: admin@seim.local

---

## 📝 Documentation Maintenance

This documentation is continuously maintained as part of the SEIM project:

- **Regular Updates**: Documentation updated with each major release
- **Link Verification**: Links checked and updated periodically
- **Content Review**: Documentation reviewed for accuracy
- **Auto-Generation**: API and code docs automatically generated

---

**Last Updated**: August 20, 2026  
**Version**: 2.3  
**Maintained By**: SEIM Development Team
