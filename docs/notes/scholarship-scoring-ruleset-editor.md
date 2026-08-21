# Scholarship scoring ruleset editor (2026-08-20)

## Shipped (MVP)

- Model `ScholarshipScoringRuleset` (`slug`, `label`, `factor_weights` JSON, single `is_active`).
- Scoring (`compute_scholarship_allocation_score`) reads the active ruleset’s factor max weights; v1 factor *formulas* are unchanged (bands scale with the max).
- Staff API: `/api/scholarship-scoring-rulesets/` (+ `GET …/active/`).
- SPA: `/seim/scholarship-scoring-rulesets` (list + edit weights), i18n en/es.

## Deferred

- Custom / alternate factor formulas (not just max weights).
- Per-program ruleset assignment.
- Workflow hooks that gate awards on score thresholds.
- Version history / audit of weight changes beyond `updated_at`.
