"""
Custom throttling classes for SEIM API.

These throttle classes help prevent abuse and ensure fair resource usage.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """
    Burst rate throttle for high-frequency endpoints.

    Use for endpoints that should have stricter short-term limits
    like login, registration, and password reset.
    """
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    """
    Sustained rate throttle for regular API usage.

    Default throttle for most authenticated endpoints.
    """
    scope = 'user'


class StrictAnonRateThrottle(AnonRateThrottle):
    """
    Strict rate limit for anonymous users.

    Used to prevent abuse from unauthenticated users.
    """
    scope = 'anon'

