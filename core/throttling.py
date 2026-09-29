"""
Custom throttling classes for SEIM API.

These throttle classes help prevent abuse and ensure fair resource usage.
"""

from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle, UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """
    Burst rate throttle for high-frequency endpoints.

    Use for endpoints that should have stricter short-term limits
    like login, registration, and password reset.
    """

    scope = "burst"


class ResendVerificationEmailThrottle(SimpleRateThrottle):
    """
    IP burst safety net for resend-verification.

    Authoritative per-email cooldown lives in accounts.resend_verification
    (1 request / 5 minutes) and is applied inside the view after verifying
    the account is unverified.
    """

    scope = "resend_verification"

    def get_cache_key(self, request, view):
        # Fall back to IP when anonymous (typical for this endpoint).
        ident = self.get_ident(request)
        if not ident:
            return None
        return self.cache_format % {"scope": self.scope, "ident": ident}


class SustainedRateThrottle(UserRateThrottle):
    """
    Sustained rate throttle for regular API usage.

    Default throttle for most authenticated endpoints.
    """

    scope = "user"


class StrictAnonRateThrottle(AnonRateThrottle):
    """
    Strict rate limit for anonymous users.

    Used to prevent abuse from unauthenticated users.
    """

    scope = "anon"
