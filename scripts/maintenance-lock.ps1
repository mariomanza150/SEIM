<#
.SYNOPSIS
  Take, renew, release or show the machine-wide maintenance lock (%ProgramData%\ops\maintenance.lock).

.DESCRIPTION
  One deploy at a time on this machine, across repos, and no auto-heal while it runs: Otto's outage watcher and the
  runner skip container starts/restarts while a valid lock is held. loops/runner/maintenance.py (local-ai-stack) and
  SEIM's scripts/maintenance-lock.ps1 speak the same protocol; keep the copies identical.

  The lock file holds JSON {repo, run_id, pid, host, started_at, expires_at}.
  - Create: atomic and exclusive. Python writes a private temp file and hard-links it; PowerShell on Windows moves a
    temp file without overwrite; pwsh elsewhere uses CreateNew then writes (a reader may see it empty for a moment,
    which counts as held). Two takers never both win.
  - Valid: expires_at in the future and the holder is not an orphan (same host, pid not running). An unreadable lock
    counts as held; after 30 s unreadable it is stale.
  - Takeover, renew and release run under the guard file maintenance.lock.takeover (created like the lock). Under the guard the
    lock is re-read, and a stale lock is removed only if its bytes are identical to the stale bytes read before. A
    guard older than 10 s (a crashed taker) is removed, again only if its bytes did not change.
  - Renew (the heartbeat) and release: only the owner (same repo and run_id).
  Every attempt that does not take the lock sleeps before the next one and gives up at the deadline.

  Dot-source it to use the functions, or run it:
    .\maintenance-lock.ps1 -Action Acquire -Repo SEIM -RunId 123 -TtlSeconds 600 -WaitSeconds 300 [-HolderPid n]
        the lock is held for -HolderPid (default: the calling process); exit 0 = held, 2 = bad arguments, 3 = busy (another valid holder until the deadline), 4 = any other error
    .\maintenance-lock.ps1 -Action Renew -Repo SEIM -RunId 123 -TtlSeconds 600   # exit 3 = not ours
    .\maintenance-lock.ps1 -Action Release -Repo SEIM -RunId 123
    .\maintenance-lock.ps1 -Action Status
  In a script: Enter-MaintenanceLock, then Start-MaintenanceLockHeartbeat (renews every TTL/3 from a background
  runspace), and in finally Stop-MaintenanceLockHeartbeat and Exit-MaintenanceLock.
  $env:MAINTENANCE_LOCK overrides the path (tests). One-time setup: scripts/setup-maintenance-lock-dir.ps1.
  Windows PowerShell 5.1 and PowerShell 7.
#>
[CmdletBinding()]
param(
    [ValidateSet("Acquire", "Renew", "Release", "Status", "")]
    [string]$Action = "",
    [string]$Repo = "",
    [string]$RunId = "",
    [int]$TtlSeconds = 600,
    [int]$WaitSeconds = 0,
    [int]$HolderPid = 0
)

$script:MaintenanceLockSource = $PSCommandPath
$script:UnreadableGraceSeconds = 30
$script:GuardStaleSeconds = 10
$script:GuardWaitSeconds = 15
$script:RetryMilliseconds = 50
$script:StaleGraceSeconds = 2
$script:PollSeconds = 2
$script:Invariant = [Globalization.CultureInfo]::InvariantCulture
$script:MaintenanceLockAttempts = 0   # attempts by the last Enter-MaintenanceLock (tests: no busy loop)

function Get-MaintenanceLockPath {
    if ($env:MAINTENANCE_LOCK) { return $env:MAINTENANCE_LOCK }
    $base = $env:ProgramData
    if (-not $base) { $base = [System.IO.Path]::GetTempPath() }
    return (Join-Path (Join-Path $base "ops") "maintenance.lock")
}

function Get-MaintenanceLockHost {
    $name = $env:COMPUTERNAME
    if (-not $name) { $name = [Environment]::MachineName }
    return ($name.Split(".")[0]).ToLowerInvariant()
}

function Get-MaintenanceLockTimestamp([int]$AddSeconds = 0) {
    return [DateTimeOffset]::UtcNow.AddSeconds($AddSeconds).ToString("o", $script:Invariant)
}

