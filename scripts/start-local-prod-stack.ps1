# Wait for Docker, then ensure seim-localprod compose stack is up.
param(
    [int]$DockerTimeoutSec = 300,
    [int]$HealthTimeoutSec = 180
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker-compose.local-prod.yml"
$EnvFile = Join-Path $ProjectRoot ".env.local-prod"
$ProjectName = "seim-localprod"
$HealthUrl = "http://localhost:8020/health/live/"

function Write-Step([string]$Message) {
    Write-Host "==> $Message"
}

if (-not (Test-Path $EnvFile)) {
    throw ".env.local-prod not found at $EnvFile"
}

Write-Step "Waiting for Docker (up to ${DockerTimeoutSec}s)"
$dockerReady = $false
$deadline = (Get-Date).AddSeconds($DockerTimeoutSec)
while ((Get-Date) -lt $deadline) {
    try {
        docker info *> $null
        if ($LASTEXITCODE -eq 0) {
            $dockerReady = $true
            break
        }
    }
    catch {
        # Docker CLI not ready yet
    }
    Start-Sleep -Seconds 5
}
if (-not $dockerReady) {
    throw "Docker did not become ready within ${DockerTimeoutSec}s"
}

Set-Location $ProjectRoot
Write-Step "Starting seim-localprod stack"
docker compose -p $ProjectName -f $ComposeFile --env-file $EnvFile up -d --remove-orphans
if ($LASTEXITCODE -ne 0) {
    throw "docker compose up failed (exit $LASTEXITCODE)"
}

Write-Step "Waiting for health check ($HealthUrl)"
$healthy = $false
$healthDeadline = (Get-Date).AddSeconds($HealthTimeoutSec)
while ((Get-Date) -lt $healthDeadline) {
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
    docker compose -p $ProjectName -f $ComposeFile logs --tail 40 web
    throw "Stack started but health check failed at $HealthUrl"
}

Write-Step "seim-localprod is up at http://localhost:8020/seim/"
