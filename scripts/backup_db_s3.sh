#!/usr/bin/env bash
# Daily PostgreSQL dump → private S3 backup bucket (Ultra-Lean / Minimum single-host).
#
# Prerequisites: docker, aws CLI v2, IAM permissions for s3:PutObject / ListBucket / DeleteObject
# on the backup bucket.
#
# Crontab (see docs/deployment.md):
#   0 2 * * * /opt/seim/scripts/backup_db_s3.sh >> /var/log/seim-db-backup.log 2>&1
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# Load env if present (secrets stay on host; do not commit .env.lean / .env.prod)
if [[ -f "${REPO_ROOT}/.env.lean" ]]; then
  # shellcheck disable=SC1091
  set -a
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/.env.lean"
  set +a
elif [[ -f "${REPO_ROOT}/.env.prod" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/.env.prod"
  set +a
fi

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.lean.yml}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-seim-postgres-lean}"
POSTGRES_USER="${POSTGRES_USER:-seimuser}"
POSTGRES_DB="${POSTGRES_DB:-seim}"
AWS_S3_REGION_NAME="${AWS_S3_REGION_NAME:-us-east-1}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
AWS_BACKUP_BUCKET="${AWS_BACKUP_BUCKET:?Set AWS_BACKUP_BUCKET (S3 bucket for db dumps)}"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP_DIR="$(mktemp -d)"
DUMP_FILE="${TMP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.dump"
S3_PREFIX="s3://${AWS_BACKUP_BUCKET}/db_backups"
S3_URI="${S3_PREFIX}/${POSTGRES_DB}_${TIMESTAMP}.dump"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting DB backup → ${S3_URI}"

if ! docker ps --format '{{.Names}}' | grep -qx "${POSTGRES_CONTAINER}"; then
  echo "ERROR: Postgres container '${POSTGRES_CONTAINER}' is not running." >&2
  exit 1
fi

docker exec "${POSTGRES_CONTAINER}" \
  pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc \
  > "${DUMP_FILE}"

DUMP_SIZE="$(wc -c < "${DUMP_FILE}" | tr -d ' ')"
if [[ "${DUMP_SIZE}" -lt 100 ]]; then
  echo "ERROR: Dump looks empty (${DUMP_SIZE} bytes)." >&2
  exit 1
fi

aws s3 cp "${DUMP_FILE}" "${S3_URI}" \
  --region "${AWS_S3_REGION_NAME}" \
  --only-show-errors

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Uploaded ${DUMP_SIZE} bytes to ${S3_URI}"

# 30-day retention: delete objects older than BACKUP_RETENTION_DAYS under db_backups/
if [[ "${SKIP_RETENTION:-0}" != "1" ]]; then
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Applying ${BACKUP_RETENTION_DAYS}-day retention under ${S3_PREFIX}/"
  CUTOFF_EPOCH="$(date -u -d "${BACKUP_RETENTION_DAYS} days ago" +%s 2>/dev/null || date -u -v-"${BACKUP_RETENTION_DAYS}"d +%s)"
  aws s3 ls "${S3_PREFIX}/" --region "${AWS_S3_REGION_NAME}" | while read -r line; do
    # Format: 2026-08-23 02:00:01    12345 seim_20260823T020001Z.dump
    obj_date="$(echo "${line}" | awk '{print $1}')"
    obj_time="$(echo "${line}" | awk '{print $2}')"
    obj_name="$(echo "${line}" | awk '{print $4}')"
    [[ -z "${obj_name}" ]] && continue
    obj_epoch="$(date -u -d "${obj_date} ${obj_time}" +%s 2>/dev/null || date -u -j -f "%Y-%m-%d %H:%M:%S" "${obj_date} ${obj_time}" +%s 2>/dev/null || echo 0)"
    if [[ "${obj_epoch}" -gt 0 && "${obj_epoch}" -lt "${CUTOFF_EPOCH}" ]]; then
      echo "  Deleting expired: ${obj_name}"
      aws s3 rm "${S3_PREFIX}/${obj_name}" --region "${AWS_S3_REGION_NAME}" --only-show-errors
    fi
  done
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Backup finished OK"
