> **Snapshot (2026-11).** Planning history; completed items are tracked in [changelog.md](changelog.md). Do not treat task lists as the live backlog. **Superseded for gap/priority decisions by** [`notes/gap-audit-2026-08-20.md`](notes/gap-audit-2026-08-20.md) (+ [`notes/feature-tracking.md`](notes/feature-tracking.md)).

# SEIM Roadmap

This roadmap outlines completed milestones and optional future directions. Open work lives in GitHub Issues and the gap/feature trackers linked above.

## Milestones

### Phase 1: Core Platform [✅ COMPLETED]
- ✅ Project scaffolding and initial setup
- ✅ User authentication and role-based permissions
- ✅ Student application workflow (draft, submit, review, approve/reject, complete)
- ✅ Secure document upload and validation
- ✅ Admin / staff dashboards (Vue SPA at `/seim/`)
- ✅ Vue 3 SPA with Bootstrap 5 (Django template frontend removed)
- ✅ API endpoints and documentation

### Phase 2: Communication & Notifications [✅ COMPLETED]
- ✅ Email and in-app notifications
- ✅ Background task processing with Celery
- ✅ Notification preferences and templates
- ✅ WebSocket delivery for in-app updates

### Phase 3: Analytics & Reporting [✅ COMPLETED]
- ✅ Analytics dashboard
- ✅ Exportable reports (CSV / Excel / PDF)
- ✅ Staff forecast views in the SPA

### Phase 4: API & Integrations [✅ COMPLETED]
- ✅ RESTful API endpoints
- ✅ Automated API documentation (OpenAPI / Swagger UI)
- ✅ JWT authentication
- ✅ Optional third-party integrations (e.g. S3-compatible storage)

### Phase 5: Production Readiness [✅ COMPLETED]
- ✅ Deployment scripts and documentation
- ✅ Security hardening and dependency scanning in CI
- ✅ Docker containerization
- ✅ Test suite (pytest 80% coverage gate, Vitest, Playwright E2E)
- ✅ CI/CD (`.github/workflows/ci.yml` and related workflows)
- ✅ Internationalization foundation (Django locales + Vue `vue-i18n` en/es)

## Current Status

**MVP Status: COMPLETE**  
Core exchange workflows are implemented and exercised in CI.

**Production readiness: CI-backed**  
Unit/integration coverage is gated at 80%. Remaining work is product polish and items tracked in [`notes/feature-tracking.md`](notes/feature-tracking.md) (not a missing test/CI foundation).

## Optional next themes

These are directions, not commitments. Prefer GitHub Issues for concrete tasks.

1. **Deeper i18n / a11y** — more locales, full manual accessibility audit
2. **Partner / nomination polish** — richer partner document review beyond the repository list
3. **External calendar sync** — beyond ICS/webcal subscribe (e.g. OAuth providers)
4. **White-labeling depth** — see [white_labeling.md](white_labeling.md)

---

For questions, see [Support & Contact](../README.md#support--contact). Report vulnerabilities via [SECURITY.md](../SECURITY.md).
