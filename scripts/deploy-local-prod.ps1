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
    [switch]$SkipMigrate,
    [switch]$SkipDbBackup,
    [switch]$SkipSmoke,
    [switch]$SkipRegistryPush,
    [int]$HealthTimeoutSec = 180,
    [int]$SmokeTimeoutSec = 240,
    [int]$RegistryTimeoutSec = 120,
    [int]$LockWaitSec = 180,
    [int]$LockTtlSec = 600,
    [int]$BuildTimeoutSec = 480,
    [int]$ComposeWaitTimeoutSec = 180,
    [int]$ComposeUpTimeoutSec = 240,
    [int]$MigrateTimeoutSec = 180,
    [int]$DbBackupTimeoutSec = 120,
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
$DbBackupDirRel = if ($env:SEIM_DB_BACKUP_DIR) { $env:SEIM_DB_BACKUP_DIR.Trim() } else { "backups/local-prod" }
$DbBackupKeep = 10
if ($env:SEIM_DB_BACKUP_KEEP -match '^\d+$') { $DbBackupKeep = [int]$env:SEIM_DB_BACKUP_KEEP }
$RegistryCompose = Join-Path $ProjectRoot "deploy/docker-compose.registry.yml"
$LocalRegistry = "127.0.0.1:5000"
$AppImage = ""
$ToeflImage = ""

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
    # Stop the deploy when the lock can no longer be trusted: lost, the heartbeat runspace ended
    # (Handle.IsCompleted), or no renewal within 2x the renew interval.
    $why = Test-MaintenanceLockHeartbeat $Heartbeat
    if ($why) { throw "Maintenance lock heartbeat failed ($why); stopping the deploy" }
}

function Get-EnvFileValue([string]$Path, [string]$Key, [string]$Default = "") {
    $line = Select-String -Path $Path -Pattern ("^\s*" + [regex]::Escape($Key) + "\s*=") -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $line) { return $Default }
    $raw = ($line.Line -split "=", 2)[1].Trim()
    if ($raw.StartsWith('"') -and $raw.EndsWith('"')) { $raw = $raw.Substring(1, $raw.Length - 2) }
    if ($raw.StartsWith("'") -and $raw.EndsWith("'")) { $raw = $raw.Substring(1, $raw.Length - 2) }
    if (-not $raw) { return $Default }
    return $raw
}

