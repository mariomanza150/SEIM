# Cloudflare Tunnel for SEIM local-prod

Preferred path is **Docker Compose profiles** on `docker-compose.local-prod.yml` (no host binary required):

```powershell
# Ephemeral Quick Tunnel (*.trycloudflare.com)
docker compose -p seim-localprod -f docker-compose.local-prod.yml --profile cloudflare-quick --env-file .env.local-prod up -d

# Or let the boot/ensure scripts pick the profile:
.\scripts\start-local-prod-stack.ps1
.\scripts\ensure-cloudflare-tunnel.ps1
Get-Content .\logs\cloudflare-tunnel.url
```

Managed tunnel (stable hostname): set `CLOUDFLARE_TUNNEL_TOKEN` in `.env.local-prod`, then use `--profile cloudflare`. In the Cloudflare dashboard, point the public hostname at `http://localhost:8000` (cloudflared shares the `web` network namespace).

On this network, tunnels use `--protocol http2` (UDP/QUIC is blocked).

## Optional host binary

Still used by `setup-named-cloudflare-tunnel.ps1` / host `start-cloudflare-tunnel.ps1` when `config\cloudflared\config.yml` exists:

```powershell
New-Item -ItemType Directory -Force -Path tools\cloudflared | Out-Null
Invoke-WebRequest `
  -Uri "https://github.com/cloudflare/cloudflared/releases/download/2026.8.2/cloudflared-windows-amd64.exe" `
  -OutFile tools\cloudflared\cloudflared.exe
```

Account confirmation emails use the host the user registered from. Tunnel start also writes that origin to `FRONTEND_BASE_URL` in `.env.local-prod`.
