# Ensure Cloudflare Quick Tunnel is up for seim-localprod. Safe to run from Task Scheduler.
param(
    [string]$BackendUrl = "http://127.0.0.1:8020",
    [string]$HealthPath = "/health/"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StartScript = Join-Path $PSScriptRoot "start-cloudflare-tunnel.ps1"
$LogDir = Join-Path $ProjectRoot "logs"
$UrlFile = Join-Path $LogDir "cloudflare-tunnel.url"
$PidFile = Join-Path $LogDir "cloudflare-tunnel.pid"

function Test-TunnelHealthy([string]$Url) {
    try {
        $response = Invoke-WebRequest -Uri ($Url.TrimEnd("/") + $HealthPath) -UseBasicParsing -TimeoutSec 20
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

$needStart = $true
if ((Test-Path $UrlFile) -and (Test-Path $PidFile)) {
    $pidVal = Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
    $url = (Get-Content $UrlFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    $alive = $false
    if ($pidVal) {
        $proc = Get-Process -Id $pidVal -ErrorAction SilentlyContinue
        # cmd.exe wrapper or cloudflared child may own the pid file
        $alive = $null -ne $proc
        if (-not $alive) {
            $cf = Get-CimInstance Win32_Process -Filter "Name = 'cloudflared.exe'" -ErrorAction SilentlyContinue |
                Where-Object { $_.CommandLine -match [regex]::Escape($BackendUrl) }
            $alive = $null -ne $cf
        }
    }
    if ($alive -and $url -and (Test-TunnelHealthy $url)) {
        Write-Host "Cloudflare tunnel healthy: $url"
        $needStart = $false
    }
}

if ($needStart) {
    & $StartScript -BackendUrl $BackendUrl
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "start-cloudflare-tunnel.ps1 failed (exit $LASTEXITCODE)"
    }
    $url = (Get-Content $UrlFile | Select-Object -First 1).Trim()
    if (-not (Test-TunnelHealthy $url)) {
        throw "Tunnel started but health check failed for $url"
    }
    Write-Host "Cloudflare tunnel ready: $url"
}