function Read-MaintenanceLockBytes([string]$Path) {
    # The file's bytes as base64 (comparable), or $null when there is none. Opened with Delete sharing so a reader
    # never blocks a release or takeover. Other IO errors (in use) propagate.
    try {
        $fs = New-Object System.IO.FileStream($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read,
            ([System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete))
    } catch [System.IO.FileNotFoundException] {
        return $null
    } catch [System.IO.DirectoryNotFoundException] {
        return $null
    } catch {
        $inner = $_.Exception.InnerException
        if ($inner -is [System.IO.FileNotFoundException] -or $inner -is [System.IO.DirectoryNotFoundException]) { return $null }
        throw
    }
    try {
        $ms = New-Object System.IO.MemoryStream
        $fs.CopyTo($ms)
        return [Convert]::ToBase64String($ms.ToArray())
    } finally {
        $fs.Dispose()
    }
}

function ConvertFrom-MaintenanceLockBytes($Raw) {
    # $null: no file. Unreadable=$true: present but not a valid record. ($Raw is untyped: [string] would turn $null into "".)
    if ($null -eq $Raw) { return $null }
    try {
        $text = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Raw)).TrimStart([char]0xFEFF)
        $obj = $text | ConvertFrom-Json -ErrorAction Stop
        if ($null -eq $obj -or $null -eq $obj.run_id) { throw "not a lock record" }
        # Timestamps come from the raw text: PowerShell 7's ConvertFrom-Json turns ISO strings into local DateTimes.
        $started = if ($text -match '"started_at"\s*:\s*"([^"]+)"') { $Matches[1] } else { "" }
        $expires = if ($text -match '"expires_at"\s*:\s*"([^"]+)"') { $Matches[1] } else { "" }
        return @{ Unreadable = $false; Raw = $Raw; Repo = [string]$obj.repo; RunId = [string]$obj.run_id;
                  Pid = $obj.pid; Host = [string]$obj.host; StartedAt = $started; ExpiresAt = $expires }
    } catch {
        return @{ Unreadable = $true; Raw = $Raw }
    }
}

function Read-MaintenanceLock([string]$Path) {
    try { return (ConvertFrom-MaintenanceLockBytes (Read-MaintenanceLockBytes $Path)) }
    catch { return @{ Unreadable = $true; Raw = $null } }
}

function Get-MaintenanceLockStaleReason($Lock, [string]$Path) {
    # Why the lock is stale, or $null when it is valid (held).
    $exp = $null
    if (-not $Lock.Unreadable) {
        try { $exp = [DateTimeOffset]::Parse($Lock.ExpiresAt, $script:Invariant) } catch { $exp = $null }
    }
    if ($null -eq $exp) {
        if (-not (Test-Path -LiteralPath $Path)) { return "gone" }
        try { $age = ([DateTime]::UtcNow - [System.IO.File]::GetLastWriteTimeUtc($Path)).TotalSeconds } catch { return $null }
        if ($age -ge $script:UnreadableGraceSeconds) { return "unreadable for $([int]$age)s" }
        return $null
    }
    if ($exp -le [DateTimeOffset]::UtcNow) { return "expired $($Lock.ExpiresAt)" }
    $lockHost = ([string]$Lock.Host).Split(".")[0].ToLowerInvariant()
    if ($lockHost -and $lockHost -eq (Get-MaintenanceLockHost) -and $null -ne $Lock.Pid) {
        if (-not (Get-Process -Id ([int]$Lock.Pid) -ErrorAction SilentlyContinue)) {
            return "orphaned (pid $($Lock.Pid) is not running on $lockHost)"
        }
    }
    return $null
}

function Test-MaintenanceLockStale($Lock, [string]$Path) {
    return ($null -ne (Get-MaintenanceLockStaleReason $Lock $Path))
}

function Get-MaintenanceLock {
    <# The valid lock (hashtable; Unreadable=$true counts as held), or $null when there is none or it is stale. #>
    $path = Get-MaintenanceLockPath
    $lock = Read-MaintenanceLock $path
    if ($null -eq $lock) { return $null }
    $why = Get-MaintenanceLockStaleReason $lock $path
    if ($why) {
        Write-Warning "maintenance: ignoring a stale lock at $path ($($lock.Repo) run $($lock.RunId), $why)"
        return $null
    }
    return $lock
}

