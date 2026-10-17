"""
Environment + role gating for the tester toolkit.

Every tester tool requires ALL of:
  1. ``settings.TESTER_TOOLS_ENABLED`` is true,
  2. ``settings.DEPLOY_TIER`` is ``development`` or ``test``,
  3. the acting tester has ``User.is_tester`` (and is active).

When a tester has switched into a demo account (or a triager is impersonating a
user) the access token carries the original tester id, so reporting still works
and is attributed to the real tester.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model

ALLOWED_TIERS = frozenset({"development", "test"})

# JWT claims added by the demo switcher / impersonation (PR 2).
CLAIM_SWITCHED_FROM = "qa_switched_from"
CLAIM_IMPERSONATOR = "qa_impersonator"


def deploy_tier() -> str:
    return str(getattr(settings, "DEPLOY_TIER", "production") or "production").lower()


def tester_tools_enabled() -> bool:
    """Environment gate (flag + tier). Does not look at the user."""
    return bool(getattr(settings, "TESTER_TOOLS_ENABLED", False)) and (
        deploy_tier() in ALLOWED_TIERS
    )


def _token_claim(request, claim: str):
    token = getattr(request, "auth", None)
    if token is None:
        return None
    getter = getattr(token, "get", None)
    if getter is None:
        return None
    try:
        return getter(claim)
    except Exception:  # pragma: no cover - defensive (non-JWT auth objects)
        return None


def original_actor_id(request):
    """User id of the tester behind a switched/impersonated token, if any."""
    return _token_claim(request, CLAIM_SWITCHED_FROM) or _token_claim(
        request, CLAIM_IMPERSONATOR
    )


def is_impersonating(request) -> bool:
    return bool(original_actor_id(request))


def _active_tester(user) -> bool:
    return bool(
        user is not None
        and getattr(user, "is_authenticated", False)
        and getattr(user, "is_active", False)
        and getattr(user, "is_tester", False)
    )


def get_tester(request):
    """
    Return the real tester behind this request, or ``None``.

    ``None`` whenever the environment gate is closed, so callers can 404.
    """
    if not tester_tools_enabled():
        return None
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    actor_id = original_actor_id(request)
    if actor_id:
        actor = get_user_model().objects.filter(pk=actor_id).first()
        return actor if _active_tester(actor) else None
    return user if _active_tester(user) else None


def is_triager(user) -> bool:
    """Admins triage QA reports (admin role or superuser), never demo accounts."""
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_demo_account", False):
        return False
    return bool(getattr(user, "is_admin", False))


def get_triager(request):
    """Return the tester behind the request when they are also a triager."""
    tester = get_tester(request)
    return tester if is_triager(tester) else None


def assert_not_production(command_name: str) -> None:
    """Refuse demo-data / demo-credential commands on real production."""
    from django.core.management.base import CommandError

    if deploy_tier() == "production":
        raise CommandError(
            f"{command_name} refuses to run with DEPLOY_TIER=production. "
            "Demo accounts and demo data are only for development/test servers."
        )


def demo_password(fallback: str | None = None) -> str:
    """
    Password for seeded demo accounts.

    ``TESTER_DEMO_PASSWORD`` (server env) always wins. Without it, the legacy
    fallback is only allowed on ``development`` (local/CI); on ``test`` the
    command fails so an internet-facing test server never gets known passwords.
    """
    from django.core.management.base import CommandError

    configured = (getattr(settings, "TESTER_DEMO_PASSWORD", "") or "").strip()
    if configured:
        return configured
    if deploy_tier() == "development" and fallback:
        return fallback
    raise CommandError(
        "Set TESTER_DEMO_PASSWORD in the server env file before seeding demo "
        f"accounts on DEPLOY_TIER={deploy_tier()!r}."
    )


def demo_password_is_configured() -> bool:
    return bool((getattr(settings, "TESTER_DEMO_PASSWORD", "") or "").strip())
