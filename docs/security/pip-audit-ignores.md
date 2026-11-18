# pip-audit ignored vulnerabilities

CI runs `pip-audit --desc on` and fails on any known vulnerability. Every
ignored ID must be listed here with its reason. Review the list whenever
dependencies change.

| ID | Package | Reason | Added | Remove when |
|----|---------|--------|-------|-------------|
| — | — | No ignores currently. Twisted ≥ 26.10.0 (via daphne/channels) cleared the prior CVE ignore list. | 2026-11-18 | Add a row before introducing any new `--ignore-vuln` in CI. |
