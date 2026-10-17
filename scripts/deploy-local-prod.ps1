# Rebuild and redeploy the seim-localprod Docker Compose stack (Windows / PowerShell).
#
# Usage:
#   .\scripts\deploy-local-prod.ps1
#   .\scripts\deploy-local-prod.ps1 -NoCache
#   .\scripts\deploy-local-prod.ps1 -SkipPull
#   .\scripts\deploy-local-prod.ps1 -SkipBuild   # restart only (same images)
#
# Machine-wide maintenance lock (scripts/maintenance-lock.ps1, %ProgramData%\ops\maintenance.lock): taken before
# the build, released in a finally block. It serializes deploys across repos on this machine and keeps Otto (the
# local-ai-stack outage watcher) from starting containers mid-deploy. Another holder: wait up to -LockWaitSec, then
# fail fast. The TTL (default 20 min) matches the job timeout-minutes, so a killed job cannot block the machine longer.
#
# `docker compose up` runs with --no-build --wait under a hard -ComposeUpTimeoutSec. It has hung on this machine
# after recreating containers (created, never started). On that timeout the compose process tree is killed, the
# lock released, and only this project's containers still in Created state are started with `docker start`; then
# the health check decides the job.
#
param(
    [switch]$NoCache,
    [switch]$SkipPull,
    [switch]$SkipBuild,
    [int]$HealthTimeoutSec = 180,
    [int]$LockWaitSec = 300,
    [int]$LockTtlSec = 1200,
    [int]$ComposeWaitTimeoutSec = 180,
    [int]$ComposeUpTimeoutSec = 240,
    [int]$StartTimeoutSec = 60
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$ComposeFile = "docker-compose.local-prod.yml"
$ProjectName = "seim-localprod"
$EnvFile = ".env.local-prod"
$HealthUrl = "http://localhost:8020/health/live/"
$FinalHealthUrl = "http://localhost:8020/health/"
$LockRepo = "SEIM"
$LockRunId = if ($env:GITHUB_RUN_ID) { "gh-$($env:GITHUB_RUN_ID)-$($env:GITHUB_RUN_ATTEMPT)" } else { "manual-$PID-$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())" }

. (Join-Path $PSScriptRoot "maintenance-lock.ps1")

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-ComposeUp([string[]]$UpArgs, [int]$TimeoutSec) {
    # Run `docker <UpArgs>` with a hard timeout. Returns the exit code, or $null when it timed out (the process tree
    # is killed then).
    $proc = Start-Process -FilePath "docker" -ArgumentList $UpArgs -NoNewWindow -PassThru
    $null = $proc.Handle  # keep the handle so ExitCode is available after exit (Windows PowerShell)
    if ($proc.WaitForExit($TimeoutSec * 1000)) {
        return $proc.ExitCode
    }
    Write-Host "docker compose up did not finish in ${TimeoutSec}s; killing it (pid $($proc.Id) and children)" -ForegroundColor Red
    & taskkill /T /F /PID $proc.Id | Out-Host
    return $null
}

function Invoke-CreatedContainerStart([string]$Project, [int]$TimeoutSec) {
    # docker start only this compose project's containers that are still in Created state.
    $names = @(& docker ps -a --filter "label=com.docker.compose.project=$Project" --filter "status=created" --format "{{.Names}}")
    $names = @($names | Where-Object { $_ })
    if ($names.Count -eq 0) {
        Write-Host "No $Project containers in Created state."
        return
    }
    foreach ($name in $names) {
        Write-Host "docker start $name"
        $p = Start-Process -FilePath "docker" -ArgumentList @("start", $name) -NoNewWindow -PassThru
        $null = $p.Handle
        if (-not $p.WaitForExit($TimeoutSec * 1000)) {
            & taskkill /T /F /PID $p.Id | Out-Host
            Write-Host "docker start $name did not finish in ${TimeoutSec}s" -ForegroundColor Red
        } elseif ($p.ExitCode -ne 0) {
            Write-Host "docker start $name failed (exit $($p.ExitCode))" -ForegroundColor Red
        }
    }
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

# Stamp the build with the deployed commit (tester version badge / settings.BUILD_COMMIT, and the
# GlitchTip release unless SENTRY_RELEASE is set). It is a build arg baked into the image, so
# -SkipBuild reuses the running images and keeps their release.
try {
    $env:GIT_COMMIT = (git rev-parse HEAD).Trim()
} catch {
    $env:GIT_COMMIT = ""
}

Write-Step "Taking the maintenance lock ($LockRepo run $LockRunId, wait up to ${LockWaitSec}s)"
try {
    Enter-MaintenanceLock -Repo $LockRepo -RunId $LockRunId -TtlSeconds $LockTtlSec -WaitSeconds $LockWaitSec | Out-Null
} catch {
    throw "Another deploy holds this machine: $($_.Exception.Message)"
}

$recovered = $false
try {
    if (-not $SkipBuild) {
        Write-Step "Building production images (web, celery, celery-beat, toefl)"
        $buildArgs = @(
            "compose", "-p", $ProjectName,
            "-f", $ComposeFile,
            "--env-file", $EnvFile,
            "build"
        )
        if ($NoCache) {
            $buildArgs += "--no-cache"
        }
        # Build toefl too so its tag always matches the deployed commit and `up` recreates it.
        $buildArgs += @("web", "celery", "celery-beat", "toefl")
        & docker @buildArgs
        if ($LASTEXITCODE -ne 0) { throw "docker compose build failed (exit $LASTEXITCODE)" }
    }

    # Include the named-tunnel profile when a token is configured; otherwise
    # --remove-orphans would tear down the running cloudflared container.
    $profileArgs = @()
    $tokenLine = Select-String -Path $EnvFile -Pattern '^\s*CLOUDFLARE_TUNNEL_TOKEN\s*=\s*\S+' -ErrorAction SilentlyContinue
    if ($tokenLine) {
        $profileArgs = @("--profile", "cloudflare")
    }

    Write-Step "Starting / updating stack $($profileArgs -join ' ') (hard timeout ${ComposeUpTimeoutSec}s)"
    $upArgs = @("compose", "-p", $ProjectName, "-f", $ComposeFile, "--env-file", $EnvFile) + $profileArgs + @(
        "up", "-d", "--no-build", "--remove-orphans", "--wait", "--wait-timeout", "$ComposeWaitTimeoutSec")
    $upExit = Invoke-ComposeUp -UpArgs $upArgs -TimeoutSec $ComposeUpTimeoutSec
    if ($null -eq $upExit) {
        # The hang seen on this machine: containers recreated but never started. Free the machine first, then start
        # what compose left in Created; the health check below decides the job.
        $recovered = $true
        Exit-MaintenanceLock -RunId $LockRunId | Out-Null
        Write-Step "Fallback: starting $ProjectName containers left in Created state"
        Invoke-CreatedContainerStart -Project $ProjectName -TimeoutSec $StartTimeoutSec
    } elseif ($upExit -ne 0) {
        throw "docker compose up failed (exit $upExit)"
    }

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

    $finalStatus = 0
    try {
        $finalStatus = (Invoke-WebRequest -Uri $FinalHealthUrl -UseBasicParsing -TimeoutSec 10).StatusCode
    } catch {
        $finalStatus = 0
    }
    if ($finalStatus -ne 200) {
        throw "Deploy finished but $FinalHealthUrl returned $finalStatus, not 200"
    }
    if ($recovered) {
        Write-Host "::warning::docker compose up hung and was killed; the stack was started by the fallback and is healthy."
    }
} finally {
    Exit-MaintenanceLock -RunId $LockRunId | Out-Null
}

Write-Step "Deploy complete"
Write-Host "App: http://localhost:8020/seim/" -ForegroundColor Green
Write-Host "Health: $HealthUrl" -ForegroundColor Green
& docker compose -p $ProjectName -f $ComposeFile ps
