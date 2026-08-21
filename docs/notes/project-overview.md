# SEIM - Project Overview

**Date:** 2026-08-20  
**Type:** Web Application  
**Architecture:** Service-Oriented Layered Architecture

## Executive Summary

SEIM manages student exchange programs with a **Django 5.2** backend, **Vue 3.5 SPA** at `/seim/`, **Wagtail 7** public site, JWT auth, and DRF API. Dev server: **http://localhost:8001**.

## Project Classification

- **Repository Type:** Monolith
- **Project Type(s):** Web Application (Django + Vue SPA)
- **Primary Language(s):** Python 3.12, JavaScript/TypeScript (Vue)
- **Architecture Pattern:** Service-Oriented Layered Architecture with Clean Architecture principles

## Technology Stack Summary

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| **Web Framework** | Django | 5.2.17 | ORM, admin, ecosystem |
| **API Framework** | Django REST Framework | 3.16+ | REST + OpenAPI |
| **Database** | PostgreSQL | 15+ | Production DB |
| **Cache/Tasks** | Redis | 7+ | Celery + cache |
| **CMS** | Wagtail | 7 | Public site `/` |
| **Frontend** | Vue + Vite | 3.5 / 7 | SPA `/seim/` |
| **Frontend tests** | Vitest | 3.x | `frontend-vue/` |
| **E2E** | Playwright | primary | `make e2e-test` |
| **Dev URL** | Docker Compose | host 8001 | Maps container 8000 |

## Key Features

- **User Management**: Custom user model with email verification, role-based access control (Student, Coordinator, Admin), JWT authentication
- **Exchange Program Management**: Complete CRUD with eligibility criteria (GPA, language, age), program cloning, recurring program support
- **Application Workflow**: Full state machine (draft → submitted → under_review → approved/rejected → completed/cancelled), eligibility validation using grade translation
- **Document Management**: File upload, validation, virus scanning integration, resubmission workflow, comments
- **Notifications**: Email and in-app notifications, async processing via Celery, user preferences, reminders
- **Grade Translation**: International grade scale conversion (US GPA, ECTS, UK, German, French, Canadian), automatic conversion between scales
- **Analytics**: Admin dashboard with real-time metrics, program-specific analytics, application status breakdowns
- **Dynamic Forms**: Visual drag-and-drop form builder using django-dynforms, JSON schema storage
- **CMS Integration**: Wagtail CMS for public landing pages with rich content blocks, blog posts, FAQs
- **WebSocket Support**: Real-time notifications via Django Channels
- **API Layer**: Complete RESTful API with OpenAPI documentation, pagination, filtering, role-based permissions

## Architecture Highlights

- **Clean Architecture**: Separation of concerns across presentation, application, domain, and infrastructure layers
- **Service Layer**: Business logic encapsulated in service modules, keeping views/controllers thin
- **Modular App Structure**: Feature-based Django apps (accounts, exchange, documents, notifications, grades, analytics, etc.)
- **API-First Design**: RESTful API prioritized for all major workflows with comprehensive documentation
- **Security**: Account lockout policy, password reset, JWT authentication, role-based permissions
- **Internationalization**: Multi-language support (English, Spanish, French, German) with locale paths configured
- **Extensibility**: Plugin system for custom workflows, modular settings for different environments

## Development Overview

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.12+ (for E2E testing and local development tools)

### Getting Started

1. Clone repository and copy `.env.example` to `.env`
2. Start services: `docker-compose up -d`
3. Run migrations: `docker-compose exec web python manage.py migrate`
4. Create initial data: `docker-compose exec web python manage.py create_initial_data`
5. Restore CMS: `docker-compose exec web python manage.py restore_cms`
6. Collect static files: `docker-compose exec web python manage.py collectstatic --noinput`

Access:
- Web: http://localhost:8001/
- Admin: http://localhost:8001/seim/admin/
- CMS Admin: http://localhost:8001/cms/
- API Docs: http://localhost:8001/api/docs/

### Key Commands

- **Install:** `docker-compose up -d`
- **Dev:** `docker-compose up` (with logs)
- **Test:** `make test` (Docker) or `make test-selenium` (host OS for E2E)
- **Build:** `docker-compose exec web python manage.py collectstatic --noinput`
- **Quality:** `make quality-check`

## Repository Structure

- **`accounts/`** - User management and authentication
- **`exchange/`** - Exchange program and application logic
- **`documents/`** - Document management system
- **`notifications/`** - Email and notification system
- **`analytics/`** - Reporting and metrics
- **`grades/`** - Grade translation system
- **`application_forms/`** - Dynamic form builder and management
- **`cms/`** - Wagtail CMS pages and content
- **`api/`** - REST API gateway (URL aggregator)
- **`frontend/`** - Django templates and static files
- **`core/`** - Shared utilities, base models, permissions
- **`seim/`** - Django project settings
- **`templates/`** - HTML templates
- **`static/`** - CSS, JavaScript, images
- **`tests/`** - Test suites (unit, integration, e2e)

## Documentation Map

For detailed information, see:

- [index.md](./index.md) - Master documentation index
- [architecture.md](./architecture.md) - Detailed architecture
- [source-tree-analysis.md](./source-tree-analysis.md) - Directory structure
- [development-guide.md](./development-guide.md) - Development workflow
- [api-contracts.md](./api-contracts.md) - API endpoint documentation
- [data-models.md](./data-models.md) - Database schema documentation
- [component-inventory.md](./component-inventory.md) - UI component catalog

---

_Generated using BMAD Method `document-project` workflow_