function New-MaintenanceLockTemp([string]$Path, [string]$Json) {
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $tmp = "$Path.$PID.$([Guid]::NewGuid().ToString('N')).tmp"
    [System.IO.File]::WriteAllBytes($tmp, (New-Object System.Text.UTF8Encoding($false)).GetBytes($Json))
    return $tmp
}

function Test-MaintenanceLockOnWindows {
    return (-not $IsLinux -and -not $IsMacOS)   # both undefined in Windows PowerShell 5.1
}

function New-MaintenanceLockFile([string]$Path, [string]$Text) {
    # $true when we created the file, $false when it exists. Windows: a temp file moved without overwrite (atomic,
    # never half-written). Elsewhere .NET's Move(overwrite: false) checks and then renames (not atomic), so the file
    # is created with CreateNew (O_EXCL) and then written: a reader may see it empty for a moment, which counts as
    # held (UnreadableGraceSeconds).
    if (Test-MaintenanceLockOnWindows) {
        $tmp = New-MaintenanceLockTemp $Path $Text
        try {
            [System.IO.File]::Move($tmp, $Path)
            return $true
        } catch {
            if (Test-Path -LiteralPath $Path) { return $false }
            throw
        } finally {
            if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
        }
    }
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    try {
        $fs = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write,
                                     [System.IO.FileShare]::None)
    } catch {
        if (Test-Path -LiteralPath $Path) { return $false }
        throw
    }
    try {
        $bytes = (New-Object System.Text.UTF8Encoding($false)).GetBytes($Text)
        $fs.Write($bytes, 0, $bytes.Length)
    } finally {
        $fs.Dispose()
    }
    return $true
}

function Enter-MaintenanceLockGuard([string]$Path, [double]$WaitSeconds) {
    # Our guard token, or $null when it could not be had within WaitSeconds. The guard is created like the lock. A
    # guard older than GuardStaleSeconds (a crashed taker) is removed if it still exists and its bytes did not change.
    $guard = "$Path.takeover"
    $deadline = [DateTime]::UtcNow.AddSeconds($WaitSeconds)
    while ($true) {
        $token = "$(Get-MaintenanceLockHost):$($PID):$([Guid]::NewGuid().ToString('N'))"
        $created = $false
        try { $created = New-MaintenanceLockFile $guard $token } catch { $created = $false }
        if ($created) { return $token }
        try {
            $seen = Read-MaintenanceLockBytes $guard
            $fi = New-Object System.IO.FileInfo($guard)
            if ($null -ne $seen -and $fi.Exists) {  # Exists: a missing file's LastWriteTimeUtc is 1601
                $age = ([DateTime]::UtcNow - $fi.LastWriteTimeUtc).TotalSeconds
                if ($age -gt $script:GuardStaleSeconds -and (Read-MaintenanceLockBytes $guard) -eq $seen) {
                    Write-Warning "maintenance: removing a stale takeover guard ($([int]$age)s old)"
                    [System.IO.File]::Delete($guard)
                }
            }
        } catch { }
        if ([DateTime]::UtcNow -ge $deadline) { return $null }
        Start-Sleep -Milliseconds $script:RetryMilliseconds
    }
}

function Exit-MaintenanceLockGuard([string]$Path, [string]$Token) {
    $guard = "$Path.takeover"
    try {
        $raw = Read-MaintenanceLockBytes $guard
        if ($null -ne $raw -and [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($raw)) -eq $Token) {
            [System.IO.File]::Delete($guard)
        }
    } catch { }
}

function Invoke-MaintenanceLockTakeover([string]$Path, [string]$StaleRaw) {
    # Remove the stale lock whose bytes we read, under the guard and only if unchanged. $true when removed.
    $token = Enter-MaintenanceLockGuard $Path 0
    if ($null -eq $token) { return $false }
    try {
        if ((Read-MaintenanceLockBytes $Path) -ne $StaleRaw) { return $false }
        [System.IO.File]::Delete($Path)
        return $true
    } finally {
        Exit-MaintenanceLockGuard $Path $token
    }
}

function New-MaintenanceLockBusyError([string]$Message) {
    $ex = New-Object System.InvalidOperationException($Message)
    $ex.Data["MaintenanceLockBusy"] = $true
    return $ex
}

