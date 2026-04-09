# SEIM Documentation

Welcome to the SEIM (Student Exchange Information Manager) documentation. This comprehensive guide provides everything you need to understand, deploy, and maintain the SEIM platform.

**📌 Documentation Structure:**
- **`documentation/`** (this directory) - **Manual/Maintained Documentation** - Authoritative source for development guidelines, user guides, and planning documents. Manually maintained by the team.
- **`docs/`** - **Generated/Auto-Generated Documentation** - Auto-generated documentation from code analysis and tools. See [docs/index.md](../docs/index.md) for generated documentation.

**Quick Reference:**
- Need authoritative info? → Check this directory (`documentation/`)
- Need current system state? → Check [`docs/`](../docs/)
- Need project structure? → See [PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md)

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
- **[Frontend Guide](frontend_guide.md)** - Frontend development and UI patterns
- **[Form Builder Guide](form_builder_guide.md)** - Dynamic form creation and management

### **🔧 Technical Reference**
- **[API Documentation](api_documentation.md)** - API endpoints and usage
- **[Caching Guide](caching.md)** - Cache implementation and optimization
- **[Testing Guide](testing.md)** - Testing strategies and setup
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

### **⚙️ Administration**
- **[Admin Guide](admin_guide.md)** - System administration and operations
- **[Deployment Guide](deployment.md)** - Production deployment instructions
- **[Virus Scanner Setup](virus_scanner_setup.md)** - Document scanning configuration
- **[Selenium Setup](selenium_setup.md)** - E2E testing setup

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
- **Backend**: Django 5.1.4 with PostgreSQL
- **Frontend**: Bootstrap 5 with modern JavaScript
- **Caching**: Redis for performance optimization
- **Background Tasks**: Celery for async processing
- **Containerization**: Docker for consistent deployment
- **API**: Django REST Framework with OpenAPI documentation

---

## 🚀 Quick Start

```bash
# Clone and start the application
git clone <repository-url>
cd SEIM
docker-compose up -d

# Run migrations and create initial data
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py create_initial_data

# Access the application
# Web: http://localhost:8001/
# Admin: http://localhost:8001/seim/admin/
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

# View at: documentation/sphinx/build/html/index.html
```

### **Documentation Maintenance:**

For maintaining and updating documentation, see:
- **[Documentation Maintenance Guide](documentation_maintenance.md)** - Complete guide for keeping docs up-to-date

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
| `api/` | REST API layer |
| `core/` | Shared utilities |
| `dashboard/` | User interfaces |
| `frontend/` | UI components |
| `plugins/` | Extensibility system |

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

**Last Updated**: November 20, 2025  
**Version**: 2.2  
**Maintained By**: SEIM Development Team
