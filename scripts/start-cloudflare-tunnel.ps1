# Start Cloudflare Tunnel for seim-localprod (named tunnel preferred, Quick Tunnel fallback).
#
# Named (stable hostname): run setup-named-cloudflare-tunnel.ps1 first.
# Quick: temporary https://*.trycloudflare.com (changes each restart).
param(
    [string]$BackendUrl = "http://127.0.0.1:8020",
    [int]$ReadyTimeoutSec = 120
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Cloudflared = Join-Path $ProjectRoot "tools\cloudflared\cloudflared.exe"
$ConfigDir = Join-Path $ProjectRoot "config\cloudflared"
$ConfigFile = Join-Path $ConfigDir "config.yml"
$StateFile = Join-Path $ConfigDir "tunnel-state.json"
$LogDir = Join-Path $ProjectRoot "logs"
$UrlFile = Join-Path $LogDir "cloudflare-tunnel.url"
$LogFile = Join-Path $LogDir "cloudflare-tunnel.log"
$PidFile = Join-Path $LogDir "cloudflare-tunnel.pid"

function Write-Step([string]$Message) {
    Write-Host "==> $Message"
}

function Stop-SeimCloudflared {
    if (Test-Path $PidFile) {
        $oldPid = Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($oldPid) {
            $proc = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Step "Stopping previous wrapper PID $oldPid ($($proc.ProcessName))"
                Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
            }
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }

    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            ($_.Name -eq "cloudflared.exe" -and $_.CommandLine -match "tunnel") -or
            ($_.Name -eq "cmd.exe" -and $_.CommandLine -match "cloudflared.exe")
        } |
        ForEach-Object {
            Write-Step "Stopping $($_.Name) PID $($_.ProcessId)"
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }

    Start-Sleep -Seconds 2
}

function Test-PublicHealth([string]$Url) {
    try {
        $code = curl.exe -s -o NUL -w "%{http_code}" "$($Url.TrimEnd('/'))/health/" --max-time 20
        return $code -eq "200"
    }
    catch {
        return $false
    }
}

function Set-SeimFrontendBaseUrl([string]$PublicUrl) {
    $envFile = Join-Path $ProjectRoot ".env.local-prod"
    $origin = $PublicUrl.Trim().TrimEnd("/")
    if (-not $origin) { return }
    if (-not (Test-Path $envFile)) {
        Write-Step "Skip FRONTEND_BASE_URL update (.env.local-prod missing)"
        return
    }
    $found = $false
    $changed = $false
    $newLines = foreach ($line in Get-Content $envFile) {
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
        Set-Content -Path $envFile -Value $newLines -Encoding utf8
        Write-Step "Updated FRONTEND_BASE_URL=$origin in .env.local-prod"
    }
}

if (-not (Test-Path $Cloudflared)) {
    throw "cloudflared not found at $Cloudflared"
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Stop-SeimCloudflared

$useNamed = (Test-Path $ConfigFile) -and (Test-Path $StateFile)
Remove-Item $UrlFile -Force -ErrorAction SilentlyContinue
if (Test-Path $LogFile) {
    try { Remove-Item $LogFile -Force -ErrorAction Stop }
    catch {
        $LogFile = Join-Path $LogDir ("cloudflare-tunnel-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
    }
}

if ($useNamed) {
    $state = Get-Content $StateFile -Raw | ConvertFrom-Json
    $publicUrl = $state.publicUrl
    if (-not $publicUrl -and $state.hostname) {
        $publicUrl = "https://$($state.hostname)"
    }
    Write-Step "Starting named tunnel '$($state.tunnelName)' -> $BackendUrl (http2)"
    Write-Step "Hostname: $publicUrl"
    $arg = "/c `"`"$Cloudflared`" tunnel --config `"$ConfigFile`" --protocol http2 --no-autoupdate run >`"$LogFile`" 2>&1`""
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList $arg -WindowStyle Hidden -PassThru
    Set-Content -Path $PidFile -Value $proc.Id -Encoding ascii
    Set-Content -Path $UrlFile -Value $publicUrl -Encoding utf8

    $deadline = (Get-Date).AddSeconds($ReadyTimeoutSec)
    $registered = $false
    while ((Get-Date) -lt $deadline) {
        if (Test-Path $LogFile) {
            $text = Get-Content $LogFile -Raw -ErrorAction SilentlyContinue
            if ($text -match "Registered tunnel connection") {
                $registered = $true
                break
            }
        }
        if ($proc.HasExited) {
            throw "cloudflared exited early (code $($proc.ExitCode)). See $LogFile"
        }
        Start-Sleep -Seconds 2
    }

    $probeOk = $false
    $probeDeadline = (Get-Date).AddSeconds(90)
    while ((Get-Date) -lt $probeDeadline) {
        if (Test-PublicHealth $publicUrl) {
            $probeOk = $true
            break
        }
        Write-Step "Waiting for $publicUrl/health/ ..."
        Start-Sleep -Seconds 5
    }
    if (-not $probeOk) {
        throw "Named tunnel did not become healthy at $publicUrl. See $LogFile"
    }

    Set-SeimFrontendBaseUrl $publicUrl
    Write-Step "Public URL: $publicUrl"
    Write-Step "SPA:        $publicUrl/seim/"
    Write-Host "cloudflared wrapper PID $($proc.Id) running (named)."
    return
}

# --- Quick Tunnel fallback ---
Write-Step "No named config at $ConfigFile — starting Quick Tunnel (ephemeral URL)"
Write-Step "For a stable hostname: .\scripts\setup-named-cloudflare-tunnel.ps1 -Hostname seim.example.com"
$arg = "/c `"`"$Cloudflared`" tunnel --url $BackendUrl --protocol http2 --no-autoupdate >`"$LogFile`" 2>&1`""
$proc = Start-Process -FilePath "cmd.exe" -ArgumentList $arg -WindowStyle Hidden -PassThru
Set-Content -Path $PidFile -Value $proc.Id -Encoding ascii

$deadline = (Get-Date).AddSeconds($ReadyTimeoutSec)
$publicUrl = $null
while ((Get-Date) -lt $deadline) {
    if (Test-Path $LogFile) {
        $text = Get-Content $LogFile -Raw -ErrorAction SilentlyContinue
        if ($text -match "https://[a-z0-9-]+\.trycloudflare\.com") {
            $publicUrl = $Matches[0]
            Set-Content -Path $UrlFile -Value $publicUrl -Encoding utf8
            Write-Step "Tunnel hostname: $publicUrl"
        }
        if ($publicUrl -and $text -match "Registered tunnel connection") {
            break
        }
    }
    if ($proc.HasExited) {
        throw "cloudflared exited early (code $($proc.ExitCode)). See $LogFile"
    }
    Start-Sleep -Seconds 2
}

if (-not $publicUrl) {
    throw "Timed out waiting for trycloudflare.com URL. See $LogFile"
}

$probeOk = $false
$probeDeadline = (Get-Date).AddSeconds(60)
while ((Get-Date) -lt $probeDeadline) {
    if (Test-PublicHealth $publicUrl) {
        $probeOk = $true
        break
    }
    Write-Step "Public probe waiting..."
    Start-Sleep -Seconds 5
}
if (-not $probeOk) {
    throw "Tunnel URL $publicUrl did not return HTTP 200 from /health/. See $LogFile"
}

Set-Content -Path $UrlFile -Value $publicUrl -Encoding utf8
Set-SeimFrontendBaseUrl $publicUrl
Write-Step "Public URL: $publicUrl"
Write-Step "SPA:        $publicUrl/seim/"
Write-Host "cloudflared wrapper PID $($proc.Id) running (quick)."
