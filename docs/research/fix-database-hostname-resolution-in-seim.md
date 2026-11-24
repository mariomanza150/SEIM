# Fix database hostname resolution in seim

# Database Hostname Resolution Audit Report

## 1. Context and Investigation
- Investigated GlitchTip Issue #68 (`OperationalError: could not translate host name "db" to address: Temporary failure in name resolution`), originating during database connection establishment in `django/db/backends/postgresql/base.py` via `psycopg2`.
- Examined relevant configuration, settings, and documentation files:
  - `seim/settings/production.py`
  - `seim/settings/development.py`
  - `seim/settings/base.py`
  - `docs/environment_variables.md`
  - `docker-compose.local-prod.yml`
  - `ops.yml`

## 2. Root Cause Analysis
- **Settings Helper Bypass**: `seim/settings/production.py` and `seim/settings/development.py` define `_docker_compose_postgres_service_to_localhost(url: str) -> str` to map the Docker Compose service hostname `db` to loopback `127.0.0.1` when executing on the host OS (e.g. running Gunicorn in `local-prod` behind Tailscale Serve, running management commands, or running tests outside containers).
- **`dj_database_url.config` Behavior**: When `dj_database_url.config(default=...)` is used, `dj_database_url` reads `os.environ['DATABASE_URL']` directly whenever `DATABASE_URL` is present in the environment, completely ignoring the `default` parameter. As a result, any pre-mapping wrapped in `default=` is disregarded, and the raw URL containing hostname `db` is parsed directly into `DATABASES['default']['HOST']`.
- **Hostname Resolution Failure**: Outside Docker Compose's user-defined network bridge (where Docker internal DNS daemon `127.0.0.11` resolves container service names), host OS DNS resolvers fail to translate the single-label hostname `db`, triggering `psycopg2.OperationalError: could not translate host name "db" to address: Temporary failure in name resolution`.
- **Edge Case Fragility**: Existing URL transformation logic does not guard against `None` or empty `url` values, and naive string replacements risk corrupting database passwords containing the substring `db`.

## 3. Recommended Architectural Changes
- Update `seim/settings/production.py` and `seim/settings/development.py` to extract `DATABASE_URL` (or default), pass it through `_docker_compose_postgres_service_to_localhost`, and parse the resulting mapped URL using `dj_database_url.parse` rather than `dj_database_url.config`.
- Implement robust hostname detection in `_docker_compose_postgres_service_to_localhost`:
  - Check container presence markers (`/.dockerenv`, `/run/.containerenv`).
  - Probe DNS resolution of `db` via `socket.getaddrinfo('db', None)`. If resolution fails (`socket.gaierror`) or container markers are absent, rewrite hostname `'db'` to `'127.0.0.1'`.
  - Use `urllib.parse.urlsplit` and `urllib.parse.urlunsplit` to safely mutate only the host component while preserving user credentials, passwords, and ports.
- Add unit tests in `tests/unit/test_database_host_resolution.py` verifying host vs container resolution, `None`/empty input handling, and password preservation.
- Update `docs/environment_variables.md` to document the fallback mechanism.

## 4. Decisions for Mario (Production / DevOps Boundary)
- Agent pull requests will be based on and target the `testing` branch. Promotion to `main` remains Mario's responsibility upon release.
- Any direct modifications to production host infrastructure, production secrets, Tailscale Serve routing, or production CI/CD workflows (`.github/workflows/ci.yml`) are reserved for Mario's review and decision.
