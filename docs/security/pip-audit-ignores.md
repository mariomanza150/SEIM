# pip-audit ignored vulnerabilities

CI runs `pip-audit --desc on` and fails on any known vulnerability. Every
ignored ID is listed here with its reason. Review the list whenever
dependencies change.

| ID | Package | Reason | Added | Remove when |
|----|---------|--------|-------|-------------|
| CVE-2026-106454 | twisted 26.4.0 (transitive via daphne / channels) | The flaw is in `wildcardToRegexp()` in `twisted/mail/imap4.py`. SEIM never imports or serves Twisted's IMAP4 code, so it can't be reached. No fixed Twisted release exists yet. | 2026-10-16 | Twisted publishes a fixed stable version (bump it and drop `--ignore-vuln`). |
| CVE-2026-115774 | twisted 26.4.0 | IMAP4 `parseNestedParens` negative literal DoS. SEIM does not run Twisted IMAP. Fix only in 26.10.0rc1. | 2026-10-29 | Stable Twisted release ≥ fixed version. |
| CVE-2026-115775 | twisted 26.4.0 | Unbounded XML element stream (XMPP/words). SEIM does not expose Twisted words/XMPP. Fix only in 26.10.0rc1. | 2026-10-29 | Stable Twisted release ≥ fixed version. |
| CVE-2026-115776 | twisted 26.4.0 | Unbounded IRC buffer. SEIM does not expose Twisted IRC. Fix only in 26.10.0rc1. | 2026-10-29 | Stable Twisted release ≥ fixed version. |
| CVE-2026-115778 | twisted 26.4.0 | Unbounded telnet/conch subnegotiation buffer. SEIM does not expose Twisted telnet/manhole. Fix only in 26.10.0rc1. | 2026-10-29 | Stable Twisted release ≥ fixed version. |
| CVE-2026-115877 | twisted 26.4.0 | HTTP header CR/LF smuggling gap in `HTTPChannel`. Daphne/ASGI path; no stable fix yet (26.10.0rc1 only). | 2026-10-29 | Stable Twisted release ≥ fixed version. |
| CVE-2026-83813 | twisted 26.4.0 | DNS datagram source-address not validated. SEIM does not use `twisted.names` as a resolver service. Fix only in 26.10.0rc1. | 2026-10-29 | Stable Twisted release ≥ fixed version. |
| GHSA-vpp8-g58w-m8mp | twisted 26.4.0 | HTTP/2 rapid-reset CPU DoS in `twisted.web._http2`. Daphne runs HTTP/1.1 behind nginx/cloudflared; SEIM does not serve Twisted HTTP/2 directly. Fix only in 26.10.0rc1. | 2026-10-29 | Stable Twisted release ≥ fixed version. |
