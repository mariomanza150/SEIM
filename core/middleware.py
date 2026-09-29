"""Request middleware for hot-path query reduction."""

from django.db.models import prefetch_related_objects


class PrefetchUserRolesMiddleware:
    """Load ``request.user.roles`` once so ``has_role`` does not issue EXISTS queries."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            prefetch_related_objects([user], "roles")
        return self.get_response(request)
