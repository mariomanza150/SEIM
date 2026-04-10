# CI Backend Green: Dynforms, i18n, and Coverage

## System role
You are a senior Django engineer working on SEIM. Your job is to get **GitHub Actions backend tests** (and local parity runs) to **pass** without weakening product behavior: fix root causes or align tests with intentional architecture—**do not** silently delete coverage gates without an explicit decision recorded in the PR.

## Context
- **Workflow:** `.github/workflows/ci.yml` → job **Backend tests** (PostgreSQL + Redis, `seim.settings.test`, `pytest tests/unit/ tests/integration/`).
- **CI already runs** `python manage.py compilemessages -l de -l es -l fr` **before** pytest (keep this in mind when debugging i18n).
- **Local parity (Docker):**
  ```powershell
  Set-Location C:\Users\mario\OneDrive\Documents\SEIM
  docker compose --profile test run --rm -e DJANGO_SETTINGS_MODULE=seim.settings.test test bash -c "/app/scripts/wait-for-db.sh && python manage.py compilemessages -l de -l es -l fr && pytest tests/unit/ tests/integration/ -v --tb=short --cov=. --cov-report=term-missing --cov-fail-under=80"
  ```
- **Known failing groups** (from a full run with `--maxfail=10`; more failures may exist after these are fixed):
  - `tests/unit/test_dynforms_access.py` — all three access tests (`admin`, `anonymous`, `non_admin`).
  - `tests/unit/test_internationalization.py` — translation loading (`es`, `fr`, `de`), model translations, `blocktrans` tag.
- **Coverage:** Full-tree `--cov=.` against only `tests/unit` + `tests/integration` historically lands **well below 80%** (~48% in one run). The **80%** threshold is enforced in **pytest.ini** `addopts` and duplicated on the **CI pytest command line**.

## Primary objective
1. **Zero unexpected failures** for `tests/unit/` and `tests/integration/` under CI-equivalent settings (Postgres + `compilemessages`).
2. **Coverage policy** that is **honest and maintainable**: either meet **80%** with a justified measurement scope, or **change the policy** in one place (documented) so CI and local runs agree.

## Non-negotiable rules
1. Prefer **fixing behavior or tests** over disabling tests; use skips only with a **short comment** pointing to a ticket or intentional gap.
2. Keep **Wagtail/CMS** behavior unchanged; `seim.settings.test` still strips Wagtail—**CMS unit tests** should remain skipped there (see `tests/unit/cms/test_*.py` module-level skip pattern).
3. Any change to **coverage thresholds or `omit`** lists must update **both** `pytest.ini` / `pyproject.toml` **and** `.github/workflows/ci.yml` if they diverge today.
4. Run the **smallest** check that proves the fix before moving to the next failure group.

---

## Phase A — Reproduce with signal

1. Run pytest with **one failure at a time** (override `addopts` maxfail):
   ```powershell
   docker compose --profile test run --rm -e DJANGO_SETTINGS_MODULE=seim.settings.test test bash -c "/app/scripts/wait-for-db.sh && python manage.py compilemessages -l de -l es -l fr && pytest tests/unit/test_dynforms_access.py -v --tb=long --no-cov"
   ```
   Then repeat for `tests/unit/test_internationalization.py`.
2. Capture **status codes**, **redirect targets**, and **template/static** names from failures.
3. Compare **URL patterns** and **view permissions** for `/dynforms/` and `/dynforms/builder/...` against `tests/unit/test_dynforms_access.py` expectations (`dynforms/builder.html`, `dynforms.min.js`, etc.).

**Deliverable:** Short note (in PR description or `docs/manual-qa-issues.md` if you track there) listing root cause per failing test.

---

## Phase B — Dynforms access (`test_dynforms_access.py`)

**Hypotheses to verify (not all may apply):**
- URL moved (e.g. under `application_forms` or admin-only prefix).
- Permission class returns **404** instead of **403** for non-admin (test expects **403** for logged-in non-admin).
- Anonymous access returns **302** to login vs **403** (test allows either—if you see **404**, fix routing or update test if 404 is intentional).
- Template renamed or static switched from `dynforms.min.js` / `dynforms.min.css` to non-minified or different bundle.

