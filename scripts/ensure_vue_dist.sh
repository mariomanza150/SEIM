#!/usr/bin/env bash
# Seed frontend-vue/dist when docker-compose uses a bind mount on /app (empty dist on host)
# and a named volume on dist that initialized empty. Baked assets live at /opt/seim-vue-dist.
set -euo pipefail
DIST="/app/frontend-vue/dist"
STASH="/opt/seim-vue-dist"
if [[ -f "${DIST}/index.html" ]]; then
  exit 0
fi
if [[ ! -f "${STASH}/index.html" ]]; then
  echo "ensure_vue_dist: no stash at ${STASH}/index.html (rebuild web image with frontend stage)" >&2
  exit 0
fi
mkdir -p "${DIST}"
cp -a "${STASH}/." "${DIST}/"
echo "ensure_vue_dist: populated ${DIST} from image stash"
