# pip-audit ignored vulnerabilities

CI runs `pip-audit --desc on` and fails on any known vulnerability. Every
ignored ID is listed here with its reason. Review the list whenever
dependencies change.

| ID | Package | Reason | Added | Remove when |
|----|---------|--------|-------|-------------|
| CVE-2026-106454 | twisted 26.4.0 (transitive via daphne / channels) | The flaw is in `wildcardToRegexp()` in `twisted/mail/imap4.py`. SEIM never imports or serves Twisted's IMAP4 code, so it can't be reached. No fixed Twisted release exists yet. | 2026-10-16 | Twisted publishes a fixed version (bump it and drop `--ignore-vuln`). |
