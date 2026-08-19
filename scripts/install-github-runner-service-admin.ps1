# Admin-only: remove existing runner config and reinstall as Windows service.
param(
    [string]$TokenFile = "c:\Users\OEM\Documents\APPLICACION\SEIM\logs\runner-registration-token.txt",

    [string]$RunnerDir = "C:\actions-runner\seim-localprod",
    [string]$RepoUrl = "https://github.com/mariomanza150/SEIM"
)

$ErrorActionPreference = "Stop"
$LogDir = "c:\Users\OEM\Documents\APPLICACION\SEIM\logs"
$RunnerLog = Join-Path $LogDir "github-runner-service-install.log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (-not (Test-Path $TokenFile)) {
    throw "Registration token file not found: $TokenFile"
}
$RegistrationToken = (Get-Content $TokenFile -Raw).Trim()
if (-not $RegistrationToken) {
    throw "Registration token file is empty"
}

Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Set-Location $RunnerDir
$runnerName = "$env:COMPUTERNAME-localprod"

if (Test-Path ".\.runner") {
    Write-Host "Removing existing runner configuration..."
    & .\config.cmd remove --unattended --token $RegistrationToken 2>&1 | Tee-Object -FilePath $RunnerLog -Append
}

Write-Host "Configuring runner as Windows service: $runnerName"
& .\config.cmd `
    --unattended `
    --url $RepoUrl `
    --token $RegistrationToken `
    --name $runnerName `
    --labels "self-hosted,local-prod" `
    --replace `
    --runasservice 2>&1 | Tee-Object -FilePath $RunnerLog -Append

if ($LASTEXITCODE -ne 0) {
    throw "config.cmd --runasservice failed with exit $LASTEXITCODE"
}

$service = Get-CimInstance Win32_Service | Where-Object { $_.Name -like "actions.runner.*" } | Select-Object -First 1
if (-not $service) {
    throw "Runner service was not created. See $RunnerLog"
}

Set-Service -Name $service.Name -StartupType Automatic
if ((Get-Service $service.Name).Status -ne "Running") {
    Start-Service $service.Name
}

Get-Service $service.Name | Format-Table Name, Status, StartType
Remove-Item $TokenFile -Force -ErrorAction SilentlyContinue
Write-Host "Runner service installed successfully."
