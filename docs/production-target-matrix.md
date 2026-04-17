# Production target matrix (recommended sizing)

This document recommends **host sizing** and **Compose-scale knobs** for SEIM when deploying with `docker-compose.prod.yml` and `.env.prod` (see `env.prod.example`). Values are starting points; tune using metrics (latency, queue depth, DB connections, Redis memory, ClamAV scan time).

**Related:** `documentation/deployment.md`, `docker-compose.prod.yml`, `env.prod.example`.

## Assumptions

- **Web tier:** Gunicorn WSGI (`seim.wsgi:application`) as in production compose.
- **Workers:** Celery for email, notifications, and background work; **Celery Beat** runs as a **single** scheduler (`celery-beat` service).
- **Data:** PostgreSQL 15, Redis 7.2 (broker + cache + sessions), optional ClamAV for uploads.
- **WebSockets:** Dev uses Daphne (ASGI). Production compose uses **Gunicorn WSGI**; if you need Channels/WebSockets in production, plan a separate ASGI deployment path and Nginx WebSocket proxying (not covered by default prod compose).

## Tier summary

| Tier | Typical use | Approx. concurrent users* | vCPU | RAM | SSD (data + logs + backups) |
|------|-------------|---------------------------|------|-----|---------------------------|
| **Light** | Pilot, small department, low upload volume | ~10–50 | 2 | 8 GB | 80 GB |
| **Standard** | Campus-wide steady load, moderate documents | ~50–200 | 4 | 16 GB | 150 GB |
| **High** | Many programs, heavy API + uploads, peak periods | ~200–500+ | 8+ | 32 GB+ | 300 GB+ (consider splitting DB) |

\*Rough interactive/API concurrency; not a hard SLA. Validate with load tests.

## Application scaling (`.env.prod`)

Set these in `.env.prod` (see `env.prod.example`). Defaults in the example are **Light/Standard** friendly.

| Tier | `WEB_REPLICAS` | `GUNICORN_WORKERS` | `GUNICORN_WORKER_CLASS` | `GUNICORN_TIMEOUT` (s) | `CELERY_REPLICAS` | `CELERY_CONCURRENCY` |
|------|----------------|--------------------|-------------------------|------------------------|-------------------|----------------------|
| **Light** | 1 | 2–3 | `sync` | 30 | 1 | 2–4 |
| **Standard** | 2 | 3–4 | `sync` | 30–60 | 2 | 4–6 |
| **High** | 2–4 | 4–5 | `sync` or `gevent`† | 60 | 2–4 | 6–8 |

† **`gevent`** can help I/O-bound API traffic; validate compatibility with your middleware and DB drivers before switching. `Dockerfile.prod` installs `gunicorn[gevent]`.

**Rule of thumb for `GUNICORN_WORKERS`:** start with **(2 × CPU cores available to the web containers) + 1** per replica, then reduce if memory is tight. Each worker is a separate process.

## Container memory (align with host)

`docker-compose.prod.yml` sets per-service **memory limits**. Ensure the **sum of limits** for all replicas + **headroom for OS and Docker** fits the VM. Example direction:

| Tier | Web (per replica limit) | DB | Redis | ClamAV | Celery (per replica) | Beat | Nginx |
|------|-------------------------|-----|-------|--------|----------------------|------|-------|
| **Light** | 2G × 1 | 1G | 512M | 1G | 1G × 1 | 512M | 512M |
| **Standard** | 2G × 2 | 1G | 512M–1G | 1G | 1G × 2 | 512M | 512M |
| **High** | 2G × 3–4 | 2G+ (or managed DB) | 1G+ | 1G–2G | 1G × 3–4 | 512M | 512M |

If you raise replicas without raising host RAM, lower `GUNICORN_WORKERS` per replica to avoid OOM.

## PostgreSQL

| Tier | Notes |
|------|--------|
| **Light** | `shared_buffers` ~256–512MB; `max_connections` 100–150; nightly backups to `./backups`. |
| **Standard** | `shared_buffers` ~512MB–1GB; monitor connection count vs. `(WEB_REPLICAS × GUNICORN_WORKERS)`; consider PgBouncer if connections grow. |
| **High** | Prefer **managed PostgreSQL** or dedicated host; tune `work_mem`, `effective_cache_size`, autovacuum; separate disk I/O from app nodes. |

Connection demand grows with **Gunicorn workers × web replicas** plus **Celery concurrency × celery replicas** plus occasional management commands.

## Redis

Used for: Django cache, sessions (`django_redis`), Celery broker/result backend, and Channels layer if enabled (`REDIS_URL` / separate DB indexes in code).

| Tier | Notes |
|------|--------|
| **Light** | Default 512M limit often enough; watch memory if API cache keys grow. |
| **Standard** | 512M–1G; enable monitoring on evictions and hit rate. |
| **High** | 1G+ or dedicated Redis; consider separating **cache** vs **Celery broker** only if you hit contention (requires settings/URL split). |

