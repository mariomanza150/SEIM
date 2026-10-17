from django.conf import settings
from django.core.checks import Error, Tags, register

from .gating import ALLOWED_TIERS, deploy_tier


@register(Tags.security, deploy=True)
@register(Tags.security)
def tester_tools_not_in_production(app_configs, **kwargs):
    """Refuse to run with tester tools switched on outside dev/test tiers."""
    if getattr(settings, "TESTER_TOOLS_ENABLED", False) and (
        deploy_tier() not in ALLOWED_TIERS
    ):
        return [
            Error(
                f"TESTER_TOOLS_ENABLED is true but DEPLOY_TIER={deploy_tier()!r}.",
                hint=(
                    "Tester tools (demo logins, impersonation, email capture) must "
                    "never run in production. Unset TESTER_TOOLS_ENABLED or set "
                    "DEPLOY_TIER=test on test servers."
                ),
                id="qa.E001",
            )
        ]
    backend = getattr(settings, "EMAIL_BACKEND", "")
    if backend.startswith("qa.") and deploy_tier() not in ALLOWED_TIERS:
        return [
            Error(
                f"EMAIL_BACKEND={backend!r} captures mail but DEPLOY_TIER={deploy_tier()!r}.",
                hint="Use a real email backend in production.",
                id="qa.E002",
            )
        ]
    return []
