# Security Policy

SEIM handles student PII, document uploads, and JWT authentication. Please report security issues privately so we can fix them before public disclosure.

## Supported versions

| Version | Supported |
| --- | --- |
| `1.0.x` (default branch / latest release) | Yes |
| Older tags / forks | No — please upgrade or backport fixes yourself |

Security fixes land on the active development branches (`testing`, then `main` / default) and are included in the next `1.0.x` release when applicable.

## How to report a vulnerability

**Prefer GitHub private vulnerability reporting.** Do not open a public issue for security findings.

1. Open the repository **Security** tab.
2. Choose **Report a vulnerability** (GitHub private vulnerability reporting).
3. Include:
   - Affected version or commit
   - Impact (auth bypass, data exposure, RCE, etc.)
   - Steps to reproduce or a minimal proof of concept
   - Any known mitigations

If private vulnerability reporting is unavailable in the UI, contact a repository maintainer through a private channel and ask them to open a draft security advisory. Do not paste secrets, tokens, `.env` contents, or real student data into public issues, pull requests, or discussions.

## In scope

Examples of issues we want privately:

- Authentication and authorization flaws (JWT, session, role checks)
- Document upload abuse (path traversal, content-type bypass, malware delivery paths)
- Injection (SQL, template, command) and XSS that reaches SEIM surfaces
- Sensitive data exposure (PII, credentials, signed URLs)
- Dependency or configuration issues with a realistic exploit path in SEIM

## Out of scope

- Social engineering of end users
- Denial of service without a practical SEIM-specific vector
- Findings that only affect outdated, unsupported deployments
- Issues in third-party services outside this repository’s control (report those upstream)

## Response expectations

We aim to:

| Step | Target |
| --- | --- |
| Acknowledge the report | Within **3 business days** |
| Initial triage (severity / validity) | Within **7 business days** |
| Fix or mitigation plan for confirmed issues | As soon as practical; severity drives priority |
| Public disclosure / advisory | Coordinated with the reporter after a fix is available, or after an agreed delay |

We may ask for more detail. Credit is given in the advisory when the reporter wants it.

## Non-security bugs

Feature requests and non-security bugs belong in [GitHub Issues](https://github.com/mariomanza150/SEIM/issues). See [CONTRIBUTING.md](CONTRIBUTING.md).