function Test-MaintenanceLockBusyError($ErrorRecord) {
    $ex = $ErrorRecord
    if ($ErrorRecord -is [System.Management.Automation.ErrorRecord]) { $ex = $ErrorRecord.Exception }
    return ($null -ne $ex -and $ex.Data.Contains("MaintenanceLockBusy"))
}

function ConvertTo-MaintenanceLockJson($Rec) {
    # Field order and types match maintenance.py.
    return ('{{"repo": {0}, "run_id": {1}, "pid": {2}, "host": {3}, "started_at": {4}, "expires_at": {5}}}' -f
        (ConvertTo-Json -InputObject ([string]$Rec.repo) -Compress), (ConvertTo-Json -InputObject ([string]$Rec.run_id) -Compress),
        [int]$Rec.pid, (ConvertTo-Json -InputObject ([string]$Rec.host) -Compress),
        (ConvertTo-Json -InputObject ([string]$Rec.started_at) -Compress), (ConvertTo-Json -InputObject ([string]$Rec.expires_at) -Compress))
}

function Enter-MaintenanceLock {
    <# Take the lock, waiting up to WaitSeconds for a valid one to go. Returns the record; throws an exception with
       Data["MaintenanceLockBusy"] when busy (Test-MaintenanceLockBusyError), any other exception on other errors. #>
    param([Parameter(Mandatory)][string]$Repo, [Parameter(Mandatory)][string]$RunId,
          [int]$TtlSeconds = 600, [int]$WaitSeconds = 0, [int]$HolderPid = 0)
    if ($HolderPid -le 0) { $HolderPid = $PID }
    $path = Get-MaintenanceLockPath
    $start = [DateTime]::UtcNow
    $deadline = $start.AddSeconds([Math]::Max(0, $WaitSeconds))
    $warned = $null
    $seen = $null
    $lastError = $null
    $script:MaintenanceLockAttempts = 0
    while ($true) {
        $script:MaintenanceLockAttempts++
        $rec = [ordered]@{ repo = $Repo; run_id = $RunId; pid = $HolderPid; host = (Get-MaintenanceLockHost);
                           started_at = (Get-MaintenanceLockTimestamp); expires_at = (Get-MaintenanceLockTimestamp $TtlSeconds) }
        $pauseMs = $script:PollSeconds * 1000
        $limit = $deadline
        try {
            if (New-MaintenanceLockFile $path (ConvertTo-MaintenanceLockJson $rec)) {
                Write-Host "maintenance: $Repo run $RunId took the lock until $($rec.expires_at)"
                return $rec
            }
            $raw = Read-MaintenanceLockBytes $path
            if ($null -eq $raw) { continue }  # released between our create and our read: try again at once
            $seen = ConvertFrom-MaintenanceLockBytes $raw
            if (-not $seen.Unreadable -and $seen.RunId -eq $RunId -and $seen.Repo -eq $Repo) { return $seen }
            $why = Get-MaintenanceLockStaleReason $seen $path
            if ($why) {
                if ($warned -ne $raw) {
                    Write-Warning "maintenance: replacing a stale lock ($($seen.Repo) run $($seen.RunId), $why)"
                    $warned = $raw
                }
                if (Invoke-MaintenanceLockTakeover $path $raw) { continue }
                $pauseMs = $script:RetryMilliseconds
                $graceEnd = $start.AddSeconds($script:StaleGraceSeconds)
                if ($graceEnd -gt $limit) { $limit = $graceEnd }
            }
        } catch [System.IO.IOException], [System.UnauthorizedAccessException] {
            # The lock or its guard is in use or cannot be removed right now: retried, like busy.
            $pauseMs = $script:RetryMilliseconds * 4
            $lastError = $_.Exception
            if ($null -eq $seen) { try { $seen = ConvertFrom-MaintenanceLockBytes (Read-MaintenanceLockBytes $path) } catch { } }
        }
        $leftMs = ($limit - [DateTime]::UtcNow).TotalMilliseconds
        if ($leftMs -le 0) {
            # Nobody holds it and we still could not create it (e.g. access denied on the folder): not "busy".
            if ($null -eq $seen -and $null -ne $lastError) { throw $lastError }
            if ($null -eq $seen -or $seen.Unreadable) { $who = "an unreadable lock" } else { $who = "$($seen.Repo) run $($seen.RunId)" }
            throw (New-MaintenanceLockBusyError "maintenance lock held by $who until $($seen.ExpiresAt)")
        }
        Start-Sleep -Milliseconds ([int][Math]::Max(1, [Math]::Min($pauseMs, $leftMs)))
    }
}

