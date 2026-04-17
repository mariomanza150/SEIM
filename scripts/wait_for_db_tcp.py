#!/usr/bin/env python3
"""Wait until Postgres hostname resolves and accepts TCP (Docker Compose DNS + readiness)."""
from __future__ import annotations

import os
import socket
import sys
import time

host = os.environ.get("PGHOST", "db")
port = int(os.environ.get("PGPORT", "5432"))

# 1) Resolve hostname (embedded Compose DNS).
for i in range(45):
    try:
        socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        break
    except OSError:
        if i == 44:
            print(
                f'ERROR: Cannot resolve hostname "{host}".\n'
                "Run the web container on the same Docker Compose network as the Postgres service.\n"
                "Example: docker compose -f docker-compose.local-prod.yml --env-file .env.local-prod up -d",
                file=sys.stderr,
            )
            sys.exit(1)
        time.sleep(1)

# 2) Wait for Postgres to accept connections (IPv4/IPv6 via create_connection).
for _ in range(90):
    try:
        socket.create_connection((host, port), timeout=2).close()
        break
    except OSError:
        time.sleep(1)
else:
    print(f"ERROR: {host}:{port} did not accept connections in time.", file=sys.stderr)
    sys.exit(1)

print("Database is reachable.")
