# Rebuild and redeploy the seim-localprod Docker Compose stack (Windows / PowerShell).
#
# Usage:
#   .\scripts\deploy-local-prod.ps1
#   .\scripts\deploy-local-prod.ps1 -NoCache
#   .\scripts\deploy-local-prod.ps1 -SkipPull
#   .\scripts\deploy-local-prod.ps1 -SkipBuild   # restart only (same images)
#
param(
    [switch]$NoCache,
    [switch]$SkipPull,
    [switch]$SkipBuild,
    [int]$HealthTimeoutSec = 180
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$ComposeFile = "docker-compose.local-prod.yml"
$ProjectName = "seim-localprod"
$EnvFile = ".env.local-prod"
$HealthUrl = "http://localhost:8020/health/live/"

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI not found. Start Docker Desktop and retry."
}

if (-not (Test-Path $EnvFile)) {
    throw @"
$EnvFile not found.
Copy env.local-prod.example to .env.local-prod and configure secrets first.
"@
}

if (-not $SkipPull) {
    Write-Step "Pulling latest git changes"
    git pull --ff-only
}

if (-not $SkipBuild) {
    Write-Step "Building production images (web, celery, celery-beat)"
    $buildArgs = @(
        "compose", "-p", $ProjectName,
        "-f", $ComposeFile,
        "--env-file", $EnvFile,
        "build"
    )
    if ($NoCache) {
        $buildArgs += "--no-cache"
    }
    $buildArgs += @("web", "celery", "celery-beat")
    & docker @buildArgs
    if ($LASTEXITCODE -ne 0) { throw "docker compose build failed (exit $LASTEXITCODE)" }
}

Write-Step "Starting / updating stack"
& docker compose -p $ProjectName -f $ComposeFile --env-file $EnvFile up -d --remove-orphans
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed (exit $LASTEXITCODE)" }

Write-Step "Waiting for health check ($HealthUrl)"
$deadline = (Get-Date).AddSeconds($HealthTimeoutSec)
$healthy = $false
while ((Get-Date) -lt $deadline) {
    try {
        $response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 5
    }
}

if (-not $healthy) {
    Write-Host ""
    Write-Host "Health check timed out after ${HealthTimeoutSec}s." -ForegroundColor Red
    Write-Host "Recent web logs:" -ForegroundColor Yellow
    & docker compose -p $ProjectName -f $ComposeFile logs --tail 40 web
    throw "Deploy finished but app is not healthy at $HealthUrl"
}

Write-Step "Deploy complete"
Write-Host "App: http://localhost:8020/seim/" -ForegroundColor Green
Write-Host "Health: $HealthUrl" -ForegroundColor Green
& docker compose -p $ProjectName -f $ComposeFile ps
