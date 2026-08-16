# Security Policy

## Supported Versions

SEIM is developed on a single rolling `main` branch. Only the latest released
line is supported with security fixes.

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

Pinned dependency versions (e.g. `Django==5.1.15`, `djangorestframework==3.16.1`,
`djangorestframework-simplejwt==5.5.1`) live in `requirements.txt`. Security
fixes are shipped by bumping those pins — Dependabot is enabled for `pip`,
`npm`, and `github-actions` to keep them current.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security problems.** This repository
handles student PII, identity documents, and authentication tokens; a public
issue would disclose the flaw before a fix is available.

### Preferred: GitHub private vulnerability reporting

Use GitHub's built-in private reporting so only the maintainers see the details:

1. Open the **Security** tab of this repository.
2. Click **Report a vulnerability**.
3. Fill in the form (affected version, description, steps to reproduce, impact).

> Note: the maintainer must first enable *Private vulnerability reporting*
> (Settings → Code security → Private vulnerability reporting). Once enabled,
> the Security tab above provides the report form and a `security-advisories`
> inbox. If it is not yet enabled, fall back to the email address below.

### Fallback: security contact email

If private reporting is unavailable, email the maintainer at
**security@seim.example.com** (replace with the real address before going live).
Use encrypted mail when possible and do not include live secrets or full
exploit code in the first message.

Please include:

- Affected version / commit (`git rev-parse HEAD`).
- A clear description and steps to reproduce.
- Impact and any suggested mitigation.
- Your contact details so we can follow up.

You can expect an acknowledgment within **72 hours**. We aim to provide a
triage and remediation plan within **7 days** for confirmed issues, and will
coordinate a disclosure timeline with you.

## Security Scope

This is a Django 5.1 + DRF backend serving a Vue 3 SPA (`/seim/`), a Wagtail
CMS (`/`, `/cms/`), and a REST API (`/api/`). The following areas are in scope
for security reports:

- **Authentication & authorization** — JWT issuance/refresh
  (`djangorestframework-simplejwt`), password reset, account lockout, role-based
  access control (Student / Coordinator / Admin), and session/CSRF handling.
- **Document uploads** — file upload, validation, storage
  (`django-storages`, local or S3), type/size limits, and the virus-scan
  integration in `documents/`. Report unsafe file handling, path traversal, or
  stored-XSS via uploaded content.
- **Injection** — SQL injection, ORM/`raw()` misuse, command injection,
  XSS/CSRF in the SPA and CMS templates, and unsafe deserialization.
- **PII exposure** — unintended disclosure of student personal data (profiles,
  grades, applications, documents) via API responses, logs, or error pages.
- **Secrets & configuration** — leaked `SECRET_KEY`, JWT/email/cloud
  credentials, or debug mode enabled in production. Secret scanning runs in CI
  (`.github/workflows/secret-scan.yml`); do not commit real `.env` contents.

### Out of scope (for this policy)

- Vulnerabilities only exploitable on a misconfigured deployment that diverges
  from `env.example` / the documented Docker setup (e.g. `DEBUG=True` in
  production, `ALLOWED_HOSTS` left open).
- Issues in third-party dependencies already tracked by Dependabot or CVEs
  (report the affected pin and we will bump it).
- Denial-of-service from missing rate limiting on public endpoints that are not
  yet protected — please still flag these as hardening suggestions.

## Best Practices for Reporters

- Keep exploits confidential until a fix is released.
- Allow a reasonable disclosure window after the fix before public write-ups.
- Credit will be given in release notes unless you prefer to remain anonymous.
