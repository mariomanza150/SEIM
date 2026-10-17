<#
.SYNOPSIS
  One-time setup for the machine-wide maintenance lock: create C:\ProgramData\ops and give every account that takes
  the lock (the GitHub runners, the agent-loops runner) Modify on it.

.DESCRIPTION
  Run once per machine, elevated (Windows PowerShell 5.1 or pwsh):
    .\scripts\setup-maintenance-lock-dir.ps1 -Account "WIN-A82J3T7T7M5\Rene Montes"
    .\scripts\setup-maintenance-lock-dir.ps1 -Account "DOMAIN\runner1", "DOMAIN\runner2"
  Without -Account it lists who runs the GitHub runner services/tasks and the agent-loops runner, and grants those.
  Modify is granted with (OI)(CI) inheritance, so a lock or guard file created by one account can be replaced or
  removed by the others (a stale takeover, a release). LocalSystem and Administrators already have full control.
  Idempotent. The same script is in local-ai-stack and SEIM; keep them identical.
#>
[CmdletBinding()]
param(
    [string[]]$Account = @(),
    [string]$Dir = (Join-Path $env:ProgramData "ops")
)
$ErrorActionPreference = "Stop"

function Get-LockAccounts {
    $names = New-Object System.Collections.Generic.List[string]
    try {
        foreach ($svc in Get-CimInstance Win32_Service -Filter "Name LIKE 'actions.runner.%'") {
            if ($svc.StartName -and $svc.StartName -notin @("LocalSystem", "NT AUTHORITY\SYSTEM")) { $names.Add($svc.StartName) }
        }
    } catch { Write-Warning "could not list runner services: $($_.Exception.Message)" }
    try {
        foreach ($task in Get-ScheduledTask | Where-Object { $_.TaskName -like "github-runner-*" -or $_.TaskName -eq "agent-loops-runner" }) {
            $user = $task.Principal.UserId
            if ($user -and $user -notin @("SYSTEM", "NT AUTHORITY\SYSTEM")) {
                if ($user -notmatch '\\') { $user = "$env:COMPUTERNAME\$user" }
                $names.Add($user)
            }
        }
    } catch { Write-Warning "could not list scheduled tasks: $($_.Exception.Message)" }
    return @($names | Sort-Object -Unique)
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this elevated (it changes the ACL of $Dir)."
}
if ($Account.Count -eq 0) {
    $Account = Get-LockAccounts
    if ($Account.Count -eq 0) { throw "No runner accounts found; pass -Account." }
    Write-Host "Accounts that run the runners: $($Account -join ', ')"
}
if (-not (Test-Path -LiteralPath $Dir)) {
    New-Item -ItemType Directory -Path $Dir | Out-Null
    Write-Host "Created $Dir"
}
foreach ($a in $Account) {
    & icacls $Dir /grant "$($a):(OI)(CI)M" | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "icacls /grant for $a failed (exit $LASTEXITCODE)" }
}
& icacls $Dir | Out-Host
