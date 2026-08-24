# Install boot-time autostart for:
#   1. Docker Desktop (user setting)
#   2. seim-localprod Docker stack (Scheduled Task, delayed after logon)
#   3. Cloudflare Quick Tunnel to :8020 (logon + every 15m)
#   4. GitHub Actions self-hosted runner as a Windows service (requires admin)
#
# Usage (elevated PowerShell recommended):
#   .\scripts\install-local-prod-boot.ps1
#   .\scripts\install-local-prod-boot.ps1 -SkipRunnerService   # stack only
param(
    [switch]$SkipRunnerService,
    [string]$RunnerDir = "C:\actions-runner\seim-localprod",
    [string]$RepoUrl = "https://github.com/mariomanza150/SEIM",
    [int]$StackDelaySec = 90
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StackScript = Join-Path $ProjectRoot "scripts\start-local-prod-stack.ps1"
$TunnelTaskName = "SEIM-cloudflare-tunnel"
$TunnelScript = Join-Path $ProjectRoot "scripts\ensure-cloudflare-tunnel.ps1"
$StackTaskName = "SEIM-localprod-stack"
$RunnerTaskName = "SEIM-github-runner"
$LogDir = Join-Path $ProjectRoot "logs"
$RunnerLog = Join-Path $LogDir "github-runner-service-install.log"

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-IsAdmin {
    return ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
}

function Ensure-Directory([string]$Path) {
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Set-DockerDesktopAutoStart {
    $settingsPath = Join-Path $env:APPDATA "Docker\settings-store.json"
    if (-not (Test-Path $settingsPath)) {
        Write-Warning "Docker settings file not found at $settingsPath - enable 'Start Docker Desktop when you sign in' manually."
        return
    }
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    if ($settings.AutoStart -ne $true) {
        $settings | Add-Member -NotePropertyName AutoStart -NotePropertyValue $true -Force
        $settings | ConvertTo-Json | Set-Content $settingsPath -Encoding UTF8
        Write-Host "Enabled Docker Desktop AutoStart in $settingsPath"
    }
    else {
        Write-Host "Docker Desktop AutoStart already enabled"
    }
}

function Install-StackScheduledTask {
    if (-not (Test-Path $StackScript)) {
        throw "Missing $StackScript"
    }

    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StackScript`"" `
        -WorkingDirectory $ProjectRoot

    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $trigger.Delay = "PT${StackDelaySec}S"

    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew

    Register-ScheduledTask `
        -TaskName $StackTaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Start seim-localprod Docker stack after logon (waits for Docker Desktop)" `
        -Force | Out-Null

    Write-Host "Scheduled task '$StackTaskName' registered (At logon, ${StackDelaySec}s delay)"
}

function Install-CloudflareTunnelScheduledTask {
    if (-not (Test-Path $TunnelScript)) {
        Write-Warning "Missing $TunnelScript - skip Cloudflare tunnel task"
        return
    }

    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$TunnelScript`"" `
        -WorkingDirectory $ProjectRoot

    # After stack (stack delay + buffer), then every 15 minutes.
    $tunnelDelaySec = [Math]::Max($StackDelaySec + 60, 150)
    $logon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $logon.Delay = "PT${tunnelDelaySec}S"
    $repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(5) `
        -RepetitionInterval (New-TimeSpan -Minutes 15) `
        -RepetitionDuration (New-TimeSpan -Days 3650)

    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew

    Register-ScheduledTask `
        -TaskName $TunnelTaskName `
        -Action $action `
        -Trigger @($logon, $repeat) `
        -Settings $settings `
        -Description "Ensure Cloudflare Quick Tunnel to seim-localprod :8020" `
        -Force | Out-Null

    Write-Host "Scheduled task '$TunnelTaskName' registered (logon + every 15m)"
}

function Install-RunnerFallbackTask([string]$Dir) {
    $runCmd = Join-Path $Dir "run.cmd"
    if (-not (Test-Path $runCmd)) {
        Write-Warning "Runner run.cmd not found; skipping fallback logon task."
        return
    }

    $action = New-ScheduledTaskAction `
        -Execute $runCmd `
        -WorkingDirectory $Dir

    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew

    Register-ScheduledTask `
        -TaskName $RunnerTaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Fallback GitHub runner autostart if Windows service cannot access Docker Desktop" `
        -Force | Out-Null

    Write-Host "Fallback scheduled task '$RunnerTaskName' registered (At logon)"
}

function Stop-InteractiveRunner([string]$Dir) {
    Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "Stopping interactive runner PID $($_.Id)"
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

function Install-RunnerWindowsService([string]$Dir) {
    $configCmd = Join-Path $Dir "config.cmd"
    if (-not (Test-Path $configCmd)) {
        throw "Runner config.cmd not found in $Dir"
    }

    Ensure-Directory $LogDir
    Stop-InteractiveRunner $Dir

    $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'User')
    Set-Location (Split-Path -Parent $PSScriptRoot)
    $tokenResponse = gh api repos/mariomanza150/SEIM/actions/runners/registration-token -X POST
    $regToken = ($tokenResponse | ConvertFrom-Json).token

    $adminScript = Join-Path $ProjectRoot "scripts\install-github-runner-service-admin.ps1"
    $argList = @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-File', "`"$adminScript`"",
        '-RegistrationToken', $regToken
    )
    Write-Host "Launching elevated runner service install..."
    $proc = Start-Process powershell -Verb RunAs -Wait -PassThru -ArgumentList $argList
    if ($proc.ExitCode -ne 0) {
        throw "Elevated runner service install failed (exit $($proc.ExitCode)). See $RunnerLog"
    }

    $service = Get-Service -Name "actions.runner.*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($service) {
        Write-Host "Runner Windows service '$($service.Name)' is $($service.Status)"
    }
    else {
        throw "Runner service not found after install. See $RunnerLog"
    }
}

Write-Step "Enabling Docker Desktop autostart"
Set-DockerDesktopAutoStart

Write-Step "Installing seim-localprod stack scheduled task"
Install-StackScheduledTask

Write-Step "Installing Cloudflare Tunnel scheduled task"
Install-CloudflareTunnelScheduledTask

if (-not $SkipRunnerService) {
    if (Test-IsAdmin) {
        Write-Step "Installing GitHub runner as Windows service (admin)"
        Install-RunnerWindowsService $RunnerDir
    }
    else {
        Write-Warning "Not running as Administrator - cannot install runner Windows service."
        Write-Warning "Re-run elevated: Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"'"
        Write-Step "Registering fallback runner logon task instead"
        Install-RunnerFallbackTask $RunnerDir
    }
}

Write-Step "Boot autostart setup complete"
Write-Host "Stack task : Get-ScheduledTask -TaskName '$StackTaskName'"
Write-Host "Tunnel task: Get-ScheduledTask -TaskName '$TunnelTaskName'"
Write-Host "Runner     : Get-Service 'actions.runner.*' or task '$RunnerTaskName'"
Write-Host "Test stack : .\scripts\start-local-prod-stack.ps1"
Write-Host "Test tunnel: .\scripts\ensure-cloudflare-tunnel.ps1"