function Invoke-PreMigrateDbBackup([string]$Project, [string]$Compose, [string]$EnvPath, [int]$TimeoutSec) {
    # Custom-format dump from the running db container into SEIM_DB_BACKUP_DIR (host path).
    $dbPass = Get-EnvFileValue $EnvPath "DB_PASSWORD" "changeme123"
    $backupRoot = if ([System.IO.Path]::IsPathRooted($DbBackupDirRel)) { $DbBackupDirRel } else { Join-Path $ProjectRoot $DbBackupDirRel }
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $outFile = Join-Path $backupRoot ("seim_prod-" + $stamp + ".dump")
    Write-Host "pg_dump -> $outFile"
    $dumpArgs = @(
        "compose", "-p", $Project, "-f", $Compose, "--env-file", $EnvPath,
        "exec", "-T", "-e", "PGPASSWORD=$dbPass", "db",
        "pg_dump", "-U", "seimuser", "-d", "seim_prod", "-Fc"
    )
    $proc = Start-Process -FilePath "docker" -ArgumentList $dumpArgs -NoNewWindow -PassThru `
        -RedirectStandardOutput $outFile -RedirectStandardError (Join-Path $backupRoot "pg_dump.err")
    $null = $proc.Handle
    if (-not $proc.WaitForExit($TimeoutSec * 1000)) {
        Write-Host "pg_dump did not finish in ${TimeoutSec}s; killing it" -ForegroundColor Red
        & taskkill /T /F /PID $proc.Id | Out-Host
        throw "pg_dump timed out after ${TimeoutSec}s"
    }
    if ($proc.ExitCode -ne 0) {
        $err = if (Test-Path (Join-Path $backupRoot "pg_dump.err")) { Get-Content (Join-Path $backupRoot "pg_dump.err") -Raw } else { "" }
        throw "pg_dump failed (exit $($proc.ExitCode)): $err"
    }
    # Retention: keep newest N dumps.
    $dumps = @(Get-ChildItem -Path $backupRoot -Filter "seim_prod-*.dump" | Sort-Object LastWriteTime -Descending)
    if ($dumps.Count -gt $DbBackupKeep) {
        $dumps | Select-Object -Skip $DbBackupKeep | ForEach-Object { Remove-Item -Force $_.FullName }
    }
}

function Invoke-MigrateService([string]$Project, [string]$Compose, [string]$EnvPath, [int]$TimeoutSec) {
    # One-shot migrate profile (does not stay running). Requires db healthy.
    $args = @(
        "compose", "-p", $Project, "-f", $Compose, "--env-file", $EnvPath,
        "--profile", "migrate",
        "run", "--rm", "migrate"
    )
    $code = Invoke-Bounded $args $TimeoutSec "docker compose run migrate"
    if ($null -eq $code) { throw "docker compose run migrate timed out after ${TimeoutSec}s" }
    if ($code -ne 0) { throw "docker compose run migrate failed (exit $code)" }
}

function Ensure-LocalRegistry([int]$TimeoutSec) {
    if (-not (Test-Path $RegistryCompose)) {
        throw "Missing $RegistryCompose — local registry compose file required"
    }
    Write-Host "Ensuring local registry at $LocalRegistry (loopback only)"
    $upArgs = @(
        "compose", "-f", $RegistryCompose, "--env-file", $EnvFile,
        "up", "-d", "--wait", "--wait-timeout", "60"
    )
    $code = Invoke-Bounded $upArgs $TimeoutSec "docker compose up registry"
    if ($null -eq $code) { throw "local registry up timed out after ${TimeoutSec}s" }
    if ($code -ne 0) { throw "local registry up failed (exit $code)" }
}

function Publish-ImageTags([string]$AppImage, [string]$ToeflImage, [switch]$AlsoLastGood) {
    $targets = @($AppImage, $ToeflImage)
    if ($AlsoLastGood) {
        $targets += @(($AppImage -replace ':[^:]+$', ':last-good'), ($ToeflImage -replace ':[^:]+$', ':last-good'))
    }
    foreach ($t in $targets) {
        Write-Host "docker push $t"
        $code = Invoke-Bounded @("push", $t) 120 "docker push $t"
        if ($null -eq $code) { throw "docker push $t timed out" }
        if ($code -ne 0) { throw "docker push $t failed (exit $code)" }
    }
}

function Set-LastGoodTags([string]$AppImage, [string]$ToeflImage) {
    $appGood = ($AppImage -replace ':[^:]+$', ':last-good')
    $toeflGood = ($ToeflImage -replace ':[^:]+$', ':last-good')
    foreach ($pair in @(@($AppImage, $appGood), @($ToeflImage, $toeflGood))) {
        Write-Host "docker tag $($pair[0]) -> $($pair[1])"
        $code = Invoke-Bounded @("tag", $pair[0], $pair[1]) 30 "docker tag $($pair[1])"
        if ($null -eq $code -or $code -ne 0) { throw "docker tag $($pair[1]) failed" }
    }
    if (-not $SkipRegistryPush) {
        Publish-ImageTags -AppImage $appGood -ToeflImage $toeflGood
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

if ($env:LOCAL_REGISTRY) {
    $LocalRegistry = $env:LOCAL_REGISTRY.Trim()
} else {
    $fromEnv = Get-EnvFileValue $EnvFile "LOCAL_REGISTRY" ""
    if ($fromEnv) { $LocalRegistry = $fromEnv }
}
$env:LOCAL_REGISTRY = $LocalRegistry
if (-not $env:LOCAL_REGISTRY_PORT) {
    $portPart = ($LocalRegistry -split ":", 2)[-1]
    if ($portPart -match '^\d+$') { $env:LOCAL_REGISTRY_PORT = $portPart }
}

if (-not $SkipPull) {
    Write-Step "Pulling latest git changes"
    git pull --ff-only
}

# Stamp the build with the deployed commit (tester version badge / settings.BUILD_COMMIT, and the
# GlitchTip release unless SENTRY_RELEASE is set). It is a build arg baked into the image, so
# -SkipBuild reuses the running images and keeps their release.
# SEIM_IMAGE_TAG may be pre-set (tests / pinned rollback); otherwise use git HEAD.
if (-not $env:SEIM_IMAGE_TAG) {
    try {
        $env:GIT_COMMIT = (git rev-parse HEAD).Trim()
    } catch {
        $env:GIT_COMMIT = ""
    }
    if (-not $env:GIT_COMMIT) { throw "Could not resolve git HEAD for SEIM_IMAGE_TAG" }
    $env:SEIM_IMAGE_TAG = $env:GIT_COMMIT
} else {
    if (-not $env:GIT_COMMIT) { $env:GIT_COMMIT = $env:SEIM_IMAGE_TAG }
}
$AppImage = "$LocalRegistry/seim-app:$($env:SEIM_IMAGE_TAG)"
$ToeflImage = "$LocalRegistry/seim-toefl:$($env:SEIM_IMAGE_TAG)"

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

    Ensure-LocalRegistry -TimeoutSec (Get-StepTimeout $RegistryTimeoutSec "local registry")
    Assert-LockHeld $heartbeat

    if (-not $SkipBuild) {
        $buildTimeout = Get-StepTimeout $BuildTimeoutSec "the build"
        Write-Step "Building images tagged $AppImage (and toefl) (hard timeout ${buildTimeout}s)"
        $buildArgs = @(
            "compose", "-p", $ProjectName,
            "-f", $ComposeFile,
            "--env-file", $EnvFile,
            "build"
        )
        if ($NoCache) {
            $buildArgs += "--no-cache"
        }
        # Build tags as image: LOCAL_REGISTRY/seim-app:SEIM_IMAGE_TAG (and seim-toefl).
        $buildArgs += @("web", "celery", "celery-beat", "toefl")
        $buildExit = Invoke-Bounded $buildArgs $buildTimeout "docker compose build"
        if ($null -eq $buildExit) { throw "docker compose build timed out after ${buildTimeout}s" }
        if ($buildExit -ne 0) { throw "docker compose build failed (exit $buildExit)" }

        if (-not $SkipSmoke) {
            $smokeTimeout = Get-StepTimeout $SmokeTimeoutSec "image smoke test"
            Write-Step "Smoke-testing $AppImage (empty Postgres → migrate → check --deploy → /health/live/)"
            $smokeScript = Join-Path $PSScriptRoot "smoke-local-prod-image.ps1"
            $smokeProc = Start-Process -FilePath "pwsh" -ArgumentList @(
                "-NoProfile", "-File", $smokeScript, "-Image", $AppImage, "-TimeoutSec", "$smokeTimeout"
            ) -NoNewWindow -PassThru
            $null = $smokeProc.Handle
            if (-not $smokeProc.WaitForExit(($smokeTimeout + 30) * 1000)) {
                & taskkill /T /F /PID $smokeProc.Id | Out-Host
                throw "smoke test timed out after ${smokeTimeout}s"
            }
            if ($smokeProc.ExitCode -ne 0) { throw "smoke test failed (exit $($smokeProc.ExitCode))" }
        }

        if (-not $SkipRegistryPush) {
            Write-Step "Pushing SHA tags to local registry $LocalRegistry"
            Publish-ImageTags -AppImage $AppImage -ToeflImage $ToeflImage
        }
    } else {
        Write-Step "SkipBuild: using existing tag $AppImage"
        if (-not $SkipRegistryPush) {
            # Prefer the exact SHA from the local registry when rebuilding was skipped.
            $null = Invoke-Bounded @("pull", $AppImage) 120 "docker pull $AppImage"
            $null = Invoke-Bounded @("pull", $ToeflImage) 120 "docker pull $ToeflImage"
        }
    }
    Assert-LockHeld $heartbeat

    # Data plane first so pg_dump / migrate can talk to a healthy Postgres before app rollout.
    $dataUpTimeout = Get-StepTimeout $ComposeWaitTimeoutSec "db/redis up"
    Write-Step "Ensuring db and redis are up (hard timeout ${dataUpTimeout}s)"
    $dataUpArgs = @(
        "compose", "-p", $ProjectName, "-f", $ComposeFile, "--env-file", $EnvFile,
        "up", "-d", "--no-build", "--wait", "--wait-timeout", "$ComposeWaitTimeoutSec", "db", "redis")
    $dataUpExit = Invoke-Bounded $dataUpArgs $dataUpTimeout "docker compose up db redis"
    if ($null -eq $dataUpExit) { throw "docker compose up db redis timed out after ${dataUpTimeout}s" }
    if ($dataUpExit -ne 0) { throw "docker compose up db redis failed (exit $dataUpExit)" }
    Assert-LockHeld $heartbeat

    if (-not $SkipDbBackup) {
        $backupTimeout = Get-StepTimeout $DbBackupTimeoutSec "pg_dump"
        Write-Step "Pre-migrate database backup (pg_dump, hard timeout ${backupTimeout}s)"
        Invoke-PreMigrateDbBackup -Project $ProjectName -Compose $ComposeFile -EnvPath $EnvFile -TimeoutSec $backupTimeout
        Assert-LockHeld $heartbeat
    }

    if (-not $SkipMigrate) {
        $migrateTimeout = Get-StepTimeout $MigrateTimeoutSec "migrate"
        Write-Step "Applying migrations (one-shot migrate service, hard timeout ${migrateTimeout}s)"
        Invoke-MigrateService -Project $ProjectName -Compose $ComposeFile -EnvPath $EnvFile -TimeoutSec $migrateTimeout
        Assert-LockHeld $heartbeat
    }

    # Include the named-tunnel profile when a token is configured; otherwise
    # --remove-orphans would tear down the running cloudflared container.
    $profileArgs = @()
    $tokenLine = Select-String -Path $EnvFile -Pattern '^\s*CLOUDFLARE_TUNNEL_TOKEN\s*=\s*\S+' -ErrorAction SilentlyContinue
    if ($tokenLine) {
        $profileArgs += @("--profile", "cloudflare")
    }
    $autohealLine = Select-String -Path $EnvFile -Pattern '^\s*SEIM_AUTOHEAL\s*=\s*(1|true|yes)\s*$' -ErrorAction SilentlyContinue
    if ($autohealLine -or ($env:SEIM_AUTOHEAL -match '^(1|true|yes)$')) {
        $profileArgs += @("--profile", "autoheal")
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

    Write-Step "Promoting $AppImage to last-good (local registry)"
    Set-LastGoodTags -AppImage $AppImage -ToeflImage $ToeflImage
} finally {
    Stop-MaintenanceLockHeartbeat $heartbeat
    Exit-MaintenanceLock -Repo $LockRepo -RunId $LockRunId | Out-Null
}

Write-Step "Deploy complete"
Write-Host "App: http://localhost:8020/seim/" -ForegroundColor Green
Write-Host "Health: $HealthUrl" -ForegroundColor Green
Write-Host "Image: $AppImage (last-good updated)" -ForegroundColor Green
$null = Invoke-Bounded @("compose", "-p", $ProjectName, "-f", $ComposeFile, "ps") 30 "docker compose ps"