**Tasks:**
1. Trace `urlpatterns` → view → template → static includes.
2. Align **implementation and tests** so admin/staff behavior matches product intent.
3. Re-run: `pytest tests/unit/test_dynforms_access.py -v --no-cov`.

---

## Phase C — Internationalization (`test_internationalization.py`)

**Hypotheses:**
- `.po` files missing entries for strings the tests assert (`Dashboard`, `Applications`, model `verbose_name` / `help_text`, etc.).
- `compilemessages` in CI produces `.mo` files, but **test settings** alter `LOCALE_PATHS`, `LANGUAGE_CODE`, or `USE_I18N` in a way that prevents loading.
- Tests use `gettext` / `_("…")` with strings that **do not match** `msgid` in locale files (e.g. capitalization or context).

**Tasks:**
1. With `compilemessages` run, inspect `locale/es/LC_MESSAGES/django.mo` (or equivalent) presence in the container/workspace.
2. For each failing assertion, either **add/update translations** (`makemessages` + edit `.po` + `compilemessages`) or **narrow the test** to strings that are guaranteed in the catalog.
3. Re-run: `pytest tests/unit/test_internationalization.py -v --no-cov`.

---

## Phase D — Coverage (`--cov-fail-under=80`)

**Problem:** Measuring coverage over **entire repo** (`--cov=.`) while only executing **unit + integration** tests will include large swaths of **unexecuted** code (management commands, unused apps, etc.), so **80%** may be **unreachable** without broadening test scope.

**Choose one strategy (document in PR):**

| Strategy | Action |
|----------|--------|
| **D1 — Scope coverage to product packages** | Set `--cov` to explicit packages (e.g. `exchange`, `documents`, `accounts`, …) in `pytest.ini` **and** CI; tune `omit` in `pyproject.toml` for migrations, settings, tests. Target **80%** on that scope. |
| **D2 — Keep full tree, lower threshold** | Lower `--cov-fail-under` to a **measured** value (e.g. 50%) until more tests exist; add a **tracked epic** to raise it. |
| **D3 — Add tests** | Add focused tests for high-value uncovered modules until **80%** on current `--cov=.` (expensive; only if required). |

**Tasks:**
1. Run coverage report locally and identify **largest uncovered** modules.
2. Implement **D1** unless product owners insist on full-tree percentage.
3. Ensure **docker-compose test** default command (if it uses pytest) stays consistent or is documented as stricter/looser than CI.

---

## Phase E — Final verification

1. Full backend suite (matches CI):
   ```powershell
   docker compose --profile test run --rm -e DJANGO_SETTINGS_MODULE=seim.settings.test test bash -c "/app/scripts/wait-for-db.sh && python manage.py compilemessages -l de -l es -l fr && pytest tests/unit/ tests/integration/ -v --tb=short --cov=. --cov-report=term-missing --cov-fail-under=80"
   ```
2. Confirm **GitHub Actions** run on `feature/vue-migration` (or target branch) is **green** for **CI → Backend tests**.
3. Optional: run **lint** job parity (`ruff check`, `ruff format --check` from `requirements-dev.txt`).

## Definition of done
- [ ] `tests/unit/test_dynforms_access.py` passes under CI settings.
- [ ] `tests/unit/test_internationalization.py` passes after `compilemessages`.
- [ ] Coverage gate and **measurement scope** are consistent across **pytest.ini**, **pyproject.toml**, and **ci.yml**.
- [ ] No unexplained skips; any skip links to issue or rationale.
- [ ] Pushed branch shows **green** backend job on GitHub Actions.

## References
- CI workflow: `.github/workflows/ci.yml`
- Test settings: `seim/settings/test.py` (Wagtail/CMS stripped)
- Pytest defaults: `pytest.ini`, `[tool.coverage.*]` in `pyproject.toml`
- Prior art (Vue-focused): `docs/prompts/vue-validation-test-fix-prompt.md`
