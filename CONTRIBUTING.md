# Contributing to SEIM

Thank you for your interest in contributing to the Student Exchange Information Manager (SEIM).

SEIM is a Django 5.1 + DRF backend that serves a Vue 3 SPA (`/seim/`), a Wagtail CMS (`/`, `/cms/`), and a REST API (`/api/`).

## Getting Started

1. **Fork** the repository and clone your fork.
2. **Set up** the development environment (Docker is the documented path; see below).
3. **Create a branch** for your change:
   ```powershell
   git checkout -b feature/your-feature-name
   ```

## Running the app

### Docker (documented path)

```powershell
copy env.example .env
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py create_initial_data
docker-compose exec web python manage.py seed_demo_readiness
docker-compose exec web python manage.py restore_cms
```

Then open:

- Public / CMS: http://localhost:8001/
- Vue SPA: http://localhost:8001/seim/
- API docs: http://localhost:8001/api/docs/
- Django admin: http://localhost:8001/admin/

Demo accounts from `seed_demo_readiness`: `admin@test.com` / `admin123`, `coordinator@test.com` / `coordinator123`, `student@test.com` / `student123`.

Full install steps: [documentation/installation.md](documentation/installation.md).

### Native PostgreSQL + Redis

Docker is the supported contributor path. If you run Django on the host instead (for example a Cloud VM), start local PostgreSQL and Redis first, point `.env` at `localhost` (not Compose hostnames `db` / `redis`), use `seim.settings.development`, and build the SPA:

```powershell
npm --prefix frontend-vue run build
python manage.py collectstatic --noinput
```

SQLite is rejected in development settings. See [AGENTS.md](AGENTS.md) for the native layout.

## Where the UI lives

| Surface | Path | Code |
| --- | --- | --- |
| Vue 3 SPA | `/seim/` | `frontend-vue/` |
| Wagtail CMS / public site | `/`, `/cms/` | `cms/` |
| REST API | `/api/` | domain apps + `api/urls.py` |

The legacy Django template frontend has been removed. Do not add new pages under a `frontend/` Django app. Current split: [documentation/notes/SPA_VS_LEGACY.md](documentation/notes/SPA_VS_LEGACY.md).

## Tests

```powershell
make test
npm --prefix frontend-vue run test:run
```

- Backend unit/integration: `pytest` via `make test` (Docker). Settings module: `seim.settings.test`.
- Vue unit tests: Vitest in `frontend-vue/`.
- Playwright E2E: `make e2e-test`.
- Legacy Selenium: `SEIM_RUN_SELENIUM=1 make test-selenium` (host OS, not Docker).

More detail: [documentation/testing.md](documentation/testing.md).

## Lint and quality

```powershell
make quality-check
make pre-commit-install
```

Or individually: `ruff check .`, `ruff format .`. CI runs Ruff, Bandit, backend pytest, Vue Vitest + Vite build, and related jobs on PRs to `main`.

## Branching and pull requests

- Use descriptive prefixes: `feature/`, `bugfix/`, `docs/`.
- Keep the branch up to date with `main`.
- Open a PR against `main` and fill in `.github/PULL_REQUEST_TEMPLATE.md`.
- Reference related issues. CI must be green.

## Commit messages

Use a clear, descriptive message, for example: `fix: correct document upload validation`.

## Issues and feature requests

Use the GitHub issue templates (bug report or feature request). Include environment (Docker vs native), role, and whether the problem is SPA, API, or CMS.

- Issues: https://github.com/mariomanza150/SEIM/issues

## Code review

All changes need review before merge. Address comments; keep feedback specific and respectful.

## Security

Report security issues privately to the maintainer. Do not open a public issue with secrets, tokens, or `.env` contents.

## Documentation

- Authoritative guides live in `documentation/` ([index](documentation/README.md)).
- Working notes live in `documentation/notes/` ([notes/README.md](documentation/notes/README.md)).
- `docs/` is a deprecated pointer ([docs/README.md](docs/README.md)).
- `documents/` is the Django file-upload app, not a docs tree ([documents/README.md](documents/README.md)).
- Prefer Makefile/Docker targets for generated docs (`make docs-workflow`).
- Update docstrings when behavior changes.

## Python dependencies

Pins live in `pyproject.toml` (`[project.dependencies]` and `[project.optional-dependencies]` for `dev`, `test`, and `docs`). Docker and CI install from that file (`pip install -e ".[dev]"` / `".[test]"`). After changing a pin, commit `pyproject.toml` only. `python scripts/check_python_deps.py` (or `make check-deps`) rejects leftover `requirements*.txt` files.

Coverage reports are always generated in CI. Maintainers must set the GitHub Actions secret `CODECOV_TOKEN` so uploads run on this repo; pushes to `main`/`master` fail if the secret is missing. Fork PRs skip upload and stay green. See [`.github/README.md`](.github/README.md).

## License

SEIM is MIT. See [LICENSE](LICENSE).

## Questions?

See [Support & Contact](README.md#support--contact) or open an issue.