Prod compose uses **AOF** (`--appendonly yes`) and **password** auth—plan disk for AOF growth.

## ClamAV

Virus scanning is CPU- and memory-sensitive during definition updates and concurrent scans.

| Tier | Notes |
|------|--------|
| **Light** | Single `clamav` container; stagger heavy upload tests. |
| **Standard** | Same; monitor scan latency and web timeouts (`GUNICORN_TIMEOUT`, Nginx `proxy_read_timeout`). |
| **High** | Ensure ClamAV has reserved RAM; consider async scan queues (already Celery-friendly for large files—see `documentation/virus_scanner_setup.md`). |

## Quick selection

- **First production cut:** **Standard** row for `.env.prod` scaling + **8 GB RAM** host minimum; move to **16 GB** if you run **2 web replicas** and **2 celery replicas** with defaults.
- **Cost-sensitive pilot:** **Light** row, single replica, off-peak backups, monitor disk and Celery queue depth.

## Scenario: coordination office (~500 applicants per semester)

Typical assumptions: **~500 applicants per semester**, **up to ~30 documents per applicant**, peak **~30 concurrent users**.

| Dimension | Implication |
|-----------|-------------|
| **Document volume** | 500 × 30 ≈ **15,000 documents per semester** — drives **storage**, **backup size**, and **ingestion/migration** effort more than peak CPU. |
| **Concurrency** | ~30 concurrent users sits in the **Light** tier for app scaling; size **disk and backups** first. |

**Recommended host (single node, Compose):**

| Resource | Suggestion |
|----------|------------|
| **vCPU** | **2–4** |
| **RAM** | **8 GB** minimum; **16 GB** if you want headroom for Postgres, ClamAV, and growth without immediate tuning. |
| **SSD** | **80 GB** minimum; **150 GB** safer. Plan: *(docs per semester × average file size)* + PostgreSQL + Redis AOF + logs + **room for local backup copies** (or rely on cloud object storage for backups and size disk smaller). |

**Suggested `.env.prod` scale knobs** (starting point; tune with metrics):

| Variable | Value |
|----------|--------|
| `WEB_REPLICAS` | `1` |
| `GUNICORN_WORKERS` | `3` |
| `CELERY_REPLICAS` | `1` |
| `CELERY_CONCURRENCY` | `4` |

Maps to the **Light** row in the tier and scaling tables above.

## Cloud deployment options

Patterns aligned with [docker-compose.prod.yml](../docker-compose.prod.yml) and [seim/settings/production.py](../seim/settings/production.py).

| Pattern | What runs in cloud | Tradeoffs |
|---------|-------------------|-----------|
| **A. Single VM (lift-and-shift)** | One EC2 / Azure VM / Compute Engine instance running Docker Compose (web, Nginx, Celery, optional ClamAV) | Lowest refactor; you patch OS, Docker, and images. |
| **B. Managed data plane** | **RDS** / **Cloud SQL** / **Azure Database for PostgreSQL** + **ElastiCache** / **Memorystore** / **Azure Cache for Redis**; app on VM or containers | Less DBA toil; set `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` consistently. |
| **C. Object storage for media** | **S3** / **GCS** / **Blob** via `django-storages` (see [env.prod.example](../env.prod.example)) | Better durability and off-server backups; requires correct Django storage and URL settings. |

**WebSockets:** Production Compose uses **Gunicorn (WSGI)**. Moving to the cloud does not change that: **Channels/WebSockets** still need an **ASGI** process and Nginx `Upgrade` headers if you rely on them in production.

## AWS: Pricing Calculator (authoritative estimates)

