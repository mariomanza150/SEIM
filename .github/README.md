# GitHub Actions CI/CD Workflows

Automated workflows for SEIM: quality gates, tests, container scan, E2E, and deploy.

## Workflows

### 1. CI (`ci.yml`)

Runs on: **push** to `main`, `master`, `develop`, `feature/vue-migration`; **pull request** targeting `main`, `master`, `develop`

**Jobs:** Ruff · **Migration safety** (`makemigrations --check` + `django-migration-linter`; PR label `contract-migration` allows intentional contract steps — see `docs/migrations.md`) · Bandit + `pip-audit` · mypy (non-blocking) · backend pytest (unit + integration, coverage XML) · Vue Vitest + coverage + Vite build · Docker build (Vue dist + collectstatic) + Trivy SARIF · Locust on pull requests only.

**Secrets:** `CODECOV_TOKEN` — required on same-repo CI so coverage uploads to Codecov. Missing token **fails the job** (`scripts/check_codecov_ci.py`). Fork PRs skip the token requirement because GitHub does not expose secrets. Coverage artifacts are still generated. The hard pytest gate is `--cov-fail-under=80`. See setup below.

### 2. Deploy (`deploy.yml`)

Runs on: push to `main` / `master`, or `workflow_dispatch`

**What it does:** Build `Dockerfile.prod`, push to **GHCR** (`ghcr.io/<owner>/<repo>`) as `latest` and `:sha`. Staging job runs on push to default branches; production only via manual workflow with environment `production`.

**Secrets:** uses `GITHUB_TOKEN` for GHCR (no Docker Hub required).

**Environments:** `staging`, `production` (configure reviewers in repo settings).

### 2b. Deploy local-prod (`deploy-local-prod.yml`)

Runs on: **after CI succeeds** on `main` / `master`, or `workflow_dispatch`

**Target:** Docker Compose project **`seim-localprod`** (`docker-compose.local-prod.yml`) on **this machine** — app at `http://localhost:8020`.

**Persistent logs:** named volume `logs_prod_volume` → `/app/logs` on `web`, `celery`, and `celery-beat`, with per-process `LOG_FILE` (`web.log` / `celery.log` / `celery-beat.log`) and Django rotating file handlers. Inspect with e.g. `docker compose -p seim-localprod -f docker-compose.local-prod.yml exec web tail -n 100 /app/logs/web.log`.

**Runner:** requires a **self-hosted** Windows runner with labels `self-hosted`, `windows`, `local-prod`.

**One-time setup:**

1. Copy `env.local-prod.example` → `.env.local-prod` (if not already done).
2. Set a **machine** environment variable `SEIM_REPO` to the absolute path of the local SEIM clone used by the runner (never commit host paths). Optionally set `SEIM_DB_BACKUP_DIR` for pre-migrate `pg_dump` output (default `backups/local-prod` under the repo).
3. GitHub → **Settings → Actions → Runners → New self-hosted runner** (Windows x64). Extract to a local runner directory (example placeholder: `C:\actions-runner\seim-localprod`).
4. Register with labels `self-hosted,windows,local-prod`:
   ```powershell
   $env:RUNNER_TOKEN = "<registration-token>"
   .\scripts\setup-local-prod-runner.ps1 -RunnerDir "<runner-dir>"
   cd <runner-dir>
   .\svc.cmd install
   .\svc.cmd start
   ```
5. Once per machine, elevated: create the maintenance-lock directory (`%ProgramData%\ops`) and give every runner account Modify on it:
   ```powershell
   .\scripts\setup-maintenance-lock-dir.ps1
   ```
6. Push to `main` → CI green → **Deploy local-prod** runs automatically.

**Migrate path:** deploy brings up `db`/`redis`, takes a `pg_dump`, runs the one-shot Compose `migrate` profile, then rolls out app containers. Web startup no longer runs `migrate` or `collectstatic` (statics are baked into `Dockerfile.prod`).

**Local registry (no GHCR):** `deploy/docker-compose.registry.yml` runs `registry:2` on `127.0.0.1:${LOCAL_REGISTRY_PORT:-5000}` only. Deploy builds `LOCAL_REGISTRY/seim-app:<git-sha>` (and `seim-toefl`), smoke-tests the app image (empty Postgres → migrate → `check --deploy` → `/health/live/`), pushes the SHA tag, deploys that exact tag, watches health for 5 minutes, then promotes `last-good`. If health fails during the watch, images roll back to `last-good` (**never** reverts the DB) and a Slack message is posted when `SEIM_DEPLOY_SLACK_WEBHOOK_URL` is set on the runner (document the secret name only — never commit the URL). Configure Docker Engine `insecure-registries` for the loopback address. Do not use a GitHub token or GHCR on this path.

**Maintenance lock and timeouts:** the deploy takes the machine-wide maintenance lock
(`C:\ProgramData\ops\maintenance.lock`, `scripts/maintenance-lock.ps1`, same protocol as local-ai-stack) before the
build, renews it with a heartbeat (TTL 10 min) and releases it at the end, so deploys across repos never overlap and
Otto does not restart containers mid-deploy. Build (8 min), `up --no-build --wait` (4 min), the Created-container
fallback (2 min) and the health check (3 min) each have a hard timeout, all inside an 18-minute budget under the job's
`timeout-minutes: 20`. If `up` hangs, compose is killed and this project's Created containers are started (db and redis
first); the job then passes only if `/health/` answers 200.

