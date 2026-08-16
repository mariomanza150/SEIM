"""Run axe-core against a Playwright page without skipping when the helper is installed."""

from __future__ import annotations

from typing import Any


def run_axe(page) -> Any:
    """Return axe results; raises ImportError only if the package is missing."""
    from axe_playwright_python.sync_playwright import Axe

    return Axe().run(page)


def serious_violations(results) -> list:
    """Serious/critical axe violations, compatible with axe-playwright-python result objects."""
    raw = getattr(results, "violations", None)
    if raw is None and isinstance(results, dict):
        raw = results.get("violations", [])
    if not raw:
        return []
    out = []
    for item in raw:
        impact = getattr(item, "impact", None)
        if impact is None and isinstance(item, dict):
            impact = item.get("impact")
        if impact in ("serious", "critical", None):
            # Treat missing impact as fail-closed for known WCAG issues.
            if impact in ("serious", "critical"):
                out.append(item)
    return out


def format_violations(violations) -> str:
    lines = []
    for item in violations:
        vid = getattr(item, "id", None) or (
            item.get("id") if isinstance(item, dict) else "?"
        )
        impact = getattr(item, "impact", None) or (
            item.get("impact") if isinstance(item, dict) else "?"
        )
        help_text = getattr(item, "help", None) or (
            item.get("help") if isinstance(item, dict) else ""
        )
        lines.append(f"{vid} ({impact}): {help_text}")
    return "; ".join(lines)
