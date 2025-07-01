"""API v1 URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Router will be configured when viewsets are moved here
router = DefaultRouter()

app_name = "api_v1"

urlpatterns = [
    path("", include(router.urls)),
]
