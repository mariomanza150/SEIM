set windows-shell := ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command"]

export SECRET_KEY := env("SECRET_KEY", "local-test-only")

python := if os_family() == "windows" { ".venv\\Scripts\\python.exe" } else { ".venv/bin/python" }
bootstrap_python := if os_family() == "windows" { "py -3.12" } else { "python3.12" }
curl := if os_family() == "windows" { "curl.exe" } else { "curl" }
health_url := env("HEALTH_URL", "http://localhost:8001/health/")

default:
    @just --list

# Create .venv, install backend + Vue deps and the git hooks
setup:
    {{ bootstrap_python }} -m venv .venv
    {{ python }} -m pip install -e ".[dev]"
    npm --prefix frontend-vue ci
    {{ python }} -m pre_commit install

# Same gates as the CI lint job
lint:
    {{ python }} -m ruff check .
    {{ python }} -m ruff format --check .

fmt:
    {{ python }} -m ruff check --fix .
    {{ python }} -m ruff format .

# Unit tests on seim.settings.test (SQLite unless DATABASE_URL is set) + Vue vitest
test *args:
    {{ python }} -m pytest tests/unit -q --no-cov -o addopts= --ds=seim.settings.test -m "not e2e and not e2e_playwright" --ignore=tests/unit/frontend {{ args }}
    npm --prefix frontend-vue run test:run

# mypy is advisory (CI runs it non-blocking)
typecheck:
    {{ python }} -m mypy . --ignore-missing-imports

up:
    docker compose up -d --build

down:
    docker compose down

logs service="":
    docker compose logs -f --tail=200 {{ service }}

health:
    {{ curl }} -sS --fail-with-body {{ health_url }}
