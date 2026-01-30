# PowerShell script to run video demo tests
# Run video demo tests and generate walkthrough videos

Write-Host "🎬 Starting Video Demo Generation" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Ensure videos directory exists
$videosDir = "tests/e2e_playwright/videos"
if (-not (Test-Path $videosDir)) {
    New-Item -ItemType Directory -Path $videosDir -Force | Out-Null
}

Write-Host ""
Write-Host "📹 Running video demo tests..." -ForegroundColor Yellow

# Run video demo tests
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest `
    tests/e2e_playwright/test_video_demos.py `
    -v `
    --browser=chromium `
    --base-url=http://web:8000 `
    -m video_demo `
    --tb=short

Write-Host ""
Write-Host "✅ Video demos complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Videos saved to: $videosDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Generated videos:" -ForegroundColor Cyan
Get-ChildItem -Path $videosDir -Filter "*.webm" -ErrorAction SilentlyContinue | 
    ForEach-Object { Write-Host "  - $($_.Name) ($([math]::Round($_.Length / 1MB, 2)) MB)" }

