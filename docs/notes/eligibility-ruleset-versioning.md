# Eligibility ruleset document versioning + apply-time freeze

_Shipped 2026-08-20 (schema v2) / extended 2026-08-20 (application snapshot)._

## Two version numbers

| Layer | Constant / field | Meaning |
|-------|------------------|---------|
| Evaluation engine payload | `ELIGIBILITY_SCHEMA_VERSION` (`exchange.eligibility_rules`) | Shape of `rules` rows returned by `check_eligibility` / readiness |
| Ruleset **document** | `EligibilityRuleSet.schema_version` + `content_revision` | Format + edit revision of `rules_json` |

Document schema lives in `exchange/eligibility_ruleset_schema.py` (current **v2**). Staff clients can `GET /api/eligibility-rulesets/document-schema/`. Saving invalid v2 payloads returns field errors; `content_revision` bumps only when `rules_json` changes.

## Historical evaluations

On draft create / submit, `ApplicationService.capture_eligibility_snapshot` freezes the active program ruleset onto `Application.eligibility_ruleset_snapshot`:

```json
{
  "id": "<uuid>",
  "name": "…",
  "schema_version": 2,
  "content_revision": 3,
  "is_active": true,
  "rules_json": { "program_overrides": { … } }
}
```

`_program_for_eligibility(program, application=…)` prefers that freeze over the live `Program.eligibility_ruleset`. Draft readiness still evaluates the **live** profile + live ruleset (no application snapshot passed). Re-checks with `application=` (submit parity, API preview) use the freeze when present; response `ruleset.frozen: true`.

## Deferred

- Full revision history table / restore UI for rulesets
- Migrating pre-freeze applications (they keep live-ruleset behavior until recaptured)
- Diff UI between frozen snapshot and current live ruleset
