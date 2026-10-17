<#
.SYNOPSIS
  Take, release or show the machine-wide maintenance lock (%ProgramData%\ops\maintenance.lock).

.DESCRIPTION
  One deploy at a time on this machine, across repos, and no auto-heal while it runs: Otto's outage watcher and the
  runner skip container starts/restarts while a valid lock is held (loops/runner/maintenance.py has the same
  protocol). The lock file holds JSON {repo, run_id, pid, started_at, expires_at}. It is created with an atomic
  create-exclusive open (FileMode.CreateNew), so two takers never both win. A lock past expires_at (or unreadable
  for more than 30 s) is stale: it is ignored, a warning is written, and it is replaced. Only the owner (same
  run_id) releases it.

  This is a copy of local-ai-stack's scripts/maintenance-lock.ps1 (same file, same protocol) so SEIM's deploy does
  not depend on that checkout. Keep the two in sync.

  Dot-source it to use the functions, or run it:
    .\maintenance-lock.ps1 -Action Acquire -Repo SEIM -RunId 123 -TtlSeconds 1800 -WaitSeconds 600   # exit 3 = busy
    .\maintenance-lock.ps1 -Action Release -RunId 123
    .\maintenance-lock.ps1 -Action Status
  $env:MAINTENANCE_LOCK overrides the path (tests).
#>
[CmdletBinding()]
param(
    [ValidateSet("Acquire", "Release", "Status", "")]
    [string]$Action = "",
    [string]$Repo = "",
    [string]$RunId = "",
    [int]$TtlSeconds = 1800,
    [int]$WaitSeconds = 0
)

$script:UnreadableGraceSeconds = 30

function Get-MaintenanceLockPath {
    if ($env:MAINTENANCE_LOCK) { return $env:MAINTENANCE_LOCK }
    $base = $env:ProgramData
    if (-not $base) { $base = [System.IO.Path]::GetTempPath() }
    return (Join-Path (Join-Path $base "ops") "maintenance.lock")
}

function Read-MaintenanceLock([string]$Path) {
    # $null: no file. A hashtable with Unreadable=$true: present but not valid JSON (yet).
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try {
        $text = [System.IO.File]::ReadAllText($Path)
        $obj = $text | ConvertFrom-Json -ErrorAction Stop
        if ($null -eq $obj) { throw "empty" }
        # Timestamps come from the raw text: PowerShell 7's ConvertFrom-Json turns ISO strings into local DateTimes.
        $started = if ($text -match '"started_at"\s*:\s*"([^"]+)"') { $Matches[1] } else { "" }
        $expires = if ($text -match '"expires_at"\s*:\s*"([^"]+)"') { $Matches[1] } else { "" }
        return @{ Unreadable = $false; Text = $text; Repo = [string]$obj.repo; RunId = [string]$obj.run_id;
                  Pid = $obj.pid; StartedAt = $started; ExpiresAt = $expires }
    } catch {
        return @{ Unreadable = $true; Text = $null }
    }
}

function Test-MaintenanceLockStale($Lock, [string]$Path) {
    if ($Lock.Unreadable) {
        try { $age = ((Get-Date) - (Get-Item -LiteralPath $Path).LastWriteTime).TotalSeconds } catch { return $true }
        return ($age -ge $script:UnreadableGraceSeconds)
    }
    try {
        $exp = [DateTimeOffset]::Parse($Lock.ExpiresAt, [Globalization.CultureInfo]::InvariantCulture)
    } catch { return $true }
    return ($exp -le [DateTimeOffset]::UtcNow)
}

function Get-MaintenanceLock {
    <# The valid lock (hashtable), or $null when there is none or it is stale (a warning says so). #>
    $path = Get-MaintenanceLockPath
    $lock = Read-MaintenanceLock $path
    if ($null -eq $lock) { return $null }
    if (Test-MaintenanceLockStale $lock $path) {
        Write-Warning "maintenance: ignoring a stale lock at $path ($($lock.Repo) run $($lock.RunId), expired $($lock.ExpiresAt))"
        return $null
    }
    return $lock
}

