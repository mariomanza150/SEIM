#!/bin/bash
# Run video demo tests and generate walkthrough videos

set -e

echo "🎬 Starting Video Demo Generation"
echo "=================================="

# Ensure videos directory exists
mkdir -p tests/e2e_playwright/videos

# Run video demo tests
echo ""
echo "📹 Running video demo tests..."
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest \
    tests/e2e_playwright/test_video_demos.py \
    -v \
    --browser=chromium \
    --base-url=http://web:8000 \
    -m video_demo \
    --tb=short

echo ""
echo "✅ Video demos complete!"
echo ""
echo "📁 Videos saved to: tests/e2e_playwright/videos/"
echo ""
echo "📋 Generated videos:"
ls -lh tests/e2e_playwright/videos/*.webm 2>/dev/null || echo "No videos found"

