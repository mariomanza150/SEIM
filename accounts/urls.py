from django.urls import include, path
from rest_framework.routers import DefaultRouter

from frontend.views import password_reset_view

from .views import (
    AppearanceSettingsView,
    ChangePasswordView,
    DeleteAccountView,
    EmailVerificationView,
    LoginView,
    LogoutView,
    NotificationSettingsView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PermissionViewSet,
    PrivacySettingsView,
    ProfileUpdateView,
    ProfileView,
    ProfileViewSet,
    RegistrationView,
    ResendVerificationEmailView,
    RevokeSessionView,
    RoleViewSet,
    UserPermissionsView,
    UserSessionsView,
    UserSessionViewSet,
    UserSettingsView,
    UserViewSet,
)
from .views_dashboard import DashboardStatsView

app_name = "accounts"

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'user-sessions', UserSessionViewSet, basename='user-session')

urlpatterns = [
    # Include ViewSet URLs
    path('api/', include(router.urls)),

    path("register/", RegistrationView.as_view(), name="register"),
    path("verify-email/", EmailVerificationView.as_view(), name="verify-email"),
    path("resend-verification/", ResendVerificationEmailView.as_view(), name="resend_verification"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "password-reset-request/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard_stats"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("password-reset/", password_reset_view, name="password-reset"),

    # Permissions endpoint for frontend
    path("permissions/", UserPermissionsView.as_view(), name="user_permissions"),

    # Settings endpoints
    path("appearance-settings/", AppearanceSettingsView.as_view(), name="appearance_settings"),
    path("notification-settings/", NotificationSettingsView.as_view(), name="notification_settings"),
    path("privacy-settings/", PrivacySettingsView.as_view(), name="privacy_settings"),
    path("user-settings/", UserSettingsView.as_view(), name="user_settings"),
    path("sessions/", UserSessionsView.as_view(), name="sessions"),
    path("sessions/<int:session_id>/revoke/", RevokeSessionView.as_view(), name="revoke_session"),
    path("delete/", DeleteAccountView.as_view(), name="delete_account"),
]
