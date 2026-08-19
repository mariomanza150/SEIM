# Reconfigure the local-prod GitHub runner to run as a Windows service.
# Requires elevated PowerShell (Admin).
param(
    [string]$RunnerDir = "C:\actions-runner\seim-localprod",
    [string]$RepoUrl = "https://github.com/mariomanza150/SEIM"
)

$ErrorActionPreference = "Stop"
$bootScript = Join-Path (Split-Path -Parent $PSScriptRoot) "scripts\install-local-prod-boot.ps1"
& $bootScript -RunnerDir $RunnerDir -RepoUrl $RepoUrl
