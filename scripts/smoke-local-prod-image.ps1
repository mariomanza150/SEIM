# Smoke-test a built seim-app image before tagging / deploying.
# Empty Postgres → migrate → check --deploy → gunicorn → GET /health/live/
#
#   .\scripts\smoke-local-prod-image.ps1 -Image "127.0.0.1:5000/seim-app:abc123"
#
param(
    [Parameter(Mandatory = $true)][string]$Image,
    [int]$TimeoutSec = 180
)

$ErrorActionPreference = "Stop"
$suffix = [Guid]::NewGuid().ToString("N").Substring(0, 8)
$net = "seim-smoke-$suffix"
$db = "seim-smoke-db-$suffix"
$web = "seim-smoke-web-$suffix"
$deadline = (Get-Date).AddSeconds($TimeoutSec)

function Assert-Budget {
    if ((Get-Date) -gt $deadline) { throw "Smoke test budget (${TimeoutSec}s) exhausted" }
}

function Invoke-Docker([string[]]$Args) {
    Assert-Budget
    & docker @Args
    if ($LASTEXITCODE -ne 0) { throw "docker $($Args -join ' ') failed (exit $LASTEXITCODE)" }
}

try {
    Write-Host "==> Smoke network $net"
    Invoke-Docker @("network", "create", $net)

    Write-Host "==> Empty Postgres"
    Invoke-Docker @(
        "run", "-d", "--name", $db, "--network", $net,
        "-e", "POSTGRES_DB=seim_smoke",
        "-e", "POSTGRES_USER=seimuser",
        "-e", "POSTGRES_PASSWORD=seimpass",
        "postgres:15-alpine"
    )
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        Assert-Budget
        & docker exec $db pg_isready -U seimuser -d seim_smoke | Out-Null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Seconds 2
    }
    if (-not $ready) { throw "Smoke Postgres never became ready" }

    $common = @(
        "--rm", "--network", $net,
        "-e", "DJANGO_SETTINGS_MODULE=seim.settings.production",
        "-e", "DJANGO_ENV=production",
        "-e", "DEBUG=False",
        "-e", "SECRET_KEY=smoke-test-not-for-production",
        "-e", "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1",
        "-e", "DATABASE_URL=postgresql://seimuser:seimpass@${db}:5432/seim_smoke",
        "-e", "REDIS_URL=redis://127.0.0.1:6379/15",
        "-e", "CELERY_BROKER_URL=redis://127.0.0.1:6379/15",
        "-e", "CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/15",
        "-e", "AWS_ACCESS_KEY_ID=smoke",
        "-e", "AWS_SECRET_ACCESS_KEY=smoke",
        "-e", "AWS_STORAGE_BUCKET_NAME=smoke-bucket",
        "-e", "SECURE_SSL_REDIRECT=False",
        "-e", "SESSION_COOKIE_SECURE=False",
        "-e", "CSRF_COOKIE_SECURE=False",
        "-e", "SECURE_HSTS_SECONDS=0",
        "-e", "USE_S3=false"
    )

    Write-Host "==> migrate (empty DB)"
    Invoke-Docker (@("run") + $common + @($Image, "python", "manage.py", "migrate", "--noinput"))

    Write-Host "==> check --deploy"
    Invoke-Docker (@("run") + $common + @($Image, "python", "manage.py", "check", "--deploy"))

    Write-Host "==> gunicorn + /health/live/"
    Invoke-Docker @(
        "run", "-d", "--name", $web, "--network", $net,
        "-e", "DJANGO_SETTINGS_MODULE=seim.settings.production",
        "-e", "DJANGO_ENV=production",
        "-e", "DEBUG=False",
        "-e", "SECRET_KEY=smoke-test-not-for-production",
        "-e", "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1",
        "-e", "DATABASE_URL=postgresql://seimuser:seimpass@${db}:5432/seim_smoke",
        "-e", "REDIS_URL=redis://127.0.0.1:6379/15",
        "-e", "AWS_ACCESS_KEY_ID=smoke",
        "-e", "AWS_SECRET_ACCESS_KEY=smoke",
        "-e", "AWS_STORAGE_BUCKET_NAME=smoke-bucket",
        "-e", "SECURE_SSL_REDIRECT=False",
        "-e", "SESSION_COOKIE_SECURE=False",
        "-e", "CSRF_COOKIE_SECURE=False",
        "-e", "SECURE_HSTS_SECONDS=0",
        "-e", "USE_S3=false",
        "-e", "SERVE_MEDIA=1",
        $Image,
        "gunicorn", "seim.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"
    )

    $healthy = $false
    for ($i = 0; $i -lt 40; $i++) {
        Assert-Budget
        & docker exec $web curl -fsS http://127.0.0.1:8000/health/live/ | Out-Null
        if ($LASTEXITCODE -eq 0) { $healthy = $true; break }
        Start-Sleep -Seconds 2
    }
    if (-not $healthy) {
        & docker logs $web 2>&1 | Select-Object -Last 40 | Out-Host
        throw "Smoke gunicorn never answered /health/live/"
    }
    Write-Host "OK: smoke passed for $Image" -ForegroundColor Green
}
finally {
    & docker rm -f $web 2>$null | Out-Null
    & docker rm -f $db 2>$null | Out-Null
    & docker network rm $net 2>$null | Out-Null
}
