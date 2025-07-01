"""API v1 URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExchangeViewSet, DocumentViewSet, CourseViewSet, CommentViewSet, TimelineViewSet, UserProfileViewSet

# Router will be configured when viewsets are moved here
router = DefaultRouter()
router.register(r'exchanges', ExchangeViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'timeline', TimelineViewSet)
router.register(r'userprofiles', UserProfileViewSet)

app_name = "api_v1"

urlpatterns = [
    path("", include(router.urls)),
]
