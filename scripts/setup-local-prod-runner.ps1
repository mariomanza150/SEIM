# Register a GitHub Actions self-hosted runner for seim-localprod CD.
#
# Prerequisite: download the runner zip from GitHub first:
#   Repo → Settings → Actions → Runners → New self-hosted runner → Windows x64
#   Extract to e.g. C:\actions-runner\seim-localprod
#
# Usage (from extracted runner folder, after setting GITHUB_PAT or using the UI token):
#   $env:RUNNER_TOKEN = "<registration-token-from-github>"
#   .\scripts\setup-local-prod-runner.ps1 -RunnerDir "C:\actions-runner\seim-localprod"
#
param(
    [Parameter(Mandatory = $true)]
    [string]$RunnerDir,

    [string]$RunnerName = $env:COMPUTERNAME,

    [string]$RunnerLabels = "self-hosted,windows,local-prod",

    [string]$RunnerToken = $env:RUNNER_TOKEN,

    [string]$RepoUrl = "https://github.com/mariomanza150/SEIM"
)

$ErrorActionPreference = "Stop"

if (-not $RunnerToken) {
    throw @"
RUNNER_TOKEN is required.
Get a registration token from GitHub → Settings → Actions → Runners → New self-hosted runner.
Then: `$env:RUNNER_TOKEN = '<token>'; .\scripts\setup-local-prod-runner.ps1 -RunnerDir 'C:\actions-runner\seim-localprod'
"@
}

if (-not (Test-Path $RunnerDir)) {
    throw "Runner directory not found: $RunnerDir. Download and extract the GitHub runner first."
}

$configScript = Join-Path $RunnerDir "config.cmd"
if (-not (Test-Path $configScript)) {
    throw "config.cmd not found in $RunnerDir. Extract the official actions-runner zip there first."
}

Push-Location $RunnerDir
try {
    Write-Host "Configuring runner '$RunnerName' with labels: $RunnerLabels" -ForegroundColor Cyan
    & .\config.cmd `
        --url $RepoUrl `
        --token $RunnerToken `
        --name $RunnerName `
        --labels $RunnerLabels `
        --unattended `
        --replace

    Write-Host ""
    Write-Host "Runner configured. Install as a Windows service (recommended):" -ForegroundColor Green
    Write-Host "  cd $RunnerDir"
    Write-Host "  .\svc.cmd install"
    Write-Host "  .\svc.cmd start"
    Write-Host ""
    Write-Host "Or run interactively: .\run.cmd"
}
finally {
    Pop-Location
}
