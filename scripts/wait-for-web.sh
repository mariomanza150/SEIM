#!/bin/bash
# Wait for web service to be healthy and ready before running E2E tests

set -e

host="${1:-web}"
port="${2:-8000}"
timeout="${3:-120}"

echo "Waiting for $host:$port to be ready..."

start_time=$(date +%s)

until curl -s -f "http://$host:$port/health/" > /dev/null 2>&1 || curl -s -f "http://$host:$port/" > /dev/null 2>&1; do
  current_time=$(date +%s)
  elapsed=$((current_time - start_time))
  
  if [ $elapsed -gt $timeout ]; then
    echo "Timeout waiting for $host:$port after ${timeout}s"
    exit 1
  fi
  
  echo "Waiting for $host:$port... (${elapsed}s elapsed)"
  sleep 2
done

echo "$host:$port is ready! Waited ${elapsed}s"

