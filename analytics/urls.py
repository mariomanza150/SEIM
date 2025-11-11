from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'analytics'

router = DefaultRouter()
router.register(r'admindashboard', views.AdminDashboardViewSet, basename='admindashboard')

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('application-statistics/', views.application_statistics_view, name='application_statistics'),
    path('program-statistics/', views.program_statistics_view, name='program_statistics'),
    path('user-activity/', views.user_activity_view, name='user_activity'),
    path('export-data/', views.export_data_view, name='export_data'),
    # API endpoints (stub)
    path('api/application-statistics/', views.api_application_statistics, name='api_application_statistics'),
    path('api/program-statistics/', views.api_program_statistics, name='api_program_statistics'),
    path('api/user-activity/', views.api_user_activity, name='api_user_activity'),
    path('track-event/', views.track_event, name='track_event'),
]

urlpatterns += router.urls
urlpatterns += [
    path('metrics/', views.metrics_view, name='metrics'),
    path('reports/', views.reports_view, name='reports'),
    path('application-analytics/', views.application_analytics_view, name='application-analytics'),
    path('document-analytics/', views.document_analytics_view, name='document-analytics'),
    path('notification-analytics/', views.notification_analytics_view, name='notification-analytics'),
    path('program-analytics/', views.program_analytics_view, name='program-analytics'),
    path('user-analytics/', views.user_analytics_view, name='user-analytics'),
]
