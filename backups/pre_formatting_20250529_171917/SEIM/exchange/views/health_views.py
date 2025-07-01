import time

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Basic health check endpoint for monitoring and load balancers
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Check for other services if needed
        # redis_check = cache.get('health_check_key') is not None

        return JsonResponse(
            {
                "status": "healthy",
                "timestamp": time.time(),
                "database": "connected",
                "version": "1.0.0",
            },
            status=200,
        )

    except Exception as e:
        return JsonResponse(
            {"status": "unhealthy", "timestamp": time.time(), "error": str(e)},
            status=503,
        )