**Manual deploy (no runner):**

```powershell
.\scripts\deploy-local-prod.ps1              # pull + rebuild + up
.\scripts\deploy-local-prod.ps1 -SkipPull    # deploy current checkout
make deploy-local-prod-update                # same via Makefile
```

**Boot autostart (Windows):**

```powershell
.\scripts\install-local-prod-boot.ps1
```

This enables Docker Desktop autostart, registers scheduled tasks for the stack (`SEIM-localprod-stack`, 90s after logon) and runner (`SEIM-github-runner`, at logon). For a true Windows **service** for the runner (optional), approve UAC once:

```text
scripts\install-github-runner-service-elevated.cmd
```

### 3. E2E — Playwright (`e2e-tests.yml`)

Runs on: **push** to `main`, `develop`, `master`, `feature/vue-migration`; **PR** targeting `main`, `develop`, `master`; plus manual dispatch.

Playwright against Django in CI (container port 8000). Local dev via Compose uses **http://localhost:8001**. `RUN_SEED_VUE_E2E=1` enables session seed via `tests/e2e_playwright/conftest.py`.

### 4. E2E — Selenium (`e2e-selenium-scheduled.yml`)

Weekly schedule + manual. Legacy `tests/e2e/` and `tests/selenium/` (not on every PR).

### 5. Docker Compose Test (`docker-compose-test.yml`)

Runs on: **push** to `main`, `master`, `develop`, `feature/vue-migration`; **PR** targeting `main`, `master`, `develop`

Uses **`docker compose`** (v2): build, up, migrate, `pytest tests/` in the web container.

### 6. Secret scan (`secret-scan.yml`)

Gitleaks on **push** to `main`, `master`, `develop`, `feature/vue-migration`; **PR** targeting `main`, `master`, `develop`.

## One-time setup (repository Settings)

Do these in [github.com/mariomanza150/SEIM](https://github.com/mariomanza150/SEIM) (requires admin on the repo).

1. **Deploy environments** — [Settings → Environments](https://github.com/mariomanza150/SEIM/settings/environments): create **`staging`** and **`production`**. Optionally add **required reviewers** or **wait timer** on `production` so `deploy.yml` manual production deploys are gated.
2. **Codecov (required for same-repo CI)** — CI always writes coverage reports (backend `coverage.xml`, frontend `frontend-vue/coverage/lcov.info`) and uploads them as artifacts. `scripts/check_codecov_ci.py` **fails the job** when `CODECOV_TOKEN` is missing on this repository (push and same-repo PRs). Fork PRs skip the token requirement. When the token is set, Codecov upload uses `fail_ci_if_error: true`. Local pytest does not need the token.

   1. Sign in at [codecov.io](https://codecov.io) with GitHub and add **`mariomanza150/SEIM`**.
   2. Copy the repository upload token (Settings → General on the Codecov repo page).
   3. In GitHub: [Settings → Secrets and variables → Actions](https://github.com/mariomanza150/SEIM/settings/secrets/actions) → **New repository secret** → name **`CODECOV_TOKEN`** → paste the token only (no `CODECOV_TOKEN=` prefix).
   4. Re-run **CI** on `main` (or merge a PR). Backend uploads flag `backend`; Vue uploads flag `frontend`. Policy lives in [`codecov.yml`](../codecov.yml): backend project/patch statuses fail the Codecov check on drops; frontend stays informational. pytest `--cov-fail-under=80` remains the hard local/CI gate.

   Do not put this token in `.env` or `env.example`. Never commit a real token.
3. **Merge line of work into `main`** — Open a PR from `feature/vue-migration` into `main` ([compare](https://github.com/mariomanza150/SEIM/compare/main...feature/vue-migration?expand=1)). If GitHub reports unrelated histories, merge via the UI using a merge commit or align `main` to this branch using a one-time strategy your team agrees on (replacing the old `main` history is destructive).

## Other automation

- **Dependabot:** [.github/dependabot.yml](dependabot.yml) (pip, npm root + `frontend-vue`, GitHub Actions).

## Running with act

```bash
act -l
act push -W .github/workflows/ci.yml
act push -W .github/workflows/docker-compose-test.yml
```

Optional `.secrets` file: `CODECOV_TOKEN=...` then `act --secret-file .secrets push`.

## Practices

1. CI green before merge.
2. Target coverage policy: pytest `--cov-fail-under=80` is the hard local/CI gate (`pytest.ini` / `pyproject.toml`). Codecov (`codecov.yml`) tracks history and fails the GitHub check when backend coverage drops more than 2% (or new backend lines are under 50% covered). Frontend Codecov status stays informational.
3. Staging deploy follows push to `main`/`master`; production uses protected environment + manual workflow.

## References

- [GitHub Actions](https://docs.github.com/en/actions)
- [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Codecov](https://docs.codecov.com/docs)
- [act](https://github.com/nektos/act)
