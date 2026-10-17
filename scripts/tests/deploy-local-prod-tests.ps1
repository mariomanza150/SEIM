<#
  Tests for scripts/deploy-local-prod.ps1 against a fake `docker` and `taskkill` and a local /health/ server
  (python3 -m http.server on :8020). Linux/macOS pwsh only (CI); no real docker, nothing is deployed.
    pwsh -NoProfile -File scripts/tests/deploy-local-prod-tests.ps1
#>
param([string]$Only = "")
$ErrorActionPreference = "Stop"
if (-not ($IsLinux -or $IsMacOS)) { Write-Output "skipped: needs Linux/macOS pwsh (fake docker is a shell script)"; exit 0 }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$pwshExe = (Get-Process -Id $PID).Path
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("seim-deploy-" + [Guid]::NewGuid().ToString("N"))
$sandbox = Join-Path $root "repo"
$bin = Join-Path $root "bin"
$www = Join-Path $root "www"
$calls = Join-Path $root "calls.log"
New-Item -ItemType Directory -Force -Path (Join-Path $sandbox "scripts"), $bin, $www | Out-Null
Copy-Item (Join-Path $repoRoot "scripts/deploy-local-prod.ps1"), (Join-Path $repoRoot "scripts/maintenance-lock.ps1") (Join-Path $sandbox "scripts")
Set-Content -Path (Join-Path $sandbox ".env.local-prod") -Value "CLOUDFLARE_TUNNEL_TOKEN=test-not-a-token"
Set-Content -Path (Join-Path $sandbox "docker-compose.local-prod.yml") -Value "services: {}"

$fakeDocker = @'
#!/bin/bash
L="$FAKE_CALLS"
lock() { [ -e "$MAINTENANCE_LOCK" ] && echo held || echo free; }
echo "docker $* [lock=$(lock)]" >> "$L"
case "$*" in
  *" build "*)
    end=$(( $(date +%s) + ${FAKE_BUILD_SLEEP:-0} ))
    while [ "$(date +%s)" -lt "$end" ]; do
      [ -n "$FAKE_GUARD_DURING_BUILD" ] && echo someone > "$MAINTENANCE_LOCK.takeover"
      sleep 0.3
    done
    rm -f "$MAINTENANCE_LOCK.takeover"
    exit 0;;
  *" up "*) [ "$FAKE_UP" = hang ] && exec sleep 600; exit ${FAKE_UP_EXIT:-0};;
  "ps -a "*)
    [ "$FAKE_UP" = hang ] && printf '%s\n' \
      "seim-web-local-prod|com.docker.compose.project=seim-localprod,com.docker.compose.service=web" \
      "seim-cloudflared-local-prod|com.docker.compose.service=cloudflared,com.docker.compose.project=seim-localprod" \
      "seim-redis-local-prod|com.docker.compose.project=seim-localprod,com.docker.compose.service=redis" \
      "seim-db-local-prod|com.docker.compose.project=seim-localprod,com.docker.compose.service=db"
    exit 0;;
  *) exit 0;;
esac
'@
$fakeTaskkill = @'
#!/bin/bash
pid="${@: -1}"; echo "taskkill $pid" >> "$FAKE_CALLS"; pkill -9 -P "$pid"; kill -9 "$pid"; echo "SUCCESS: killed $pid"
'@
[System.IO.File]::WriteAllText((Join-Path $bin "docker"), $fakeDocker.Replace("`r", ""))
[System.IO.File]::WriteAllText((Join-Path $bin "taskkill"), $fakeTaskkill.Replace("`r", ""))
& chmod +x (Join-Path $bin "docker") (Join-Path $bin "taskkill")

function Set-Healthy([bool]$Ok) {
    # http.server answers 200 with a listing for a directory without index.html: remove the directory for a 404.
    $health = Join-Path $www "health"
    if ($Ok) {
        New-Item -ItemType Directory -Force -Path (Join-Path $health "live") | Out-Null
        Set-Content -Path (Join-Path $health "index.html") -Value "ok"
        Set-Content -Path (Join-Path $health "live/index.html") -Value "ok"
    } elseif (Test-Path $health) { Remove-Item -Recurse -Force $health }
}
Set-Healthy $true
$server = Start-Process -FilePath "python3" -ArgumentList @("-m", "http.server", "8020", "--bind", "127.0.0.1", "--directory", $www) -PassThru -RedirectStandardError (Join-Path $root "http.err") -RedirectStandardOutput (Join-Path $root "http.out")
Start-Sleep -Seconds 1

$script:failures = 0
$script:passed = 0
function Assert([bool]$Cond, [string]$Message) { if (-not $Cond) { throw "assertion failed: $Message" } }