function Update-MaintenanceLock {
    <# Renew: push expires_at out to now + TtlSeconds if Repo/RunId holds the lock. $true renewed, $false not ours,
       $null not this time (guard busy or file in use). #>
    param([Parameter(Mandatory)][string]$Repo, [Parameter(Mandatory)][string]$RunId, [int]$TtlSeconds = 600)
    $path = Get-MaintenanceLockPath
    $token = Enter-MaintenanceLockGuard $path $script:GuardWaitSeconds
    if ($null -eq $token) { return $null }
    try {
        $lock = ConvertFrom-MaintenanceLockBytes (Read-MaintenanceLockBytes $path)
        if ($null -eq $lock -or $lock.Unreadable -or $lock.RunId -ne $RunId -or $lock.Repo -ne $Repo) { return $false }
        $rec = [ordered]@{ repo = $lock.Repo; run_id = $lock.RunId; pid = $lock.Pid; host = $lock.Host;
                           started_at = $lock.StartedAt; expires_at = (Get-MaintenanceLockTimestamp $TtlSeconds) }
        $tmp = New-MaintenanceLockTemp $path (ConvertTo-MaintenanceLockJson $rec)
        try {
            [System.IO.File]::Replace($tmp, $path, [NullString]::Value)
        } finally {
            if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
        }
        return $true
    } catch {
        return $null
    } finally {
        Exit-MaintenanceLockGuard $path $token
    }
}

function Exit-MaintenanceLock {
    <# Drop the lock if Repo/RunId holds it. Returns whether it was removed. Someone else's lock, stale or not, is
       left for its owner or the next taker. #>
    param([Parameter(Mandatory)][string]$Repo, [Parameter(Mandatory)][string]$RunId)
    $path = Get-MaintenanceLockPath
    for ($i = 0; $i -lt 3; $i++) {
        $token = Enter-MaintenanceLockGuard $path $script:GuardWaitSeconds
        if ($null -eq $token) {
            Write-Warning "maintenance: run $RunId could not get the guard to release the lock"
            return $false
        }
        try {
            $lock = ConvertFrom-MaintenanceLockBytes (Read-MaintenanceLockBytes $path)
            if ($null -eq $lock) { return $false }
            if ($lock.Unreadable -or $lock.RunId -ne $RunId -or $lock.Repo -ne $Repo) {
                Write-Warning "maintenance: $Repo run $RunId may not release the lock held by $($lock.Repo) run $($lock.RunId)"
                return $false
            }
            [System.IO.File]::Delete($path)
            Write-Host "maintenance: $Repo run $RunId released the lock"
            return $true
        } catch [System.IO.IOException], [System.UnauthorizedAccessException] {
            Start-Sleep -Milliseconds ($script:RetryMilliseconds * 4)
        } finally {
            Exit-MaintenanceLockGuard $path $token
        }
    }
    return $false
}

