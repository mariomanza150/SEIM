#!/usr/bin/env bash
# Rebuild and redeploy the seim-localprod Docker Compose stack (bash / WSL / self-hosted runner).
#
# Usage:
#   ./scripts/deploy-local-prod.sh
#   ./scripts/deploy-local-prod.sh --no-cache
#   ./scripts/deploy-local-prod.sh --skip-pull
#   ./scripts/deploy-local-prod.sh --skip-build
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

COMPOSE_FILE="docker-compose.local-prod.yml"
PROJECT_NAME="seim-localprod"
ENV_FILE=".env.local-prod"
HEALTH_URL="http://localhost:8020/health/live/"
HEALTH_TIMEOUT_SEC="${HEALTH_TIMEOUT_SEC:-180}"

NO_CACHE=0
SKIP_PULL=0
SKIP_BUILD=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-cache) NO_CACHE=1 ;;
        --skip-pull) SKIP_PULL=1 ;;
        --skip-build) SKIP_BUILD=1 ;;
        -h|--help)
            echo "Usage: $0 [--no-cache] [--skip-pull] [--skip-build]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
    shift
done

step() {
    echo ""
    echo "==> $1"
}

command -v docker >/dev/null 2>&1 || { echo "Docker CLI not found." >&2; exit 1; }

if [[ ! -f "$ENV_FILE" ]]; then
    echo "$ENV_FILE not found. Copy env.local-prod.example to .env.local-prod first." >&2
    exit 1
fi

if [[ "$SKIP_PULL" -eq 0 ]]; then
    step "Pulling latest git changes"
    git pull --ff-only
fi

if [[ "$SKIP_BUILD" -eq 0 ]]; then
    step "Building production images (web, celery, celery-beat)"
    BUILD_ARGS=(compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build)
    if [[ "$NO_CACHE" -eq 1 ]]; then
        BUILD_ARGS+=(--no-cache)
    fi
    BUILD_ARGS+=(web celery celery-beat)
    docker "${BUILD_ARGS[@]}"
fi

step "Starting / updating stack"
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --remove-orphans

step "Waiting for health check ($HEALTH_URL)"
deadline=$((SECONDS + HEALTH_TIMEOUT_SEC))
healthy=0
while (( SECONDS < deadline )); do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
        healthy=1
        break
    fi
    sleep 5
done

if [[ "$healthy" -ne 1 ]]; then
    echo "Health check timed out after ${HEALTH_TIMEOUT_SEC}s." >&2
    docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" logs --tail 40 web || true
    exit 1
fi

step "Deploy complete"
echo "App: http://localhost:8020/seim/"
echo "Health: $HEALTH_URL"
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" ps
