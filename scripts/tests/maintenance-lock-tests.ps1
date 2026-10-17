<#
  Tests for scripts/maintenance-lock.ps1 (the machine-wide maintenance lock), run under pwsh in CI:
    pwsh -NoProfile -File loops/checks/maintenance-lock-tests.ps1 [-LockScript path] [-PythonModule path/to/maintenance.py]
  No docker. -PythonModule adds the cross-language checks (a Python taker and a PowerShell taker on one lock).
  The same file lives in SEIM (scripts/tests/maintenance-lock-tests.ps1); keep them identical.
#>
param(
    [string]$LockScript = "",
    [string]$PythonModule = "",
    [string]$Only = ""   # run only the tests whose name matches this regex
)
$ErrorActionPreference = "Stop"
if (-not $LockScript) {
    $LockScript = @("scripts/maintenance-lock.ps1", "../../scripts/maintenance-lock.ps1") |
        ForEach-Object { Join-Path (Get-Location) $_ } | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $LockScript) { $LockScript = Join-Path $PSScriptRoot "../../scripts/maintenance-lock.ps1" }
}
$LockScript = (Resolve-Path $LockScript).Path
. $LockScript
$pwshExe = (Get-Process -Id $PID).Path
$script:failures = 0
$script:passed = 0

function Assert([bool]$Cond, [string]$Message) {
    if (-not $Cond) { throw "assertion failed: $Message" }
}

