# Ensure Cloudflare Tunnel for seim-localprod via Docker Compose profiles.
# Prefer: cloudflare (token) when CLOUDFLARE_TUNNEL_TOKEN is set, else cloudflare-quick.
# Host cloudflared.exe is used only when a named config.yml from setup-named-cloudflare-tunnel.ps1 exists.
#
# Safe to run from Task Scheduler / start-local-prod-stack.ps1.
param(
    [string]$HealthPath = "/health/",
    [int]$ReadyTimeoutSec = 120
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker-compose.local-prod.yml"
$EnvFile = Join-Path $ProjectRoot ".env.local-prod"
$ProjectName = "seim-localprod"
$ConfigDir = Join-Path $ProjectRoot "config\cloudflared"
$ConfigFile = Join-Path $ConfigDir "config.yml"
$StateFile = Join-Path $ConfigDir "tunnel-state.json"
$LogDir = Join-Path $ProjectRoot "logs"
$UrlFile = Join-Path $LogDir "cloudflare-tunnel.url"
$HostStartScript = Join-Path $PSScriptRoot "start-cloudflare-tunnel.ps1"

function Write-Step([string]$Message) {
    Write-Host "==> $Message"
}

function Test-TunnelHealthy([string]$Url) {
    if (-not $Url) { return $false }
    try {
        $code = curl.exe -s -o NUL -w "%{http_code}" "$($Url.TrimEnd('/'))$HealthPath" --max-time 20
        return $code -eq "200"
    }
    catch {
        return $false
    }
}

function Set-SeimFrontendBaseUrl([string]$PublicUrl) {
    $origin = $PublicUrl.Trim().TrimEnd("/")
    if (-not $origin) { return $false }
    if (-not (Test-Path $EnvFile)) {
        Write-Step "Skip FRONTEND_BASE_URL update (.env.local-prod missing)"
        return $false
    }
    $found = $false
    $changed = $false
    $newLines = foreach ($line in Get-Content $EnvFile) {
        if ($line -match '^FRONTEND_BASE_URL=') {
            $found = $true
            if ($line -ne "FRONTEND_BASE_URL=$origin") { $changed = $true }
            "FRONTEND_BASE_URL=$origin"
        }
        else {
            $line
        }
    }
    if (-not $found) {
        $newLines = @($newLines) + "FRONTEND_BASE_URL=$origin"
        $changed = $true
    }
    if ($changed) {
        Set-Content -Path $EnvFile -Value $newLines -Encoding utf8
        Write-Step "Updated FRONTEND_BASE_URL=$origin in .env.local-prod"
    }
    return $changed
}

function Get-LocalProdTunnelToken {
    if ($env:CLOUDFLARE_TUNNEL_TOKEN) {
        return $env:CLOUDFLARE_TUNNEL_TOKEN.Trim()
    }
    if (Test-Path $EnvFile) {
        $line = Get-Content $EnvFile | Where-Object { $_ -match '^\s*CLOUDFLARE_TUNNEL_TOKEN\s*=' } | Select-Object -First 1
        if ($line -and $line -match '^\s*CLOUDFLARE_TUNNEL_TOKEN\s*=\s*(.*)$') {
            return $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return ""
}

function Stop-HostCloudflared {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            ($_.Name -eq "cloudflared.exe" -and $_.CommandLine -match "tunnel") -or
            ($_.Name -eq "cmd.exe" -and $_.CommandLine -match "cloudflared.exe")
        } |
        ForEach-Object {
            Write-Step "Stopping host $($_.Name) PID $($_.ProcessId)"
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
}

function Get-QuickTunnelUrlFromLogs {
    $logs = docker compose -p $ProjectName -f $ComposeFile --env-file $EnvFile --profile cloudflare-quick logs --no-color --tail 200 cloudflared-quick 2>$null
    if (-not $logs) { return $null }
    $text = if ($logs -is [array]) { $logs -join "`n" } else { [string]$logs }
    $m = [regex]::Match($text, "https://[a-z0-9-]+\.trycloudflare\.com")
    if ($m.Success) { return $m.Value }
    return $null
}

function Test-ComposeServiceRunning([string]$Service, [string]$Profile) {
    $lines = docker compose -p $ProjectName -f $ComposeFile --env-file $EnvFile --profile $Profile ps --status running --services 2>$null
    return ($lines -split "`n" | ForEach-Object { $_.Trim() }) -contains $Service
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Named host tunnel (stable hostname from setup-named-cloudflare-tunnel.ps1)
if ((Test-Path $ConfigFile) -and (Test-Path $StateFile)) {
    Write-Step "Named host tunnel config present - using start-cloudflare-tunnel.ps1"
    & $HostStartScript
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "start-cloudflare-tunnel.ps1 failed (exit $LASTEXITCODE)"
    }
    $url = (Get-Content $UrlFile | Select-Object -First 1).Trim()
    if (-not (Test-TunnelHealthy $url)) {
        throw "Named tunnel started but health check failed for $url"
    }
    Write-Host "Cloudflare tunnel ready: $url"
    return
}

if (-not (Test-Path $EnvFile)) {
    throw ".env.local-prod not found at $EnvFile"
}
if (-not (Test-Path $ComposeFile)) {
    throw "Missing $ComposeFile"
}

$token = Get-LocalProdTunnelToken
$useToken = -not [string]::IsNullOrWhiteSpace($token)

# Avoid two tunnels fighting for the same origin
Stop-HostCloudflared

if ($useToken) {
    Write-Step "Ensuring Docker Cloudflare Tunnel (token / profile cloudflare)"
    docker compose -p $ProjectName -f $ComposeFile --env-file $EnvFile --profile cloudflare up -d cloudflared
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start cloudflared (token) container"
    }
    # Token tunnels use a dashboard hostname; persist FRONTEND_BASE_URL if already set.
    if (Test-Path $UrlFile) {
        $url = (Get-Content $UrlFile | Select-Object -First 1).Trim()
        if ($url -and (Test-TunnelHealthy $url)) {
            Write-Host "Cloudflare tunnel ready: $url"
            return
        }
    }
    Write-Host "Cloudflare token tunnel container started. Set logs\cloudflare-tunnel.url to your public hostname if needed."
    return
}

Write-Step "Ensuring Docker Cloudflare Quick Tunnel (profile cloudflare-quick)"
$needStart = $true
if (Test-ComposeServiceRunning "cloudflared-quick" "cloudflare-quick") {
    $url = Get-QuickTunnelUrlFromLogs
    if (-not $url -and (Test-Path $UrlFile)) {
        $url = (Get-Content $UrlFile | Select-Object -First 1).Trim()
    }
    if ($url -and (Test-TunnelHealthy $url)) {
        Set-Content -Path $UrlFile -Value $url -Encoding utf8
        [void](Set-SeimFrontendBaseUrl $url)
        Write-Host "Cloudflare tunnel healthy: $url"
        $needStart = $false
    }
}

if ($needStart) {
    docker compose -p $ProjectName -f $ComposeFile --env-file $EnvFile --profile cloudflare-quick up -d --force-recreate cloudflared-quick
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start cloudflared-quick container"
    }

    $deadline = (Get-Date).AddSeconds($ReadyTimeoutSec)
    $publicUrl = $null
    while ((Get-Date) -lt $deadline) {
        $publicUrl = Get-QuickTunnelUrlFromLogs
        if ($publicUrl) {
            Set-Content -Path $UrlFile -Value $publicUrl -Encoding utf8
            Write-Step "Tunnel hostname: $publicUrl"
            if (Test-TunnelHealthy $publicUrl) {
                break
            }
            Write-Step "Public probe waiting..."
        }
        Start-Sleep -Seconds 3
    }

    if (-not $publicUrl) {
        docker compose -p $ProjectName -f $ComposeFile --env-file $EnvFile --profile cloudflare-quick logs --tail 80 cloudflared-quick
        throw "Timed out waiting for trycloudflare.com URL from cloudflared-quick"
    }
    if (-not (Test-TunnelHealthy $publicUrl)) {
        throw "Tunnel URL $publicUrl did not return HTTP 200 from $HealthPath"
    }

    $changed = Set-SeimFrontendBaseUrl $publicUrl
    if ($changed) {
        Write-Step "Recreating web so FRONTEND_BASE_URL takes effect"
        docker compose -p $ProjectName -f $ComposeFile --env-file $EnvFile up -d --force-recreate --no-deps web
    }

    Write-Step "Public URL: $publicUrl"
    Write-Step "SPA:        $publicUrl/seim/"
    Write-Host "Cloudflare tunnel ready: $publicUrl"
}
