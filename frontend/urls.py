from django.urls import path

from . import views
from .views import program_create_view

app_name = "frontend"

urlpatterns = [
    # Main pages
    path("", views.home_view, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # Authentication pages
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("password-reset/", views.password_reset_view, name="password_reset"),
    # Application pages
    path("programs/", views.programs_view, name="programs"),
    path("applications/", views.applications_view, name="applications"),
    path(
        "applications/create/", views.application_create_view, name="application_create"
    ),
    path(
        "applications/<uuid:pk>/",
        views.application_detail_view,
        name="application_detail",
    ),
    path(
        "applications/<uuid:pk>/edit/",
        views.application_edit_view,
        name="application_edit",
    ),
    # User pages
    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.settings_view, name="settings"),
    # Admin pages
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("analytics/", views.AnalyticsView.as_view(), name="analytics"),
    path("programs/create/", program_create_view, name="program_create"),
    # Cache management
    path("cache/invalidate/", views.invalidate_user_cache, name="invalidate_cache"),
    path("cache/clear/", views.clear_cache_view, name="clear_cache"),
    # Test pages
    path("dark-mode-test/", views.dark_mode_test_view, name="dark_mode_test"),
    path("debug-theme/", views.debug_theme_view, name="debug_theme"),
    path("theme-test/", views.theme_test_view, name="theme_test"),
    path("theme-debug/", views.theme_debug_view, name="theme_debug"),
    path(
        "theme-feedback-test/",
        views.theme_feedback_test_view,
        name="theme_feedback_test",
    ),
    # Documents placeholder for tests
    path("documents/", views.documents_list_view, name="documents_list"),
]
