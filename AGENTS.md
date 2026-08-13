# AGENTS.md

## Cursor Cloud specific instructions

SEIM is a single Django 5.1 + DRF backend that serves a Vue 3 SPA (`/seim/*`), a Wagtail CMS (`/`, `/cms/`), and a REST API (`/api/*`). Although the repo docs recommend Docker, the Cursor Cloud VM runs it **natively** (no Docker) against system PostgreSQL + Redis. The startup update script only refreshes dependencies; the notes below cover everything else.

### Services and how to start them
Nothing auto-starts on boot. Start PostgreSQL and Redis once per session before running the app or tests:

```bash
sudo pg_ctlcluster 16 main start   # PostgreSQL (system service on 5432)
sudo redis-server --daemonize yes   # Redis (6379)
```

Run the Django dev server (ASGI/WebSockets work via runserver):

```bash
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=seim.settings.development
python manage.py runserver 0.0.0.0:8001
```

App is at http://localhost:8001/ — SPA `/seim/`, admin `/admin/`, API docs `/api/docs/`, health `/health/`.

### Environment gotchas (non-obvious)
- The dev/prod settings **auto-rewrite** the Compose hostnames `db`→`127.0.0.1:5434` and `redis`→`127.0.0.1:6379` only when the host is literally `db`/`redis`. The committed `.env` here uses `localhost:5432` / `localhost:6379` directly (native Postgres listens on the default 5432, not 5434), so no rewrite happens. Keep `.env` pointing at `localhost`.
- DB credentials: database `seim`, user `seimuser` / `seimpass` (owner). Created once; persists in the VM snapshot.
- SQLite is hard-rejected in `development.py`; PostgreSQL is mandatory.
- The Vue SPA build output `frontend-vue/dist` is **not** produced by the update script. Until you run `npm --prefix frontend-vue run build`, `development.py` serves a "missing dist" placeholder for `/seim/*` instead of crashing. Build it to exercise the real SPA:
  ```bash
  npm --prefix frontend-vue run build
  python manage.py collectstatic --noinput
  ```
- API login is `POST /api/login/` and expects a `login` field (email or username), not `email`. Returns JWT `access`/`refresh`.

### Demo seed
`manage.py seed_demo_readiness` seeds deterministic demo users, programs, exchange agreements, applications, documents, and notifications without the removed `partner_reference_id` field. Use `manage.py create_initial_data` first (roles, statuses, document/notification types, mobility schemes, profile catalogs) plus a manually created superuser. Demo credentials: `admin@test.com` / `admin123`, `coordinator@test.com` / `coordinator123`, `student@test.com` / `student123`.

### Lint / test / build (standard commands live in the Makefile & CLAUDE.md)
Run these against the venv (the Makefile targets assume Docker, so invoke tools directly here):
- Lint: `.venv/bin/ruff check .` (repo currently has pre-existing ruff findings).
- Backend tests: `.venv/bin/python -m pytest tests/unit tests/integration` — uses `seim.settings.test` (also needs Postgres+Redis running). Full run enforces `--cov-fail-under=80`; for a subset override with `-o addopts="--ds=seim.settings.test -m 'not e2e and not e2e_playwright'"`.
- Frontend unit tests: `npm --prefix frontend-vue run test:run` (Vitest) and root `npx jest --config jest.config.js` (Jest).
- Vue build: `npm --prefix frontend-vue run build`.
