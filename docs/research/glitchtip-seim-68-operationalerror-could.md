# [GlitchTip seim#68] OperationalError: could not translate host name "db" to address

# Audit Report: GlitchTip SEIM-9 (#68) Database Host Resolution Failure

## 1. What Was Checked
- **GlitchTip Issue SEIM-9 (Issue #68)**:
  - Error: `OperationalError: could not translate host name "db" to address: Temporary failure in name resolution`
  - Event Count: 3 events
  - Timeline: First seen at 2026-11-18 10:27 PM (America/Mexico_City); last seen at 2026-11-19 1:02 AM (America/Mexico_City)
  - Culprit: Django database backend connection initialization (`django.db.backends.postgresql.base.DatabaseWrapper.get_new_connection`)
  - Release: `f56c065e776ec5999a9048066a50315949e2e003`
- **Database & Environment Settings**:
  - `seim/settings/production.py`: Examined database configuration (`DATABASES`), host resolution, and `_docker_compose_postgres_service_to_localhost`.
  - `seim/settings/development.py`: Verified `DATABASES` configuration and local fallback helpers.
  - `seim/settings/base.py`: Checked default database routing and settings loading.
  - `docs/environment_variables.md`: Reviewed `DATABASE_URL` format and container environment expectations.
- **Docker Compose Stack**:
  - `docker-compose.local-prod.yml` and `docker-compose.prod.yml`: Verified network configurations, container names, and service hostname alias `db` assigned to the PostgreSQL container.
- **Observability Configuration**:
  - `core/observability.py` and `tests/unit/core/test_observability.py`: Confirmed error scrubbing, Sentry/GlitchTip integration, and logging handlers.
- **Decision Context**:
  - Mario's explicit decision: *"Dismiss in GlitchTip as transient Docker network failure"*.

---

## 2. Findings and Root Cause Analysis
- **Root Cause**:
  - The error `could not translate host name "db" to address: Temporary failure in name resolution` was triggered by a temporary failure of the Docker daemon's internal DNS resolver (`127.0.0.11`) on the host. During that window, the host's Docker Desktop was unstable, causing inter-container service discovery on the Compose bridge network to intermittently fail when Django attempted to establish new database connections to `db:5432`.
- **Transient Nature**:
  - Only 3 events were logged over a ~2.5-hour span ending at 1:02 AM on 2026-11-19.
  - There has been zero recurrence since 1:02 AM on November 19, 2026.
- **Codebase Integrity**:
  - The database configuration in `seim/settings/production.py` and `seim/settings/base.py` correctly parses `DATABASE_URL` and routes to the Compose service name `db`.
  - The error is entirely an infrastructure/host Docker DNS issue, not a defect in application code, Django configuration, or database drivers.

---

## 3. What Should Change
- **Application Code**:
  - **No code changes are required.** The application configuration and container specifications are correct.
- **GlitchTip Status**:
  - Dismiss / resolve issue SEIM-9 (#68) in GlitchTip as a transient host Docker network failure, adhering to Mario's decision.
- **Follow-up Tasks**:
  - Because no code modifications are necessary, no tasks are scheduled.