function Start-MaintenanceLockHeartbeat {
    <# Renew Repo/RunId's lock every IntervalSeconds (default TtlSeconds/3) from a background runspace, so it keeps
       running while the caller blocks on docker. Stop it with Stop-MaintenanceLockHeartbeat. .State.Lost is set
       once the lock is no longer ours. #>
    param([Parameter(Mandatory)][string]$Repo, [Parameter(Mandatory)][string]$RunId, [int]$TtlSeconds = 600,
          [double]$IntervalSeconds = 0)
    if ($IntervalSeconds -le 0) { $IntervalSeconds = [Math]::Max(1, $TtlSeconds / 3) }
    $state = [hashtable]::Synchronized(@{ Stop = $false; Renewals = 0; Lost = $false; LastError = $null })
    $loop = @'

$hb = $MaintenanceLockHeartbeatState
while (-not $hb.Stop) {
    $until = [DateTime]::UtcNow.AddSeconds($MaintenanceLockHeartbeatInterval)
    while (-not $hb.Stop -and [DateTime]::UtcNow -lt $until) { Start-Sleep -Milliseconds 200 }
    if ($hb.Stop) { break }
    try {
        $ok = Update-MaintenanceLock -Repo $Repo -RunId $RunId -TtlSeconds $TtlSeconds
        if ($ok -eq $true) { $hb.Renewals++ }
        elseif ($ok -eq $false) { $hb.Lost = $true; break }
    } catch { $hb.LastError = $_.Exception.Message }
}
'@
    $text = [System.IO.File]::ReadAllText($script:MaintenanceLockSource) + "`n" + $loop
    $rs = [runspacefactory]::CreateRunspace()
    $rs.Open()
    $rs.SessionStateProxy.SetVariable("MaintenanceLockHeartbeatState", $state)
    $rs.SessionStateProxy.SetVariable("MaintenanceLockHeartbeatInterval", $IntervalSeconds)
    $ps = [powershell]::Create()
    $ps.Runspace = $rs
    [void]$ps.AddScript($text).AddParameter("Repo", $Repo).AddParameter("RunId", $RunId).AddParameter("TtlSeconds", $TtlSeconds)
    $handle = $ps.BeginInvoke()
    return [pscustomobject]@{ Repo = $Repo; RunId = $RunId; State = $state; PowerShell = $ps; Handle = $handle; Runspace = $rs }
}

function Get-MaintenanceLockParentPid {
    # The process that ran this script as a command (the CLI's lock is held on its behalf), or $PID.
    try {
        $p = Get-CimInstance Win32_Process -Filter "ProcessId=$PID" -ErrorAction Stop
        if ($p.ParentProcessId) { return [int]$p.ParentProcessId }
    } catch { }
    try {
        $parent = (Get-Process -Id $PID).Parent
        if ($parent) { return [int]$parent.Id }
    } catch { }
    return $PID
}

function Stop-MaintenanceLockHeartbeat($Heartbeat) {
    if ($null -eq $Heartbeat) { return }
    $Heartbeat.State.Stop = $true
    try {
        if ($Heartbeat.Handle.AsyncWaitHandle.WaitOne(($script:GuardWaitSeconds + 5) * 1000)) {
            [void]$Heartbeat.PowerShell.EndInvoke($Heartbeat.Handle)
        } else {
            $Heartbeat.PowerShell.Stop()
        }
    } catch { }
    $Heartbeat.PowerShell.Dispose()
    $Heartbeat.Runspace.Dispose()
}

if ($Action -eq "Acquire") {
    if (-not $Repo -or -not $RunId) { Write-Error "-Repo and -RunId are required" -ErrorAction Continue; exit 2 }
    try {
        # Run as a command, this process exits at once: the lock is held for the caller (-HolderPid, else the parent).
        if ($HolderPid -le 0) { $HolderPid = Get-MaintenanceLockParentPid }
        Enter-MaintenanceLock -Repo $Repo -RunId $RunId -TtlSeconds $TtlSeconds -WaitSeconds $WaitSeconds -HolderPid $HolderPid | Out-Null
        exit 0
    } catch {
        Write-Error $_.Exception.Message -ErrorAction Continue
        if (Test-MaintenanceLockBusyError $_) { exit 3 }
        exit 4
    }
} elseif ($Action -eq "Renew") {
    if (-not $Repo -or -not $RunId) { Write-Error "-Repo and -RunId are required" -ErrorAction Continue; exit 2 }
    $ok = Update-MaintenanceLock -Repo $Repo -RunId $RunId -TtlSeconds $TtlSeconds
    if ($ok -eq $true) { exit 0 } elseif ($ok -eq $false) { exit 3 } else { exit 4 }
} elseif ($Action -eq "Release") {
    if (-not $Repo -or -not $RunId) { Write-Error "-Repo and -RunId are required" -ErrorAction Continue; exit 2 }
    try { Exit-MaintenanceLock -Repo $Repo -RunId $RunId | Out-Null; exit 0 }
    catch { Write-Error $_.Exception.Message -ErrorAction Continue; exit 4 }
} elseif ($Action -eq "Status") {
    $l = Get-MaintenanceLock
    if ($null -eq $l) { Write-Output "free" }
    elseif ($l.Unreadable) { Write-Output "held (unreadable lock)" }
    else { Write-Output "$($l.Repo) run $($l.RunId) until $($l.ExpiresAt)" }
    exit 0
}
