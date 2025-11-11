"""URL configuration for grades app."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GradeScaleViewSet, GradeTranslationViewSet, GradeValueViewSet

app_name = 'grades'

# Create router for API endpoints
router = DefaultRouter()
router.register(r'scales', GradeScaleViewSet, basename='gradescale')
router.register(r'values', GradeValueViewSet, basename='gradevalue')
router.register(r'translations', GradeTranslationViewSet, basename='gradetranslation')

urlpatterns = [
    path('api/', include(router.urls)),
]