function Invoke-Deploy([hashtable]$Env, [string[]]$DeployArgs) {
    $lock = Join-Path $root ("lock-" + [Guid]::NewGuid().ToString("N") + "/maintenance.lock")
    $vars = @{ PATH = "$bin$([IO.Path]::PathSeparator)$env:PATH"; MAINTENANCE_LOCK = $lock; FAKE_CALLS = $calls;
               GITHUB_RUN_ID = "111"; GITHUB_RUN_ATTEMPT = "1" } + $Env
    $saved = @{}
    foreach ($k in $vars.Keys) { $saved[$k] = [Environment]::GetEnvironmentVariable($k); [Environment]::SetEnvironmentVariable($k, [string]$vars[$k]) }
    if (Test-Path $calls) { Remove-Item $calls }
    try {
        if ($Env.ContainsKey("PRELOCK")) {
            New-Item -ItemType Directory -Force -Path (Split-Path $lock) | Out-Null
            Set-Content -Path $lock -Value $Env.PRELOCK -NoNewline
        }
        $out = & $pwshExe -NoProfile -File (Join-Path $sandbox "scripts/deploy-local-prod.ps1") -SkipPull -HealthTimeoutSec 6 -ComposeUpTimeoutSec 3 -LockWaitSec 2 -StartTimeoutSec 5 @DeployArgs 2>&1 | Out-String
        $code = $LASTEXITCODE
    } finally {
        foreach ($k in $saved.Keys) { [Environment]::SetEnvironmentVariable($k, $saved[$k]) }
    }
    $log = if (Test-Path $calls) { @(Get-Content $calls) } else { @() }
    return [pscustomobject]@{ Code = $code; Out = $out; Calls = $log; LockLeft = (Test-Path $lock); Lock = $lock }
}

function Test-Case([string]$Name, [scriptblock]$Body) {
    if ($Only -and $Name -notmatch $Only) { return }
    try { & $Body; $script:passed++; Write-Output "ok   $Name" }
    catch { $script:failures++; Write-Output "FAIL $Name : $($_.Exception.Message)" }
}

try {
    Test-Case "a normal deploy: lock, build, up --no-build --wait, health, release" {
        $r = Invoke-Deploy @{} @()
        Assert ($r.Code -eq 0) "exit $($r.Code): $($r.Out)"
        Assert ($r.Calls[0] -match "build web celery celery-beat toefl \[lock=held\]") "build under the lock: $($r.Calls[0])"
        Assert ($r.Calls[1] -match "up -d --no-build --remove-orphans --wait --wait-timeout 180 \[lock=held\]") "up: $($r.Calls[1])"
        Assert (-not $r.LockLeft) "released"
    }

    Test-Case "up hangs: compose killed, Created containers started db/redis first under the lock, job passes with a warning" {
        $r = Invoke-Deploy @{ FAKE_UP = "hang" } @()
        Assert ($r.Code -eq 0) "exit $($r.Code): $($r.Out)"
        Assert (@($r.Calls | Where-Object { $_ -match '^taskkill ' }).Count -eq 1) "compose killed"
        $starts = @($r.Calls | Where-Object { $_ -match '^docker start ' })
        Assert ($starts.Count -eq 4) "starts: $($starts -join ' | ')"
        Assert ($starts[0] -match "seim-db-local-prod" -and $starts[1] -match "seim-redis-local-prod" -and $starts[3] -match "cloudflared") "order: $($starts -join ' | ')"
        Assert (@($starts | Where-Object { $_ -notmatch '\[lock=held\]' }).Count -eq 0) "lock held through the fallback"
        Assert ($r.Out -match "::warning::docker compose up hung") "warning"
        Assert (-not $r.LockLeft) "released"
    }

    Test-Case "heartbeat renewals stop during the build: Assert-LockHeld fails the deploy before up" {
        $r = Invoke-Deploy @{ FAKE_BUILD_SLEEP = "5"; FAKE_GUARD_DURING_BUILD = "1" } @("-LockTtlSec", "3")
        Assert ($r.Code -ne 0) "should fail: $($r.Out)"
        Assert ($r.Out -match "heartbeat failed \(no renewal for") "reason: $($r.Out)"
        Assert (@($r.Calls | Where-Object { $_ -match ' up ' }).Count -eq 0) "up never ran"
        Assert (-not $r.LockLeft) "released"
    }

    Test-Case "a healthy heartbeat keeps a 3 s TTL lock through a 5 s build" {
        $r = Invoke-Deploy @{ FAKE_BUILD_SLEEP = "5" } @("-LockTtlSec", "3")
        Assert ($r.Code -eq 0) "exit $($r.Code): $($r.Out)"
    }

    Test-Case "another holder: fails fast, its lock untouched" {
        $future = [DateTimeOffset]::UtcNow.AddMinutes(10).ToString("o", [Globalization.CultureInfo]::InvariantCulture)
        $other = '{"repo": "local-ai-stack/x", "run_id": "other", "pid": 1, "host": "elsewhere", "started_at": "' + $future + '", "expires_at": "' + $future + '"}'
        $r = Invoke-Deploy @{ PRELOCK = $other } @()
        Assert ($r.Code -ne 0) "should fail"
        Assert ($r.Out -match "Another deploy holds this machine") "message: $($r.Out)"
        Assert ($r.Calls.Count -eq 0) "no docker calls"
        Assert ((Get-Content $r.Lock -Raw) -eq $other) "untouched"
    }

    Test-Case "a build that outlives its timeout is killed and fails the job" {
        $r = Invoke-Deploy @{ FAKE_BUILD_SLEEP = "30" } @("-BuildTimeoutSec", "2")
        Assert ($r.Code -ne 0 -and $r.Out -match "build timed out after 2s") "out: $($r.Out)"
        Assert (-not $r.LockLeft) "released"
    }

    Test-Case "unhealthy: fails after the health window" {
        Set-Healthy $false
        try {
            $r = Invoke-Deploy @{} @()
            Assert ($r.Code -ne 0 -and $r.Out -match "not healthy") "out: $($r.Out)"
            Assert (-not $r.LockLeft) "released"
        } finally { Set-Healthy $true }
    }
} finally {
    Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $root -ErrorAction SilentlyContinue
}
Write-Output "$($script:passed) passed, $($script:failures) failed"
exit [int]($script:failures -gt 0)
