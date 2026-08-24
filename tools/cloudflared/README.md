# cloudflared (portable)

Binary is gitignored. Download:

```powershell
New-Item -ItemType Directory -Force -Path tools\cloudflared | Out-Null
Invoke-WebRequest `
  -Uri "https://github.com/cloudflare/cloudflared/releases/download/2026.8.2/cloudflared-windows-amd64.exe" `
  -OutFile tools\cloudflared\cloudflared.exe
```

Then:

```powershell
.\scripts\ensure-cloudflare-tunnel.ps1
Get-Content .\logs\cloudflare-tunnel.url
```

Account confirmation emails use the host the user registered from. Tunnel start also writes that origin to `FRONTEND_BASE_URL` in `.env.local-prod`.

On this network, tunnels use `--protocol http2` (UDP/QUIC is blocked).
