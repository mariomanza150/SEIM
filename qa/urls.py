from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IssueViewSet, QAContextView

router = DefaultRouter()
router.register("issues", IssueViewSet, basename="qa-issue")

urlpatterns = [
    path("context/", QAContextView.as_view(), name="qa-context"),
    path("", include(router.urls)),
]
