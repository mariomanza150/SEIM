# Rebuild and redeploy the seim-localprod Docker Compose stack (Windows / PowerShell).
#
# Usage:
#   .\scripts\deploy-local-prod.ps1
#   .\scripts\deploy-local-prod.ps1 -NoCache
#   .\scripts\deploy-local-prod.ps1 -SkipPull
#   .\scripts\deploy-local-prod.ps1 -SkipBuild   # restart only (same images)
#
# Machine-wide maintenance lock (scripts/maintenance-lock.ps1, %ProgramData%\ops\maintenance.lock; one-time setup:
# scripts/setup-maintenance-lock-dir.ps1). Taken before the build and held to the end (through the Created fallback
# and the final health check), renewed by a heartbeat every TTL/3, released in finally. It serializes deploys across
# repos on this machine and keeps Otto (the local-ai-stack outage watcher) from starting containers mid-deploy.
# Another holder: wait up to -LockWaitSec, then fail fast. If the job is killed, the heartbeat dies with it and the
# lock goes stale within -LockTtlSec (or at once: the holder pid is gone).
#
# Every docker step has a hard timeout, and all of them together stay inside -TotalBudgetSec (18 min, under the
# job's timeout-minutes: 20): build (-BuildTimeoutSec), then `up --no-build --wait` (-ComposeUpTimeoutSec). up has
# hung on this machine after recreating containers (created, never started). On that timeout the compose process
# tree is killed and only this project's containers still in Created state are started with `docker start`, data
# services first; then the health check decides the job.
#
param(
    [switch]$NoCache,
    [switch]$SkipPull,
    [switch]$SkipBuild,
    [int]$HealthTimeoutSec = 180,
    [int]$LockWaitSec = 180,
    [int]$LockTtlSec = 600,
    [int]$BuildTimeoutSec = 480,
    [int]$ComposeWaitTimeoutSec = 180,
    [int]$ComposeUpTimeoutSec = 240,
    [int]$StartTimeoutSec = 30,
    [int]$FallbackTimeoutSec = 120,
    [int]$TotalBudgetSec = 1080
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
# Fallback start order: data services first, the tunnel last; anything else in between.
$StartOrder = @("db", "redis", "toefl", "web", "celery", "celery-beat", "cloudflared")
$ScriptDeadline = (Get-Date).AddSeconds($TotalBudgetSec)

. (Join-Path $PSScriptRoot "maintenance-lock.ps1")

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Get-StepTimeout([int]$CapSec, [string]$Step) {
    # The step's cap, or what is left of the total budget if that is less.
    $left = [int][Math]::Floor(($ScriptDeadline - (Get-Date)).TotalSeconds)
    if ($left -lt 5) { throw "Deploy budget (${TotalBudgetSec}s) used up before $Step" }
    return [Math]::Min($CapSec, $left)
}

function Invoke-Bounded([string[]]$ArgList, [int]$TimeoutSec, [string]$What) {
    # Run `docker <ArgList>` with a hard timeout. Returns the exit code, or $null when it timed out (the process tree
    # is killed then).
    $proc = Start-Process -FilePath "docker" -ArgumentList $ArgList -NoNewWindow -PassThru
    $null = $proc.Handle  # keep the handle so ExitCode is available after exit (Windows PowerShell)
    if ($proc.WaitForExit($TimeoutSec * 1000)) {
        return $proc.ExitCode
    }
    Write-Host "$What did not finish in ${TimeoutSec}s; killing it (pid $($proc.Id) and children)" -ForegroundColor Red
    & taskkill /T /F /PID $proc.Id | Out-Host
    return $null
}

function Get-StartRank([string]$Service) {
    $i = [Array]::IndexOf($StartOrder, $Service)
    if ($i -lt 0) { return ($StartOrder.Count - 1) - 0.5 }  # unknown services: after the app, before the tunnel
    return $i
}

function Invoke-CreatedContainerStart([string]$Project, [int]$PerContainerSec, [int]$TotalSec) {
    # docker start only this compose project's containers that are still in Created state, in $StartOrder.
    # {{.Labels}} has no inner quotes (Windows PowerShell 5.1 mangles quotes in native arguments).
    $lines = @(& docker ps -a --filter "label=com.docker.compose.project=$Project" --filter "status=created" --format "{{.Names}}|{{.Labels}}")
    $found = foreach ($line in @($lines | Where-Object { $_ })) {
        $name, $labels = $line -split '\|', 2
        $service = if ($labels -match 'com\.docker\.compose\.service=([^,]+)') { $Matches[1] } else { "" }
        [pscustomobject]@{ Name = $name.Trim(); Service = $service; Rank = (Get-StartRank $service) }
    }
    $found = @($found | Sort-Object Rank, Name)
    if ($found.Count -eq 0) {
        Write-Host "No $Project containers in Created state."
        return
    }
    $until = (Get-Date).AddSeconds($TotalSec)
    foreach ($c in $found) {
        $left = [int][Math]::Floor(($until - (Get-Date)).TotalSeconds)
        if ($left -lt 1) {
            Write-Host "Fallback budget (${TotalSec}s) used up; not starting $($c.Name)" -ForegroundColor Red
            continue
        }
        Write-Host "docker start $($c.Name) ($($c.Service))"
        $code = Invoke-Bounded @("start", $c.Name) ([Math]::Min($PerContainerSec, $left)) "docker start $($c.Name)"
        if ($null -ne $code -and $code -ne 0) {
            Write-Host "docker start $($c.Name) failed (exit $code)" -ForegroundColor Red
        }
    }
}

function Assert-LockHeld($Heartbeat) {
    if ($Heartbeat.State.Lost) { throw "Lost the maintenance lock (it expired and was taken); stopping the deploy" }
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
    Enter-MaintenanceLock -Repo $LockRepo -RunId $LockRunId -TtlSeconds $LockTtlSec -WaitSeconds (Get-StepTimeout $LockWaitSec "the lock") | Out-Null
} catch {
    if (Test-MaintenanceLockBusyError $_) { throw "Another deploy holds this machine: $($_.Exception.Message)" }
    throw "Could not take the maintenance lock: $($_.Exception.Message)"
}

$heartbeat = $null
$recovered = $false
try {
    $heartbeat = Start-MaintenanceLockHeartbeat -Repo $LockRepo -RunId $LockRunId -TtlSeconds $LockTtlSec

    if (-not $SkipBuild) {
        $buildTimeout = Get-StepTimeout $BuildTimeoutSec "the build"
        Write-Step "Building production images (web, celery, celery-beat, toefl) (hard timeout ${buildTimeout}s)"
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
        $buildExit = Invoke-Bounded $buildArgs $buildTimeout "docker compose build"
        if ($null -eq $buildExit) { throw "docker compose build timed out after ${buildTimeout}s" }
        if ($buildExit -ne 0) { throw "docker compose build failed (exit $buildExit)" }
    }
    Assert-LockHeld $heartbeat

    # Include the named-tunnel profile when a token is configured; otherwise
    # --remove-orphans would tear down the running cloudflared container.
    $profileArgs = @()
    $tokenLine = Select-String -Path $EnvFile -Pattern '^\s*CLOUDFLARE_TUNNEL_TOKEN\s*=\s*\S+' -ErrorAction SilentlyContinue
    if ($tokenLine) {
        $profileArgs = @("--profile", "cloudflare")
    }

    $upTimeout = Get-StepTimeout $ComposeUpTimeoutSec "docker compose up"
    Write-Step "Starting / updating stack $($profileArgs -join ' ') (hard timeout ${upTimeout}s)"
    $upArgs = @("compose", "-p", $ProjectName, "-f", $ComposeFile, "--env-file", $EnvFile) + $profileArgs + @(
        "up", "-d", "--no-build", "--remove-orphans", "--wait", "--wait-timeout", "$ComposeWaitTimeoutSec")
    $upExit = Invoke-Bounded $upArgs $upTimeout "docker compose up"
    if ($null -eq $upExit) {
        # The hang seen on this machine: containers recreated but never started. Start what compose left in Created
        # (still holding the lock, so Otto stays off); the health check below decides the job.
        $recovered = $true
        Write-Step "Fallback: starting $ProjectName containers left in Created state ($($StartOrder -join ', '))"
        Invoke-CreatedContainerStart -Project $ProjectName -PerContainerSec $StartTimeoutSec -TotalSec (Get-StepTimeout $FallbackTimeoutSec "the fallback")
    } elseif ($upExit -ne 0) {
        throw "docker compose up failed (exit $upExit)"
    }
    Assert-LockHeld $heartbeat

    $healthTimeout = Get-StepTimeout $HealthTimeoutSec "the health check"
    Write-Step "Waiting for health check ($HealthUrl, up to ${healthTimeout}s)"
    $deadline = (Get-Date).AddSeconds($healthTimeout)
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
            Write-Verbose "health: $($_.Exception.Message)"
        }
        Start-Sleep -Seconds 5   # also after a non-200 answer
    }

    if (-not $healthy) {
        Write-Host ""
        Write-Host "Health check timed out after ${healthTimeout}s." -ForegroundColor Red
        Write-Host "Recent web logs:" -ForegroundColor Yellow
        $null = Invoke-Bounded @("compose", "-p", $ProjectName, "-f", $ComposeFile, "logs", "--tail", "40", "web") 30 "docker compose logs"
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
    Stop-MaintenanceLockHeartbeat $heartbeat
    Exit-MaintenanceLock -Repo $LockRepo -RunId $LockRunId | Out-Null
}

Write-Step "Deploy complete"
Write-Host "App: http://localhost:8020/seim/" -ForegroundColor Green
Write-Host "Health: $HealthUrl" -ForegroundColor Green
$null = Invoke-Bounded @("compose", "-p", $ProjectName, "-f", $ComposeFile, "ps") 30 "docker compose ps"
