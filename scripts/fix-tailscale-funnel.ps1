# Re-sync Tailscale Funnel to public internet (Windows control-plane bug)
# Run: powershell -ExecutionPolicy Bypass -File scripts\fix-tailscale-funnel.ps1

$ErrorActionPreference = "Stop"
$Port = 8001
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "Restarting Tailscale service (UAC prompt)..."
$restartScript = Join-Path $env:TEMP "restart-tailscale.ps1"
Set-Content $restartScript "Restart-Service Tailscale -Force`nStart-Sleep -Seconds 8"
Start-Process powershell -Verb RunAs -Wait -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$restartScript`""

Start-Sleep -Seconds 5
tailscale funnel --bg "http://127.0.0.1:$Port"
tailscale funnel status

$dns = (tailscale status --json | ConvertFrom-Json).Self.DNSName.TrimEnd('.')
Write-Host ""
Write-Host "Public URL: https://$dns/"
Write-Host "Share this URL with non-Tailscale clients (not the 100.x IP)."
