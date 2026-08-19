@echo off
REM Install GitHub Actions runner as a Windows service (requires one UAC approval).
REM Usage: double-click, or from repo root: scripts\install-github-runner-service-elevated.cmd
setlocal
cd /d "%~dp0.."

if /I "%~1"=="elevated" goto :install

echo Fetching GitHub runner registration token...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop'; ^
   $logDir = Join-Path (Get-Location) 'logs'; New-Item -ItemType Directory -Force -Path $logDir | Out-Null; ^
   $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); ^
   $token = (gh api repos/mariomanza150/SEIM/actions/runners/registration-token -X POST | ConvertFrom-Json).token; ^
   Set-Content -Path (Join-Path $logDir 'runner-registration-token.txt') -Value $token -NoNewline"

if errorlevel 1 (
  echo Failed to fetch registration token. Ensure gh/git credentials are configured.
  pause
  exit /b 1
)

echo Launching elevated installer...
powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -ArgumentList 'elevated'"
exit /b 0

:install
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-github-runner-service-admin.ps1"
if errorlevel 1 (
  echo Runner service install failed. See logs\github-runner-service-install.log
  pause
  exit /b 1
)
echo Runner Windows service installed.
pause
