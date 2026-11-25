# Django migrations: expand / contract

SEIM deploys to a live local-prod stack after every merge to `main`. App containers
and the database schema must stay compatible across a rollout: briefly, **old and
new app code may run against the same schema**. Breaking that invariant causes
outages even when CI is green.

## CI gates

CI runs `scripts/ci_check_migrations.py`:

1. **`makemigrations --check --dry-run`** — model changes must ship with migration
   files. Missing migrations fail the build.
2. **`django-migration-linter`** on **first-party apps only**, for migrations
   introduced since the PR base (or push parent). Operations that break the
   previous app version (for example `RemoveField`, `RenameField`,
   `DeleteModel`, incompatible `AlterField`) fail the build. Historical and
   third-party migrations are not re-checked.

### Escape hatch: `contract-migration` label

Add the repository label **`contract-migration`** to a pull request only when the
migration is an intentional **contract** step (removing something the previous
release no longer needs). The linter still runs; CI prints a warning and allows
the PR. `makemigrations --check` is never skipped.

Create the label once under GitHub → Issues → Labels if it does not exist
(name exactly `contract-migration`). Do not use it for ordinary feature work.

## Expand / contract pattern

Split schema work into at least two deploys:

| Phase | Schema change | App code | Label? |
| :--- | :--- | :--- | :--- |
| **Expand** | Additive only: `AddField` (nullable or with default), new table, new index | New code writes both old and new shapes when needed; readers tolerate either | No |
| **Migrate data** (optional) | Backfill / dual-write cleanup via management command or data migration that does not drop the old shape | Still dual-compatible | No |
| **Contract** | Drop / rename / tighten nullability once nothing reads the old shape | Code that only uses the new shape is already on `main` | Yes — `contract-migration` |

### Safe (expand) examples

- Add a nullable column, then backfill, then (later) set `null=False` in a
  **contract** PR after all rows are filled and old code is gone.
- Add a new table or M2M; keep the old relation until readers switch.
- Create an index concurrently-friendly in Postgres via `AddIndex` when downtime
  is unacceptable (follow Django/`RunSQL` guidance for large tables).

### Unsafe (contract) examples — need the label, and a prior expand release

- `RemoveField` / `DeleteModel`
- `RenameField` / `RenameModel` (prefer add-new + copy + remove-old)
- `AlterField` that changes type or drops nullability while old code still runs
- `AlterUniqueTogether` / constraint changes that reject rows old writers insert

## Local checks

```bash
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=seim.settings.test
# Postgres + Redis required (see AGENTS.md)
python scripts/ci_check_migrations.py
```

To simulate the label locally:

```bash
python scripts/ci_check_migrations.py --allow-contract
# or: SEIM_ALLOW_CONTRACT_MIGRATION=1 python scripts/ci_check_migrations.py
```

## Related

- Deploy overview: [deployment.md](deployment.md)
- Environment reference: [environment_variables.md](environment_variables.md)
