"""Virus scanner settings helpers (fail-closed outside development/test)."""

from __future__ import annotations

import logging
import os

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

_DEV_TEST_TIERS = frozenset({"development", "test", "dev"})
_REAL_SCANNER_TYPES = frozenset({"clamav", "clamav_cli"})
_ALLOWED_TYPES = _REAL_SCANNER_TYPES | {"mock"}


def mock_virus_scanner_allowed(
    *,
    deploy_tier: str,
    allow_mock: bool = False,
) -> bool:
    """Return True when the mock scanner is permitted for this tier."""
    tier = (deploy_tier or "").strip().lower()
    if tier in _DEV_TEST_TIERS:
        return True
    return bool(allow_mock)


def resolve_virus_scanner_type(
    *,
    deploy_tier: str,
    environ: dict[str, str] | None = None,
) -> str:
    """Resolve VIRUS_SCANNER_TYPE for the active deploy tier.

    Development/test: default ``mock`` when unset.
    Production-like: require an explicit value; ``mock`` only with
    ``VIRUS_SCANNER_ALLOW_MOCK=1`` (logged at CRITICAL).
    """
    env = environ if environ is not None else os.environ
    tier = (deploy_tier or "").strip().lower()
    raw = (env.get("VIRUS_SCANNER_TYPE") or "").strip().lower()
    allow_mock = (env.get("VIRUS_SCANNER_ALLOW_MOCK") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )

    if not raw:
        if mock_virus_scanner_allowed(deploy_tier=tier, allow_mock=False):
            return "mock"
        raise ImproperlyConfigured(
            "VIRUS_SCANNER_TYPE must be set on production-like tiers "
            "(e.g. clamav or clamav_cli). The mock scanner is not the "
            "default outside development/test. To force mock, set "
            "VIRUS_SCANNER_TYPE=mock and VIRUS_SCANNER_ALLOW_MOCK=1."
        )

    if raw not in _ALLOWED_TYPES:
        raise ImproperlyConfigured(
            f"Unknown VIRUS_SCANNER_TYPE={raw!r}. "
            f"Expected one of: {', '.join(sorted(_ALLOWED_TYPES))}."
        )

    if raw == "mock" and not mock_virus_scanner_allowed(
        deploy_tier=tier, allow_mock=allow_mock
    ):
        raise ImproperlyConfigured(
            "VIRUS_SCANNER_TYPE=mock is not allowed on production-like "
            "tiers without VIRUS_SCANNER_ALLOW_MOCK=1."
        )

    if raw == "mock" and tier not in _DEV_TEST_TIERS:
        logger.critical(
            "VIRUS_SCANNER_TYPE=mock is active on deploy tier %r "
            "(VIRUS_SCANNER_ALLOW_MOCK=1). Uploads are not scanned by ClamAV.",
            tier,
        )

    return raw