function New-TestLock {
    $dir = Join-Path ([System.IO.Path]::GetTempPath()) ("mlock-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $dir | Out-Null
    $env:MAINTENANCE_LOCK = Join-Path (Join-Path $dir "ops") "maintenance.lock"
    return $env:MAINTENANCE_LOCK
}

function Write-TestLock([string]$Path, [string]$Text) {
    $d = Split-Path -Parent $Path
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
    [System.IO.File]::WriteAllText($Path, $Text)
}

function Get-StaleJson([string]$RunId = "dead", [string]$LockHost = "") {
    $past = [DateTimeOffset]::UtcNow.AddMinutes(-5).ToString("o", [Globalization.CultureInfo]::InvariantCulture)
    return ('{{"repo": "old", "run_id": "{0}", "pid": 1, "host": "{1}", "started_at": "{2}", "expires_at": "{2}"}}' -f $RunId, $LockHost, $past)
}

function Invoke-Cli([string[]]$CliArgs) {
    & $pwshExe -NoProfile -File $LockScript @CliArgs 2>&1 | Out-Null
    return $LASTEXITCODE
}

function Test-Case([string]$Name, [scriptblock]$Body) {
    if ($Only -and $Name -notmatch $Only) { return }
    $saved = $env:MAINTENANCE_LOCK
    try {
        & $Body
        $script:passed++
        Write-Output "ok   $Name"
    } catch {
        $script:failures++
        Write-Output "FAIL $Name : $($_.Exception.Message) ($($_.InvocationInfo.ScriptLineNumber))"
    } finally {
        $env:MAINTENANCE_LOCK = $saved
    }
}

Test-Case "the lock file holds the record, with 'o' timestamps" {
    $p = New-TestLock
    $rec = Enter-MaintenanceLock -Repo SEIM -RunId 42 -TtlSeconds 600 6>$null
    $obj = [System.IO.File]::ReadAllText($p) | ConvertFrom-Json
    Assert ($obj.repo -eq "SEIM" -and $obj.run_id -eq "42" -and $obj.pid -eq $PID -and $obj.host -eq (Get-MaintenanceLockHost)) "fields"
    Assert ($rec.expires_at -match '^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{7}\+00:00$') "o format: $($rec.expires_at)"
    $l = Get-MaintenanceLock
    Assert ($l.RunId -eq "42") "held"
    Assert (Exit-MaintenanceLock -Repo SEIM -RunId 42 6>$null) "released"
    Assert (-not (Test-Path $p)) "file gone"
    Assert ((Get-ChildItem (Split-Path $p) -Filter *.tmp).Count -eq 0) "no temp files left"
}

Test-Case "busy: a second taker fails fast with exit 3; bad arguments exit 2" {
    $p = New-TestLock
    Enter-MaintenanceLock -Repo SEIM -RunId 1 6>$null | Out-Null
    $t0 = [DateTime]::UtcNow
    $code = Invoke-Cli @("-Action", "Acquire", "-Repo", "Cataloqui", "-RunId", "2", "-WaitSeconds", "1")
    Assert ($code -eq 3) "exit $code"
    Assert (([DateTime]::UtcNow - $t0).TotalSeconds -lt 15) "bounded"
    Assert ((Invoke-Cli @("-Action", "Acquire", "-Repo", "SEIM")) -eq 2) "usage"
    try { Enter-MaintenanceLock -Repo Cataloqui -RunId 2 | Out-Null; Assert $false "no throw" }
    catch { Assert (Test-MaintenanceLockBusyError $_) "busy error" }
    Exit-MaintenanceLock -Repo SEIM -RunId 1 6>$null | Out-Null
}

Test-Case "other errors are not busy: exit 4" {
    $dir = Join-Path ([System.IO.Path]::GetTempPath()) ("mlock-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $dir | Out-Null
    $file = Join-Path $dir "a-file"
    [System.IO.File]::WriteAllText($file, "x")
    $env:MAINTENANCE_LOCK = Join-Path (Join-Path $file "ops") "maintenance.lock"   # its parent is a file
    $code = Invoke-Cli @("-Action", "Acquire", "-Repo", "SEIM", "-RunId", "1", "-WaitSeconds", "1")
    Assert ($code -eq 4) "exit $code"
}

Test-Case "only the owner releases it, and the repo must match" {
    $p = New-TestLock
    Enter-MaintenanceLock -Repo SEIM -RunId 1 6>$null | Out-Null
    Assert (-not (Exit-MaintenanceLock -Repo SEIM -RunId 2 3>$null)) "other run"
    Assert (-not (Exit-MaintenanceLock -Repo Cataloqui -RunId 1 3>$null)) "other repo"
    Assert (Test-Path $p) "still there"
    Assert (Exit-MaintenanceLock -Repo SEIM -RunId 1 6>$null) "owner"
}

Test-Case "a stale lock is ignored, replaced, and not released by a non-owner" {
    $p = New-TestLock
    Write-TestLock $p (Get-StaleJson)
    Assert ($null -eq (Get-MaintenanceLock 3>$null)) "ignored"
    Assert (-not (Exit-MaintenanceLock -Repo Cataloqui -RunId x 3>$null)) "not released by others"
    Enter-MaintenanceLock -Repo Cataloqui -RunId new 3>$null 6>$null | Out-Null
    Assert ((Get-MaintenanceLock).RunId -eq "new") "replaced"
}

Test-Case "an unreadable lock counts as held, stale after 30 s" {
    $p = New-TestLock
    Write-TestLock $p "not json"
    $l = Get-MaintenanceLock
    Assert ($null -ne $l -and $l.Unreadable) "held"
    try { Enter-MaintenanceLock -Repo SEIM -RunId 1 -WaitSeconds 0 | Out-Null; Assert $false "taken" }
    catch { Assert (Test-MaintenanceLockBusyError $_) "busy: $($_.Exception.Message)" }
    [System.IO.File]::SetLastWriteTimeUtc($p, [DateTime]::UtcNow.AddSeconds(-31))
    Assert ($null -eq (Get-MaintenanceLock 3>$null)) "stale"
    Enter-MaintenanceLock -Repo SEIM -RunId 1 3>$null 6>$null | Out-Null
    Assert ((Get-MaintenanceLock).RunId -eq "1") "taken"
}

Test-Case "an orphaned lock on this host is stale, not one from another host" {
    $p = New-TestLock
    $dead = Start-Process -FilePath $pwshExe -ArgumentList @("-NoProfile", "-Command", "exit 0") -PassThru
    $dead.WaitForExit()
    $future = [DateTimeOffset]::UtcNow.AddHours(1).ToString("o", [Globalization.CultureInfo]::InvariantCulture)
    Write-TestLock $p ('{{"repo": "SEIM", "run_id": "1", "pid": {0}, "host": "elsewhere", "started_at": "{1}", "expires_at": "{1}"}}' -f $dead.Id, $future)
    Assert ($null -ne (Get-MaintenanceLock)) "other host: held"
    Write-TestLock $p ('{{"repo": "SEIM", "run_id": "1", "pid": {0}, "host": "{1}", "started_at": "{2}", "expires_at": "{2}"}}' -f $dead.Id, (Get-MaintenanceLockHost).ToUpper(), $future)
    Assert ($null -eq (Get-MaintenanceLock 3>$null)) "orphan: stale"
}

Test-Case "renew pushes the expiry out for the owner only" {
    $p = New-TestLock
    $rec = Enter-MaintenanceLock -Repo SEIM -RunId 1 -TtlSeconds 60 6>$null
    Assert ((Update-MaintenanceLock -Repo SEIM -RunId 1 -TtlSeconds 3600) -eq $true) "renewed"
    $l = Get-MaintenanceLock
    Assert ([DateTimeOffset]::Parse($l.ExpiresAt) -gt [DateTimeOffset]::UtcNow.AddMinutes(50)) "pushed out"
    Assert ($l.StartedAt -eq $rec.started_at) "started_at kept"
    Assert ((Update-MaintenanceLock -Repo SEIM -RunId 2) -eq $false) "other run"
    Assert ((Update-MaintenanceLock -Repo Cataloqui -RunId 1) -eq $false) "other repo"
    Assert ((Invoke-Cli @("-Action", "Renew", "-Repo", "SEIM", "-RunId", "1")) -eq 0) "cli renew"
    Assert ((Invoke-Cli @("-Action", "Renew", "-Repo", "SEIM", "-RunId", "9")) -eq 3) "cli renew not ours"
}

Test-Case "the heartbeat keeps a lock past its TTL while the caller blocks" {
    $p = New-TestLock
    Enter-MaintenanceLock -Repo SEIM -RunId 1 -TtlSeconds 3 6>$null | Out-Null
    $hb = Start-MaintenanceLockHeartbeat -Repo SEIM -RunId 1 -TtlSeconds 3 -IntervalSeconds 0.5
    try {
        & $pwshExe -NoProfile -Command "Start-Sleep -Seconds 5"   # a blocking native call, like docker build
        $l = Get-MaintenanceLock 3>$null
        Assert ($null -ne $l -and $l.RunId -eq "1") "still held after 5 s with a 3 s TTL"
        Assert ($hb.State.Renewals -ge 3) "renewals: $($hb.State.Renewals) err: $($hb.State.LastError)"
    } finally {
        Stop-MaintenanceLockHeartbeat $hb
    }
    Assert (Exit-MaintenanceLock -Repo SEIM -RunId 1 6>$null) "released"
}

Test-Case "the heartbeat stops once the lock is lost" {
    $p = New-TestLock
    Enter-MaintenanceLock -Repo SEIM -RunId 1 6>$null | Out-Null
    $hb = Start-MaintenanceLockHeartbeat -Repo SEIM -RunId 1 -IntervalSeconds 0.3
    try {
        Remove-Item $p
        $until = [DateTime]::UtcNow.AddSeconds(5)
        while (-not $hb.State.Lost -and [DateTime]::UtcNow -lt $until) { Start-Sleep -Milliseconds 100 }
        Assert $hb.State.Lost "lost"
    } finally { Stop-MaintenanceLockHeartbeat $hb }
}

Test-Case "a renew that could not run is retried after RetrySeconds, not a full interval" {
    $p = New-TestLock
    Enter-MaintenanceLock -Repo SEIM -RunId 1 6>$null | Out-Null
    [System.IO.File]::WriteAllText("$p.takeover", "someone")   # a fresh guard: renew returns $null
    $hb = Start-MaintenanceLockHeartbeat -Repo SEIM -RunId 1 -IntervalSeconds 4 -RetrySeconds 0.5
    try {
        Assert ($hb.RetrySeconds -eq 0.5) "retry"
        $until = [DateTime]::UtcNow.AddSeconds(10)
        while ($hb.State.Retries -lt 1 -and [DateTime]::UtcNow -lt $until) { Start-Sleep -Milliseconds 50 }
        Assert ($hb.State.Retries -ge 1) "a renew failed (guard busy): $($hb.State.LastError)"
        Remove-Item "$p.takeover"
        $t0 = [DateTime]::UtcNow
        while ($hb.State.Renewals -lt 1 -and [DateTime]::UtcNow -lt $t0.AddSeconds(8)) { Start-Sleep -Milliseconds 20 }
        $took = ([DateTime]::UtcNow - $t0).TotalSeconds
        Assert ($hb.State.Renewals -ge 1) "renewed after the guard went"
        # the guard wait is min(2, RetrySeconds) = 0.5 s, the retry pause 0.5 s: about 1 s at worst, a full interval is 4 s
        Assert ($took -lt 2.5) "retried within RetrySeconds, not after the 4 s interval: $took s"
    } finally { Stop-MaintenanceLockHeartbeat $hb }
    $default = Start-MaintenanceLockHeartbeat -Repo SEIM -RunId 1 -TtlSeconds 600
    try { Assert ($default.RetrySeconds -eq 5 -and $default.IntervalSeconds -eq 200) "defaults: $($default.RetrySeconds)/$($default.IntervalSeconds)" }
    finally { Stop-MaintenanceLockHeartbeat $default }
}

Test-Case "Test-MaintenanceLockHeartbeat: healthy, stopped runspace, stalled renewals, lost" {
    $p = New-TestLock
    Enter-MaintenanceLock -Repo SEIM -RunId 1 6>$null | Out-Null
    $hb = Start-MaintenanceLockHeartbeat -Repo SEIM -RunId 1 -IntervalSeconds 0.3
    try {
        Start-Sleep -Milliseconds 800
        $why = Test-MaintenanceLockHeartbeat $hb
        Assert ($null -eq $why) "healthy: $why"
        # renewals stop rising (the guard is held by someone else for good)
        [System.IO.File]::WriteAllText("$p.takeover", "someone")
        Start-Sleep -Milliseconds 1200
        $why = Test-MaintenanceLockHeartbeat $hb
        Assert ("$why" -match "no renewal for") "stalled: $why"
        Remove-Item "$p.takeover"
        Start-Sleep -Milliseconds 1500
        Assert ($null -eq (Test-MaintenanceLockHeartbeat $hb)) "healthy again"
        # the runspace ends
        $hb.PowerShell.Stop()
        Assert ($hb.Handle.IsCompleted) "completed"
        $why = Test-MaintenanceLockHeartbeat $hb
        Assert ("$why" -match "stopped running") "stopped: $why"
    } finally { Stop-MaintenanceLockHeartbeat $hb }
    $fake = [pscustomobject]@{ IntervalSeconds = 1; Handle = [pscustomobject]@{ IsCompleted = $false };
                               State = @{ Lost = $true; LastRenewedAt = [DateTime]::UtcNow; Retries = 0 } }
    Assert ("$(Test-MaintenanceLockHeartbeat $fake)" -match "no longer ours") "lost"
    Assert ("$(Test-MaintenanceLockHeartbeat $null)" -eq "no heartbeat") "none"
}

Test-Case "a crashed taker's guard goes stale; a fresh guard is respected" {
    $p = New-TestLock
    Write-TestLock $p (Get-StaleJson)
    [System.IO.File]::WriteAllText("$p.takeover", "someone")
    try { Enter-MaintenanceLock -Repo SEIM -RunId 1 -WaitSeconds 0 3>$null | Out-Null; Assert $false "taken past a fresh guard" }
    catch { Assert (Test-MaintenanceLockBusyError $_) "busy: $($_.Exception.Message)" }
    Assert ((ConvertFrom-MaintenanceLockBytes (Read-MaintenanceLockBytes $p)).RunId -eq "dead") "untouched"
    [System.IO.File]::SetLastWriteTimeUtc("$p.takeover", [DateTime]::UtcNow.AddSeconds(-11))
    Enter-MaintenanceLock -Repo SEIM -RunId 1 3>$null 6>$null | Out-Null
    Assert ((Get-MaintenanceLock).RunId -eq "1") "taken after the guard went stale"
    Assert (-not (Test-Path "$p.takeover")) "guard gone"
}

$isRoot = $false
if (-not $IsWindows -and (Get-Command id -ErrorAction SilentlyContinue)) { $isRoot = ((& id -u) -eq "0") }
if (-not $isRoot -and -not $IsWindows -and $PSVersionTable.PSVersion.Major -ge 6) {
    Test-Case "a stale lock that cannot be removed sleeps between tries and gives up at the deadline (exit 3)" {
        $p = New-TestLock
        Write-TestLock $p (Get-StaleJson)
        $dir = Split-Path $p
        & chmod 555 $dir
        try {
            $t0 = [DateTime]::UtcNow
            try { Enter-MaintenanceLock -Repo SEIM -RunId 1 -WaitSeconds 3 3>$null | Out-Null; Assert $false "taken" }
            catch { Assert (Test-MaintenanceLockBusyError $_) "busy: $($_.Exception.Message)" }
            $took = ([DateTime]::UtcNow - $t0).TotalSeconds
            Assert ($took -ge 2.9 -and $took -lt 10) "deadline: $took s"
            Assert ($script:MaintenanceLockAttempts -lt 200) "attempts: $($script:MaintenanceLockAttempts) (no spin)"
            $code = Invoke-Cli @("-Action", "Acquire", "-Repo", "SEIM", "-RunId", "1", "-WaitSeconds", "1")
            Assert ($code -eq 3) "cli exit $code"
        } finally { & chmod 755 $dir }
    }
}

Test-Case "racing takers on a stale lock: exactly one holder per round, none loses it mid-hold" {
    $p = New-TestLock
    $worker = @'
param($Lock, $LockScript, $I, $Start)
$env:MAINTENANCE_LOCK = $Lock
. $LockScript
while ([DateTime]::UtcNow -lt $Start) { Start-Sleep -Milliseconds 1 }
try { Enter-MaintenanceLock -Repo R -RunId "run$I" -TtlSeconds 60 -WaitSeconds 0 3>$null 6>$null | Out-Null }
catch { return "busy" }
$ok = $true
for ($k = 0; $k -lt 6; $k++) {
    Start-Sleep -Milliseconds 50
    $l = ConvertFrom-MaintenanceLockBytes (Read-MaintenanceLockBytes $Lock)
    if ($null -eq $l -or $l.RunId -ne "run$I") { $ok = $false; $saw = if ($null -eq $l) { "none" } else { "$($l.RunId)/$($l.Unreadable)" } }
}
Exit-MaintenanceLock -Repo R -RunId "run$I" 3>$null 6>$null | Out-Null
if ($ok) { "held" } else { "lost:$saw" }
'@
    $pool = [runspacefactory]::CreateRunspacePool(1, 8)
    $pool.Open()
    try {
        for ($round = 0; $round -lt 15; $round++) {
            Get-ChildItem (Split-Path $p) -ErrorAction SilentlyContinue | Remove-Item -Force
            Write-TestLock $p (Get-StaleJson)
            $start = [DateTime]::UtcNow.AddMilliseconds(400)
            $jobs = foreach ($i in 0..7) {
                $ps = [powershell]::Create()
                $ps.RunspacePool = $pool
                [void]$ps.AddScript($worker).AddArgument($p).AddArgument($LockScript).AddArgument($i).AddArgument($start)
                [pscustomobject]@{ PS = $ps; H = $ps.BeginInvoke() }
            }
            $res = foreach ($j in $jobs) { $j.PS.EndInvoke($j.H); $j.PS.Dispose() }
            $held = @($res | Where-Object { $_ -eq "held" }).Count
            $lost = @($res | Where-Object { "$_" -like "lost*" }).Count
            Assert ($held -eq 1 -and $lost -eq 0) "round $round : $($res -join ',')"
        }
    } finally { $pool.Close() }
}

if ($PythonModule) {
    $PythonModule = (Resolve-Path $PythonModule).Path
    $py = (Get-Command python3, python -ErrorAction SilentlyContinue | Select-Object -First 1).Source
    Test-Case "Python and PowerShell read each other's locks and refuse each other" {
        $p = New-TestLock
        Enter-MaintenanceLock -Repo SEIM -RunId ps1 6>$null | Out-Null
        $status = & $py $PythonModule status
        Assert ("$status" -match '"run_id": "ps1"') "python sees the PowerShell lock: $status"
        & $py $PythonModule acquire --repo Cataloqui --run-id py1 2>$null | Out-Null
        Assert ($LASTEXITCODE -eq 3) "python busy: $LASTEXITCODE"
        & $py $PythonModule renew --repo SEIM --run-id ps1 2>$null | Out-Null
        Assert ($LASTEXITCODE -eq 0) "python renews a PowerShell lock for its owner: $LASTEXITCODE"
        Assert ($null -ne (Get-MaintenanceLock)) "still valid after the python renew"
        Assert (Exit-MaintenanceLock -Repo SEIM -RunId ps1 6>$null) "released"
        & $py $PythonModule acquire --repo Cataloqui --run-id py1 2>$null | Out-Null
        Assert ($LASTEXITCODE -eq 0) "python takes it"
        try { Enter-MaintenanceLock -Repo SEIM -RunId ps2 | Out-Null; Assert $false "taken" }
        catch { Assert (Test-MaintenanceLockBusyError $_) "PowerShell busy" }
        Assert ((Update-MaintenanceLock -Repo Cataloqui -RunId py1) -eq $true) "PowerShell renews a Python lock for its owner"
        & $py $PythonModule release --repo Cataloqui --run-id py1 2>$null | Out-Null
        Assert (-not (Test-Path $p)) "python released"
    }
    Test-Case "a stale lock raced by Python and PowerShell takers: one holder" {
        $p = New-TestLock
        for ($round = 0; $round -lt 5; $round++) {
            Get-ChildItem (Split-Path $p) -ErrorAction SilentlyContinue | Remove-Item -Force
            Write-TestLock $p (Get-StaleJson)
            $code = "import sys,time,json,os; sys.path.insert(0, os.path.dirname(sys.argv[1])); import maintenance as m
t=float(sys.argv[2])
while time.time()<t: time.sleep(0.001)
try: m.acquire('R', sys.argv[3], ttl=60, wait=0)
except m.Busy: print('busy'); sys.exit()
ok=True
for _ in range(10):
    time.sleep(0.05); ok = ok and (m._read(m.Path(os.environ['MAINTENANCE_LOCK'])) or {}).get('run_id')==sys.argv[3]
print('held' if ok else 'lost'); m.release('R', sys.argv[3])"
            $start = [DateTimeOffset]::UtcNow.AddSeconds(2)
            $epoch = $start.ToUnixTimeMilliseconds() / 1000.0
            $procs = foreach ($i in 0..3) {
                $out = Join-Path (Split-Path $p) "py$i.out"
                Start-Process -FilePath $py -ArgumentList @("-c", "`"$($code -replace '"','\"')`"", $PythonModule, "$epoch", "py$i") -RedirectStandardOutput $out -PassThru -NoNewWindow
            }
            $worker = @"
`$env:MAINTENANCE_LOCK = '$p'
. '$LockScript'
while ([DateTimeOffset]::UtcNow -lt [DateTimeOffset]::FromUnixTimeMilliseconds($($start.ToUnixTimeMilliseconds()))) { Start-Sleep -Milliseconds 1 }
try { Enter-MaintenanceLock -Repo R -RunId ps -TtlSeconds 60 -WaitSeconds 0 3>`$null 6>`$null | Out-Null } catch { 'busy'; exit }
`$ok = `$true
for (`$k = 0; `$k -lt 10; `$k++) { Start-Sleep -Milliseconds 50; `$l = ConvertFrom-MaintenanceLockBytes (Read-MaintenanceLockBytes '$p'); if (`$null -eq `$l -or `$l.RunId -ne 'ps') { `$ok = `$false } }
Exit-MaintenanceLock -Repo R -RunId ps 3>`$null 6>`$null | Out-Null
if (`$ok) { 'held' } else { 'lost' }
"@
            $psRes = & $pwshExe -NoProfile -Command $worker
            foreach ($pr in $procs) { $pr.WaitForExit() }
            $res = @($psRes) + @(foreach ($i in 0..3) { (Get-Content (Join-Path (Split-Path $p) "py$i.out") -Raw).Trim() })
            $held = @($res | Where-Object { $_ -eq "held" }).Count
            $lost = @($res | Where-Object { $_ -eq "lost" }).Count
            Assert ($held -eq 1 -and $lost -eq 0) "round $round : $($res -join ',')"
        }
    }
}

Write-Output "$($script:passed) passed, $($script:failures) failed"
exit [int]($script:failures -gt 0)
