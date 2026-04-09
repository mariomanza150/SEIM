# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🧱 High-Level Architecture

SEIM follows a modular, service-oriented architecture using Django, organized into distinct apps:
- **`accounts/`**: Handles user management, authentication, and roles.
- **`exchange/`**: Manages the core exchange program and application workflow logic.
- **`documents/`**: Implements document storage, validation, and workflow.
- **`notifications/`**: Processes emails and system notifications via Celery.
- **`analytics/`**: Aggregates metrics for the admin dashboard.
- **`grades/`**: Contains logic for international grade scale conversion.
- **`application_forms/`**: Manages the dynamic form builder for applications.
- **`api/`**: Houses the entire RESTful API layer built with Django REST Framework.
- **`dashboard/`**: Contains the view logic for role-based dashboards.
- **`frontend/`**: Holds Django templates and static assets for server-rendered components.

The system uses a clear separation of concerns: the **API Layer** handles data contracts (DRF), the **Business Logic Layer** resides in dedicated services (e.g., grade translation), and the **Data Layer** is managed by Django ORM over PostgreSQL.

### 🌐 Tech Stack Overview
*   **Backend**: Django 5.1.4, Django REST Framework, PostgreSQL, Redis, Celery.
*   **Frontend**: Bootstrap 5, Django Templates, ES6+ JavaScript.
*   **Deployment**: Docker Compose for containerization (`web`, `redis`, `db`, `worker`).

## 🛠️ Common Development Commands

All development, testing, and documentation generation should be executed inside the Docker containers where possible.

### Docker Compose Workflow (Recommended)
1.  **Start Services**: `docker-compose up -d`
2.  **Migrate DB**: `docker-compose exec web python manage.py migrate`
3.  **Initial Data**: `docker-compose exec web python manage.py create_initial_data`
4.  **CMS Restore**: `docker-compose exec web python manage.py restore_cms`
5.  **Collect Static**: `docker-compose exec web python manage.py collectstatic --noinput`

### Testing
*   **Unit/Integration Tests (Docker)**: `make test`
*   **Frontend Vue Tests**: `npm --prefix frontend-vue run test:run`
*   **Selenium E2E Tests (Host OS Only)**: `make test-selenium`

### Documentation
*   **Generate all docs (API, code, DB, Sphinx)**: `make docs-workflow`
*   **View API Docs**: `http://localhost:8001/api/docs/`

### Code Quality & Linting
*   **Run all checks**: `make quality-check`
*   **Install Hooks (Recommended)**: `make pre-commit-install`

## ⚙️ Environment Configuration
*   **Python**: Requires `python3.12+` for E2E testing (if running locally outside Docker).
*   **Dependencies**: Use `requirements-dev.txt` for development dependencies when working on host OS tools (e.g., frontend testing).
*   **Environment Variables**: Must be set in a `.env` file based on `env.example`, especially `DATABASE_URL`, `REDIS_URL`, and email credentials for production environments.

## 📚 Key Guides
*   **[CMS Management](documentation/CMS_RESTORE_GUIDE.md)**: For managing the Wagtail CMS content.
*   **[Developer Guide](documentation/developer_guide.md)**: Contains the full set of developer guidelines.
*   **[Architecture Decisions](documentation/architectural_decisions.md)**: Critical place to review major design choices.

---
*This guide summarizes the structure and common tasks for efficient development in SEIM.*
