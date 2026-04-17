# SEIM Documentation Index

**Type:** Monolith  
**Primary Language:** Python, JavaScript  
**Architecture:** Service-Oriented Layered Architecture (Clean Architecture principles)  
**Last Updated:** 2026-04-08

## Project Overview

SEIM (Student Exchange Information Manager) is a comprehensive Django-based web application for managing student exchange programs, applications, and workflows. The system features a modern Bootstrap 5 frontend with JWT authentication, role-based dashboards, Wagtail CMS integration, and a complete RESTful API. The application follows Clean Architecture principles with clear separation between presentation, application, domain, and infrastructure layers.

## Quick Reference

- **Tech Stack:** Django 5.1.4, PostgreSQL 15+, Bootstrap 5, Redis 7.2+, Celery 5.5.3
- **Entry Point:** `manage.py` (Django), `static/js/main.js` (Frontend)
- **Architecture Pattern:** Service-Oriented Layered Architecture
- **Database:** PostgreSQL 15+
- **Deployment:** Docker & Docker Compose

## Generated Documentation

**Note:** This directory contains auto-generated and generated documentation. For manually maintained documentation, see the [`documentation/`](../documentation/) directory.

### Core Documentation

- [Project Overview](./project-overview.md) - Executive summary and high-level architecture
- [Source Tree Analysis](./source-tree-analysis.md) - Annotated directory structure
- [Architecture](../documentation/architecture.md) - Maintained system architecture guide
- [Component Inventory](./component-inventory.md) - Catalog of major components and UI elements
- [Development Guide](../documentation/developer_guide.md) - Maintained development workflow and setup guide
- [API Contracts](./api-contracts.md) - API endpoints and schemas
- [Data Models](./data-models.md) - Database schema and models
- [Project Structure](./PROJECT_STRUCTURE.md) - Comprehensive project structure guide

### Status Reports

- [Test Coverage Improvements](./status/test-coverage-improvements.md) - Test coverage status
- [System Status](./status/system-status.md) - Current system status
- [E2E Expansion Progress](./status/e2e-expansion-progress.md) - E2E testing progress
- [E2E Test Implementation Status](./status/e2e-test-implementation-status.md) - E2E implementation status
- [Video Demos Ready](./status/video-demos-ready.md) - Video demos status

### Quick Guides

- [Video Demos Guide](./guides/video-demos-guide.md) - How to generate video demos
- [Video Review Checklist](./guides/video-review-checklist.md) - Video review checklist
- [E2E Quick Fix Guide](./guides/e2e-quick-fix-guide.md) - E2E testing quick fixes

### Operations

- [Production target matrix](./production-target-matrix.md) - Host sizing, Light/Standard/High tiers, coordination-office scenario, cloud patterns, AWS/GCP/Azure calculator BOM, backups, legacy migration, on-premises + cloud DR

### Frontend Migration Notes

- [Vue Migration Plan](./VUE_MIGRATION_PLAN.md) - Historical migration rationale and scope
- [Vue Test Results](./VUE_TEST_RESULTS.md) - Current Vue testing status and rerun instructions

## Manual Documentation

**Note:** The project has extensive manually maintained documentation in the [`documentation/`](../documentation/) directory. This is the authoritative source for:
- Development guidelines
- User guides
- Planning documents
- Implementation details

See [documentation/README.md](../documentation/README.md) for the complete index.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.12+ (for E2E testing and local development tools)

### Setup

```bash
# Clone repository
git clone <repository-url>
cd SEIM

# Copy environment template
cp env.example .env

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create initial data
docker-compose exec web python manage.py create_initial_data

# Restore CMS
docker-compose exec web python manage.py restore_cms

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Run Locally

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access application
# Web: http://localhost:8001/
# Admin: http://localhost:8001/seim/admin/
# CMS Admin: http://localhost:8001/cms/
# API Docs: http://localhost:8001/api/docs/
```

### Run Tests

```bash
# Run all tests (Docker)
make test

# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run E2E tests (host OS, requires virtualenv)
.venv\Scripts\Activate.ps1  # Windows
make test-selenium
```

## For AI-Assisted Development

This documentation was generated specifically to enable AI agents to understand and extend this codebase.

### When Planning New Features:

**UI-only features:**
→ Reference: `documentation/architecture.md`, `component-inventory.md`

**API/Backend features:**
→ Reference: `documentation/architecture.md`, `api-contracts.md`, `data-models.md`

**Full-stack features:**
→ Reference: All architecture docs

**Deployment changes:**
→ Reference: `documentation/developer_guide.md` and `documentation/deployment.md`

### Key Documentation for AI Development:

1. **Understanding the System:**
   - Start with `project-overview.md` for high-level understanding
   - Review `documentation/architecture.md` for technical architecture
   - Check `data-models.md` for database structure

2. **Working with APIs:**
   - `api-contracts.md` - Complete API reference
   - Authentication: JWT via `/api/token/`
   - All endpoints documented with methods and parameters

3. **Working with Data:**
   - `data-models.md` - All models, relationships, and fields
   - Service layer pattern: business logic in services
   - Permission system: check `core/permissions.py`

4. **Frontend Development:**
   - `component-inventory.md` - All UI components
   - JavaScript modules documented
   - Template structure explained

5. **Adding Features:**
   - Follow service layer pattern (business logic in services)
   - Use PermissionManager for access control
   - Add caching for read operations
   - Write tests for new functionality

---

_Generated using BMAD Method `document-project` workflow (Exhaustive Scan)_