**Do not rely on ad-hoc dollar figures in this doc.** Build an estimate in the official **[AWS Pricing Calculator](https://calculator.aws/)**, export or save the estimate, and revisit when region or usage changes.

**Suggested line items (Bill of Materials) for a Light-tier SEIM deployment** — adjust region (e.g. `us-east-1`), instance families, and storage to match your scenario:

1. **Compute:** Amazon EC2 (e.g. **t3.large** or **m6i.large** for 8–16 GiB RAM) — On-Demand or Savings Plans as appropriate.
2. **Block storage:** Amazon EBS **gp3** attached to the instance (e.g. **150 GiB** for the coordination-office scenario).
3. **Optional split:** **Amazon RDS for PostgreSQL** (e.g. small burstable class + allocated storage) instead of Postgres in Compose on the same host.
4. **Redis:** Either **ElastiCache for Redis** (small node) *or* Redis in Docker on the same EC2 as today’s compose (no separate ElastiCache line).
5. **Object storage:** **Amazon S3** (Standard) for media and/or backup objects — include **GB-month**, **PUT/GET** request tiers, and lifecycle rules if using IA/Glacier for older semesters.
6. **Networking:** **Data transfer out** to internet (often underestimated); keep internal traffic in the same region/AZ where possible.
7. **Optional:** **[AWS Backup](https://aws.amazon.com/backup/pricing/)** for EC2/EBS/RDS snapshot policies.

**Reference pricing pages (detail; still use Calculator for totals):**

- [EC2 On-Demand pricing](https://aws.amazon.com/ec2/pricing/on-demand/)
- [RDS for PostgreSQL pricing](https://aws.amazon.com/rds/postgresql/pricing/)
- [Amazon S3 pricing](https://aws.amazon.com/s3/pricing/)

**Verification note:** Export a dated estimate from the calculator after configuration; treat third-party “calculator” sites as **illustrative only**.

## Google Cloud and Microsoft Azure (calculator-first)

Use each vendor’s official calculator; configure the **same logical BOM** as AWS (VM + managed Postgres optional + Redis optional + object storage + egress).

| Provider | Calculator | Typical products to add |
|----------|------------|-------------------------|
| **Google Cloud** | [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator) | Compute Engine VM, Cloud SQL (PostgreSQL), Memorystore (Redis), Cloud Storage, egress |
| **Microsoft Azure** | [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) | Linux VM, Azure Database for PostgreSQL Flexible Server, Azure Cache for Redis, Blob Storage, egress |

**Illustrative only (not a quote):** Small dev/test configurations on public pricing pages are often quoted in **single-digit to low tens of USD/month** for minimal instances; production HA, storage, backups, and egress dominate real bills. Always build your own estimate in the official calculator for your region and currency.

## Cloud backups and retention

| Area | Practice |
|------|----------|
| **PostgreSQL** | Use managed **automated backups** / PITR where available (RDS, Cloud SQL, Azure). Otherwise schedule **`pg_dump`** (or physical backup) to object storage with encryption at rest. |
| **Media** | Object storage **versioning**; **lifecycle** rules to transition old semester data to cheaper tiers if policy allows; consider **cross-region replication** for DR. |
| **Secrets / config** | Do not commit production secrets; use the cloud **secret manager** and document restore steps. |
| **Restore testing** | Run a **quarterly** restore drill (DB + sample media). Align operational steps with [documentation/deployment.md](../documentation/deployment.md) backup sections and `make prod-backup` where applicable. |

Define **RPO** (how much data you can lose) and **RTO** (how fast you must be back) with stakeholders; size backup frequency and multi-AZ choices accordingly.

## Legacy data migration

Phased approach for moving **old applications, documents, or spreadsheets** into SEIM:

1. **Discovery:** Inventory sources (files shares, legacy DB, Excel), document types, PII/consent rules, and ownership.
2. **Mapping:** Define how source entities map to SEIM models (users, programs, applications, documents).
3. **Extract / transform:** Prefer **Django management commands** or a one-off ETL in a **staging** environment; validate row counts and file checksums.
4. **Load:** Bulk insert DB rows; upload files to `media` or object storage with paths referenced in DB.
5. **Virus scan:** Run **ClamAV** (or your policy) on ingested files before marking them accepted (see [documentation/virus_scanner_setup.md](../documentation/virus_scanner_setup.md)).
6. **Cutover:** Short freeze window, final delta sync, DNS or load-balancer switch, smoke tests.
7. **Rollback plan:** Keep read-only snapshot of source until sign-off.

## On-premises (coordination office) with cloud backup / DR

For a **small coordination office** running the same **Light**-tier software footprint:

| Topic | Guidance |
|-------|----------|
| **Hardware** | Small tower, NUC, or short-depth **1U** with **≥8 GB RAM**, **≥150 GB SSD**, reliable network; **UPS** recommended. |
| **Network** | HTTPS in front of the app (Nginx or appliance); restrict admin paths; **VPN** for staff if needed. |
| **Backup / DR** | Nightly **encrypted** backups to **S3 / GCS / Azure Blob** (or vendor backup vault); **least privilege** IAM keys; test restore quarterly. Optional **one-way sync** of media to cloud for disaster recovery without running the app in cloud full-time. |
| **Cost model** | **Capex** for hardware and **power/cooling** vs **opex** for cloud VMs in the calculator sections above—often hybrid: on-prem app + cloud object storage for backups only. |

## Validation checklist

After deploy, confirm:

- `/health/` OK behind Nginx
- Celery workers processing tasks (`celery inspect active`)
- Beat schedules firing (`django_celery_beat` periodic tasks)
- DB connections within `max_connections`
- Redis memory stable; no unexpected evictions if you rely on cache durability
- ClamAV healthy (`clamdscan --ping` inside container)
- Backup job and restore drill (`make prod-backup` / restore procedure)

---

**Last updated:** 2026-04-16 (expanded: scenario, cloud, calculators, backups, migration, on-premises)
