# SEIM System Status Report
**Date:** August 20, 2026  
**Status:** ✅ Production-ready codebase; use demo seed for walkthrough data

---

## Summary

This file is a **living pointer**, not a database snapshot. Inventory counts below the November 2025 section are **historical** and do not reflect a fresh database.

For current stack facts (Django 5.2, Vue 3.5, Playwright E2E, ports, admin URLs), see [docs/README.md](../../README.md) **Current State**.

For reproducible demo data after reset:

```bash
docker compose exec web python manage.py create_initial_data
docker compose exec web python manage.py seed_demo_readiness
docker compose exec web python manage.py restore_cms
```

Demo credentials: `admin@test.com` / `admin123`, `coordinator@test.com` / `coordinator123`, `student@test.com` / `student123`, `partner@test.com` / `partner123`.

Recent QA evidence: [docs/notes/qa-runs/](../qa-runs/) (August 2026 manual runs at `http://localhost:8001` and local-prod `http://localhost:8020`).

---

## Historical snapshot (November 20, 2025)

> Preserved for audit trail only. User/program counts may not match a fresh `seed_demo_readiness` run.

All pending issues at that time had been resolved and the system was filled with test data for manual QA.
