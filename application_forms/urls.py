"""
Application Forms URLs

API endpoints for form types and submissions.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'application_forms'

router = DefaultRouter()
router.register(r'form-types', views.FormTypeViewSet, basename='formtype')
router.register(r'step-templates', views.FormStepTemplateViewSet, basename='formsteptemplate')
router.register(r'submissions', views.FormSubmissionViewSet, basename='formsubmission')

urlpatterns = [
    path('', include(router.urls)),
    # Form list view
    path('list/', views.FormTypeListView.as_view(), name='form-list'),
    # Enhanced form builder
    path('builder/', views.EnhancedFormBuilderView.as_view(), name='enhanced-builder'),
    path('builder/<int:pk>/', views.EnhancedFormBuilderView.as_view(), name='enhanced-builder-edit'),
]

