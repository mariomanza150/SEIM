from django.urls import include, path
from rest_framework.routers import DefaultRouter

from toefl.views import LaunchView, PracticeAttemptViewSet, webhook_view

router = DefaultRouter()
router.register(r"attempts", PracticeAttemptViewSet, basename="toefl-attempt")

urlpatterns = [
    path("launch/", LaunchView.as_view(), name="toefl-launch"),
    path("webhook/", webhook_view, name="toefl-webhook"),
    path("", include(router.urls)),
]
