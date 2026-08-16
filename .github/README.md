# GitHub Actions CI/CD Workflows

Automated workflows for SEIM: quality gates, tests, container scan, E2E, and deploy.

## Workflows

### 1. CI (`ci.yml`)

Runs on: **push** to `main`, `master`, `develop`, `feature/vue-migration`; **pull request** targeting `main`, `master`, `develop`

**Jobs:** Ruff · Bandit + `pip-audit` · mypy (non-blocking) · backend pytest (unit + integration, coverage XML) · Vue Vitest + coverage + Vite build · Docker build (Vue dist + collectstatic) + Trivy SARIF · Locust on pull requests only.

**Secrets:** `CODECOV_TOKEN` — add this so CI can upload coverage to Codecov. When it is missing, CI still generates coverage artifacts, warns, and stays green. Fork PRs skip upload. The hard gate is pytest `--cov-fail-under=80`. See setup below.

### 2. Deploy (`deploy.yml`)

Runs on: push to `main` / `master`, or `workflow_dispatch`

**What it does:** Build `Dockerfile.prod`, push to **GHCR** (`ghcr.io/<owner>/<repo>`) as `latest` and `:sha`. Staging job runs on push to default branches; production only via manual workflow with environment `production`.

**Secrets:** uses `GITHUB_TOKEN` for GHCR (no Docker Hub required).

**Environments:** `staging`, `production` (configure reviewers in repo settings).

### 3. E2E — Playwright (`e2e-tests.yml`)

Runs on: **push** to `main`, `develop`, `master`, `feature/vue-migration`; **PR** targeting `main`, `develop`, `master`; plus manual dispatch.

Playwright against Django on port 8000; `RUN_SEED_VUE_E2E=1` enables session seed via `tests/e2e_playwright/conftest.py`.

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
2. **Codecov (recommended for production metrics on this repo)** — CI always writes coverage reports (backend `coverage.xml`, frontend `frontend-vue/coverage/lcov.info`) and uploads them as artifacts. When `CODECOV_TOKEN` is set, CI uploads to Codecov and a failed upload **fails the job**. When the secret is missing, upload is skipped, CI emits a warning, and the job stays green (fork PRs, local `act` without `.secrets`, or this repo before the secret is added). Maintainers should still set the secret so Codecov history is tracked.

   1. Sign in at [codecov.io](https://codecov.io) with GitHub and add **`mariomanza150/SEIM`**.
   2. Copy the repository upload token (Settings → General on the Codecov repo page).
   3. In GitHub: [Settings → Secrets and variables → Actions](https://github.com/mariomanza150/SEIM/settings/secrets/actions) → **New repository secret** → name **`CODECOV_TOKEN`** → paste the token only (no `CODECOV_TOKEN=` prefix).
   4. Re-run **CI** on `main` (or merge a PR). Backend uploads flag `backend`; Vue uploads flag `frontend`. Policy lives in [`codecov.yml`](../codecov.yml): backend project/patch statuses fail the Codecov check on drops; frontend stays informational. pytest `--cov-fail-under=80` remains the hard local/CI gate.

   The job summary states when the secret is missing. Do not put this token in `.env` or `env.example`. Never commit a real token.
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
