# SEIM AWS Deployment Guide

Deploy SEIM (Student Exchange Information Manager) on AWS for university workloads: roughly **120 applicants/year**, **~10 staff**, low continuous traffic with occasional spikes of **~30 concurrent users**. Traffic for Saltillo and Monterrey, Mexico is served from **`us-east-1`** with **Cloudflare** at the edge.

**ClamAV is omitted from all base AWS profiles** to avoid ~1.2–1.5 GB of idle resident RAM. Virus scanning stays optional (`docker compose --profile clamav` on Minimum only).

## Table of Contents

- [Deployment tiers](#deployment-tiers)
- [Region, latency, and cost](#region-latency-and-cost)
- [Media uploads (S3)](#media-uploads-s3)
- [Security (Cloudflare + security groups)](#security-cloudflare--security-groups)
- [Ultra-Lean (default) — `docker-compose.lean.yml`](#ultra-lean-default--docker-composeleanyml)
- [Minimum — `docker-compose.prod.yml`](#minimum--docker-composeprodyml)
- [Recommended (split tier)](#recommended-split-tier)
- [Database backups to S3](#database-backups-to-s3)
- [Environment templates](#environment-templates)
- [Monitoring and operations](#monitoring-and-operations)
- [Troubleshooting](#troubleshooting)

---

## Deployment tiers

| Tier | Monthly Est. | Sizing / Hardware | Architecture & Key Decisions |
| :--- | :--- | :--- | :--- |
| **Ultra-Lean (Default)** | **~$15 / mo** | 1× EC2 `t4g.small` (2 vCPU, 2 GB ARM) + 30 GB gp3 | Single-node Docker Compose (`docker-compose.lean.yml`). ClamAV omitted. Cloudflare Free proxy for SSL/CDN (cached at Monterrey PoP). Daily S3 database backup cron. |
| **Minimum** | **~$65 / mo** | 1× EC2 `t4g.medium` (2 vCPU, 4 GB) + 40 GB gp3 | Single-host production Compose (`docker-compose.prod.yml`) with **separated** Celery worker and beat containers, basic CloudWatch alarms, Elastic IP. ClamAV omitted by default. |
| **Recommended (Split Tier)** | **~$180–$220 / mo** | 1× EC2 `t4g.medium` + RDS `db.t4g.small` + ElastiCache Redis | Split data tier for automated backups and failover. App on EC2; managed PostgreSQL (RDS); managed Redis (ElastiCache); S3 + CloudFront (or Cloudflare) for static/CDN. |

**Workload fit:** Ultra-Lean is the default for this application size. Move to Minimum when you need Elastic IP, separated Celery processes, and CloudWatch headroom. Move to Recommended when you want managed DB backups, Multi-AZ options, and less operational risk.

Compose / env mapping:

| Tier | Compose file | Env template | Runtime env file |
| :--- | :--- | :--- | :--- |
| Ultra-Lean | `docker-compose.lean.yml` | `env.lean.example` | `.env.lean` |
| Minimum | `docker-compose.prod.yml` | `env.prod.example` | `.env.prod` (+ `secrets/`) |
| Recommended | App still from `docker-compose.prod.yml` (omit local `db`/`redis` or point URLs at managed endpoints) | `env.prod.example` | `.env.prod` with RDS + ElastiCache URLs |

---

## Region, latency, and cost

**Use `us-east-1` (N. Virginia), not a Mexico-local AWS region.**

| Option | Approx. latency to Saltillo / Monterrey | Cost / availability notes |
| :--- | :--- | :--- |
| **`us-east-1` + Cloudflare Free** | ~40–50 ms via Monterrey PoP (HTML/static cached; origin for API/dynamic) | Lowest EC2/RDS/S3 prices; mature service catalog; Cloudflare Free terminates TLS and caches at the edge |
| Mexico City (`mx-central-1`) / other LatAm | Lower raw RTT to origin in some cases | Higher instance pricing, smaller footprint; still need edge CDN for global assets |

**Why this pairing wins for SEIM**

1. **Cost:** `t4g` ARM and gp3 in `us-east-1` keep Ultra-Lean near **~$15/mo** (compute + disk + modest S3).
2. **Latency:** Browser users hit Cloudflare’s Monterrey (or nearest) PoP; cached static assets and SPA shells respond locally. Origin round-trips for authenticated API calls remain acceptable for staff workflows.
3. **S3:** Same-region buckets for private documents avoid cross-region transfer fees from the EC2 host.

Point your DNS (proxied orange-cloud) at the EC2 public IP or Elastic IP. Prefer **Full (strict)** SSL between Cloudflare and origin when you terminate TLS on Nginx; **Flexible** only for early bring-up.

---

## Media uploads (S3)

Student documents are **private** objects in S3 (`AWS_DEFAULT_ACL=private`, bucket block-public-access on).

**Deployment rule for all three tiers:** keep media off the EC2 root volume.

1. Set `USE_S3=true`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME=us-east-1`, and credentials (or prefer an **EC2 instance role** with `s3:GetObject` / `PutObject` on the media bucket).
2. Prefer **presigned URL** upload/download so browsers stream **directly to/from S3**. That keeps EC2 RAM and egress free during multi-megabyte PDF uploads.
3. Nginx continues to serve **collected static files** from the `static_*` volume; do not proxy large private media through Gunicorn when S3 is enabled.
4. On Recommended, optionally put a CloudFront distribution in front of public static assets; keep student documents private (presigned or signed cookies)—never world-readable.

Backup bucket (`AWS_BACKUP_BUCKET`) is **separate** from the media bucket and must stay private.

---

## Security (Cloudflare + security groups)

### Security group (EC2)

| Direction | Port | Source | Purpose |
| :--- | :--- | :--- | :--- |
| Inbound | 80, 443 | **Cloudflare IP ranges only** | HTTP/HTTPS to Nginx (see [Cloudflare IP ranges](https://www.cloudflare.com/ips/)) |
| Inbound | 22 | **Administrator IPs only** | SSH (never `0.0.0.0/0`) |
| Outbound | * | Restrict as needed | S3, SES/SMTP, OS updates, Cloudflare |

Do **not** expose PostgreSQL (5432) or Redis (6379) on the public interface. On Ultra-Lean / Minimum they stay on the Docker bridge network only.

### Application

- `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` must list your real hostname(s).
- Set `USE_TLS_PROXY_HEADERS=1` so Django trusts `X-Forwarded-Proto` from Cloudflare.
- Rotate `SECRET_KEY`, DB, and Redis passwords; store Minimum/Recommended secrets under `secrets/` with mode `600`.

---

## Ultra-Lean (default) — `docker-compose.lean.yml`

**Hardware:** EC2 `t4g.small` (ARM, 2 GB) + 30 GB gp3 in `us-east-1`.

**Services:** `web` (Gunicorn, 2 workers), `celery` (**combined** worker + beat, `--concurrency=2`), `postgres` (Alpine, tuned for ~512 MB), `redis` (Alpine, `--maxmemory 128mb --maxmemory-policy allkeys-lru`), `nginx`.

**Memory budget (approx.):** Postgres 512 MB · Web 512 MB · Celery 384 MB · Redis 160 MB · Nginx 128 MB · OS/Docker headroom ~300 MB.

### Quick start

```bash
# On the EC2 host (Amazon Linux 2023 / Ubuntu ARM64)
git clone <repository-url> /opt/seim
cd /opt/seim

cp env.lean.example .env.lean
# Edit: SECRET_KEY, passwords, ALLOWED_HOSTS, AWS_*, email

mkdir -p backups nginx/ssl
docker compose -f docker-compose.lean.yml --env-file .env.lean up -d --build

docker compose -f docker-compose.lean.yml exec web python manage.py createsuperuser
docker compose -f docker-compose.lean.yml exec web python manage.py create_initial_data
```

Or via Make (Linux/macOS shell on the host):

```bash
make lean-setup lean-deploy
make lean-status
make lean-logs
```

### Health check

```bash
curl -fsS https://your-domain.com/health/
docker compose -f docker-compose.lean.yml ps
docker stats --no-stream
```

---

## Minimum — `docker-compose.prod.yml`

**Hardware:** EC2 `t4g.medium` (4 GB) + 40 GB gp3, Elastic IP, basic CloudWatch (CPU, status check, disk).

**Services:** Separated `web`, `celery` worker, `celery-beat`, on-host `db`, `redis`, `nginx`. Optional Fluentd. **ClamAV not started** unless `--profile clamav`.

### Quick start

```bash
cp env.prod.example .env.prod
make prod-setup
make prod-secrets
# Fill secrets/aws_*.txt, email secrets, and .env.prod (WEB_REPLICAS=1, CELERY_REPLICAS=1)

make deploy-prod
make prod-health
```

Tune `.env.prod` for a single 4 GB host: `WEB_REPLICAS=1`, `GUNICORN_WORKERS=3`, `CELERY_REPLICAS=1`, `CELERY_CONCURRENCY=2`.

Optional ClamAV (adds ~1.2–1.5 GB RAM — only if the host has spare memory):

```bash
# In .env.prod: VIRUS_SCANNER_TYPE=clamav
docker compose -f docker-compose.prod.yml --profile clamav up -d
```

---

## Recommended (split tier)

**Hardware / services**

| Component | Service |
| :--- | :--- |
| App + Nginx + Celery | EC2 `t4g.medium` running Compose **without** local Postgres/Redis data plane (or stop those services) |
| Database | RDS PostgreSQL `db.t4g.small` (automated backups, optional Multi-AZ) |
| Cache / broker | ElastiCache Redis (same VPC) |
| Media | S3 (private) + CloudFront or Cloudflare for public static |
| Backups | RDS automated snapshots; retain S3 dumps only if you want portable copies |

### Configuration sketch

In `.env.prod` (and/or secrets):

```bash
DATABASE_URL=postgresql://seimuser:PASSWORD@your-rds.xxxxx.us-east-1.rds.amazonaws.com:5432/seim
REDIS_URL=redis://:PASSWORD@your-elasticache.xxxxx.cache.amazonaws.com:6379/0
CELERY_BROKER_URL=redis://:PASSWORD@your-elasticache.xxxxx.cache.amazonaws.com:6379/0
CELERY_RESULT_BACKEND=redis://:PASSWORD@your-elasticache.xxxxx.cache.amazonaws.com:6379/0
USE_S3=true
AWS_STORAGE_BUCKET_NAME=your-media-bucket
AWS_S3_REGION_NAME=us-east-1
```

Place EC2, RDS, and ElastiCache in private subnets where possible; expose only Nginx via Cloudflare. Security groups: EC2 → RDS:5432, EC2 → ElastiCache:6379; no public DB/Redis.

Monthly cost lands roughly **$180–$220** depending on Multi-AZ, snapshot retention, and data transfer.

---

## Database backups to S3

For **Ultra-Lean** and **Minimum** (Postgres in Docker), use `scripts/backup_db_s3.sh`:

1. `pg_dump -Fc` via `docker exec`
2. Upload to `s3://<AWS_BACKUP_BUCKET>/db_backups/`
3. Delete objects older than **30 days** (override with `BACKUP_RETENTION_DAYS`)

### One-time setup on the EC2 host

```bash
# IAM user or instance role: s3:PutObject, s3:GetObject, s3:ListBucket, s3:DeleteObject
# on arn:aws:s3:::your-seim-backup-bucket/db_backups/*

chmod +x /opt/seim/scripts/backup_db_s3.sh
# Ensure AWS CLI v2 is installed and credentials/role work:
aws s3 ls s3://your-seim-backup-bucket/db_backups/
```

Set in `.env.lean` or `.env.prod`:

```bash
AWS_BACKUP_BUCKET=your-seim-backup-bucket
AWS_S3_REGION_NAME=us-east-1
# Ultra-Lean defaults (script defaults match lean):
# COMPOSE_FILE=docker-compose.lean.yml
# POSTGRES_CONTAINER=seim-postgres-lean
# Minimum:
# COMPOSE_FILE=docker-compose.prod.yml
# POSTGRES_CONTAINER=seim-db-prod
```

### Crontab

```bash
sudo crontab -e
```

```cron
# Daily 02:00 UTC — Ultra-Lean
0 2 * * * /opt/seim/scripts/backup_db_s3.sh >> /var/log/seim-db-backup.log 2>&1
```

Manual run:

```bash
/opt/seim/scripts/backup_db_s3.sh
# Skip retention pass once:
SKIP_RETENTION=1 /opt/seim/scripts/backup_db_s3.sh
```

**Restore (custom format):**

```bash
aws s3 cp s3://your-seim-backup-bucket/db_backups/seim_YYYYMMDDTHHMMSSZ.dump ./restore.dump
docker exec -i seim-postgres-lean pg_restore -U seimuser -d seim --clean --if-exists < restore.dump
```

On **Recommended**, prefer RDS automated backups / PITR; keep the script only if you need portable dumps.

---

## Environment templates

| File | Purpose |
| :--- | :--- |
| `env.example` | Local / Docker Compose development |
| `env.lean.example` | Ultra-Lean AWS (→ `.env.lean`) |
| `env.prod.example` | Minimum / Recommended AWS (→ `.env.prod`) |

Shared production variables across lean and prod templates:

- `USE_S3`, `AWS_*`, `AWS_BACKUP_BUCKET`, `AWS_S3_REGION_NAME=us-east-1`
- `VIRUS_SCANNER_TYPE=mock` (ClamAV not in base profiles)
- `USE_TLS_PROXY_HEADERS=1` for Cloudflare

---

## Monitoring and operations

| Tier | What to enable |
| :--- | :--- |
| Ultra-Lean | Cloudflare analytics; `docker stats`; free-tier CloudWatch basic metrics if desired |
| Minimum | CloudWatch alarms: CPU > 80%, status check failed, disk > 80%; Elastic IP; `make prod-logs` |
| Recommended | RDS Performance Insights / free metrics; ElastiCache evictions; ALB/CloudFront or Cloudflare analytics |

Useful Make targets:

```bash
# Ultra-Lean
make lean-status lean-logs lean-health lean-stop

# Minimum
make prod-status prod-logs prod-health prod-backup prod-stop
```

---

## Troubleshooting

### OOM / containers restarting (Ultra-Lean)

```bash
docker stats --no-stream
# Keep GUNICORN_WORKERS=2 and CELERY_CONCURRENCY=2; do not enable ClamAV on 2 GB hosts.
```

### Static files 404

```bash
docker compose -f docker-compose.lean.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.lean.yml restart nginx
```

### Database connection refused

Confirm service name: lean uses hostname **`postgres`**; prod uses **`db`**. `DATABASE_URL` must match.

### Cloudflare 522 / 525

Origin security group must allow Cloudflare IPs on 80/443; origin Nginx must be up (`docker compose … ps`).

---

## Production checklist

- [ ] Chose tier (Ultra-Lean default for this workload)
- [ ] EC2 in `us-east-1`, gp3 sized per tier
- [ ] Security group: Cloudflare-only HTTP/S; SSH locked to admin IPs
- [ ] DNS orange-clouded to instance / Elastic IP
- [ ] `.env.lean` or `.env.prod` (+ secrets) filled; S3 media + backup buckets private
- [ ] ClamAV left disabled unless intentionally profiled in on a larger host
- [ ] `scripts/backup_db_s3.sh` crontab installed (Ultra-Lean / Minimum)
- [ ] Superuser + `create_initial_data` completed
- [ ] `/health/` returns OK through Cloudflare

## Additional resources

- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Cloudflare IP ranges](https://www.cloudflare.com/ips/)
- [Environment variables](environment_variables.md)
- [Virus scanner (optional)](virus_scanner_setup.md)
- [Production sizing notes](notes/production-target-matrix.md)

---

**Note:** Dollar estimates assume on-demand `t4g` in `us-east-1`, modest S3, and Cloudflare Free. Spot, Savings Plans, and Multi-AZ RDS change the monthly total.