function New-MaintenanceLockFile([string]$Path, [string]$Json) {
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    try {
        $fs = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write,
                                     [System.IO.FileShare]::None)
    } catch [System.IO.IOException] {
        if (Test-Path -LiteralPath $Path) { return $false }
        throw
    }
    try {
        $bytes = (New-Object System.Text.UTF8Encoding($false)).GetBytes($Json)
        $fs.Write($bytes, 0, $bytes.Length)
    } finally {
        $fs.Dispose()
    }
    return $true
}

function Enter-MaintenanceLock {
    <# Take the lock, waiting up to WaitSeconds for a valid one to go. Returns the record; throws when busy. #>
    param([Parameter(Mandatory)][string]$Repo, [Parameter(Mandatory)][string]$RunId,
          [int]$TtlSeconds = 1800, [int]$WaitSeconds = 0)
    $path = Get-MaintenanceLockPath
    $deadline = (Get-Date).AddSeconds([Math]::Max(0, $WaitSeconds))
    while ($true) {
        $now = [DateTimeOffset]::UtcNow
        $rec = [ordered]@{ repo = $Repo; run_id = $RunId; pid = $PID;
                           started_at = $now.ToString("yyyy-MM-ddTHH:mm:ss+00:00");
                           expires_at = $now.AddSeconds($TtlSeconds).ToString("yyyy-MM-ddTHH:mm:ss+00:00") }
        $json = $rec | ConvertTo-Json -Compress
        if (New-MaintenanceLockFile $path $json) {
            Write-Host "maintenance: $Repo run $RunId took the lock until $($rec.expires_at)"
            return $rec
        }
        $seen = Read-MaintenanceLock $path
        if ($null -eq $seen) { continue }
        if (Test-MaintenanceLockStale $seen $path) {
            Write-Warning "maintenance: replacing a stale lock ($($seen.Repo) run $($seen.RunId), expired $($seen.ExpiresAt))"
            $again = Read-MaintenanceLock $path
            if ($null -ne $again -and $again.Text -eq $seen.Text) {
                Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
            }
            continue
        }
        if (-not $seen.Unreadable -and $seen.RunId -eq $RunId -and $seen.Repo -eq $Repo) { return $seen }
        if ((Get-Date) -ge $deadline) {
            throw "maintenance lock held by $($seen.Repo) run $($seen.RunId) until $($seen.ExpiresAt)"
        }
        Start-Sleep -Seconds 2
    }
}

function Exit-MaintenanceLock {
    <# Drop the lock if RunId holds it (or it is stale). Returns whether it was removed. #>
    param([Parameter(Mandatory)][string]$RunId)
    $path = Get-MaintenanceLockPath
    $lock = Read-MaintenanceLock $path
    if ($null -eq $lock) { return $false }
    if ($lock.RunId -ne $RunId -and -not (Test-MaintenanceLockStale $lock $path)) {
        Write-Warning "maintenance: run $RunId may not release the lock held by $($lock.Repo) run $($lock.RunId)"
        return $false
    }
    Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
    Write-Host "maintenance: run $RunId released the lock"
    return $true
}

if ($Action -eq "Acquire") {
    if (-not $Repo -or -not $RunId) { Write-Error "-Repo and -RunId are required"; exit 2 }
    try { Enter-MaintenanceLock -Repo $Repo -RunId $RunId -TtlSeconds $TtlSeconds -WaitSeconds $WaitSeconds | Out-Null; exit 0 }
    catch { Write-Error $_.Exception.Message; exit 3 }
} elseif ($Action -eq "Release") {
    if (-not $RunId) { Write-Error "-RunId is required"; exit 2 }
    Exit-MaintenanceLock -RunId $RunId | Out-Null
    exit 0
} elseif ($Action -eq "Status") {
    $l = Get-MaintenanceLock
    if ($l) { Write-Output "$($l.Repo) run $($l.RunId) until $($l.ExpiresAt)" } else { Write-Output "free" }
    exit 0
}
