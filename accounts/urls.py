from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicLevelViewSet,
    AllowedEmailDomainViewSet,
    AppearanceSettingsView,
    BankInstitutionViewSet,
    ChangePasswordView,
    CountryCatalogView,
    DeleteAccountView,
    EmailVerificationView,
    HomeAcademicProgramViewSet,
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
    SchoolFacultyViewSet,
    SpokenLanguageViewSet,
    UnidadViewSet,
    UserPermissionsView,
    UserSessionsView,
    UserSessionViewSet,
    UserSettingsView,
    UserViewSet,
)
from .views_dashboard import CoordinatorWorkloadView, DashboardStatsView

app_name = "accounts"

# Create router for ViewSets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"user-sessions", UserSessionViewSet, basename="user-session")

catalog_router = DefaultRouter()
catalog_router.register(
    r"allowed-email-domains",
    AllowedEmailDomainViewSet,
    basename="allowed-email-domain",
)
catalog_router.register(
    r"academic-levels", AcademicLevelViewSet, basename="academic-level"
)
catalog_router.register(r"schools", SchoolFacultyViewSet, basename="school")
catalog_router.register(r"unidades", UnidadViewSet, basename="unidad")
catalog_router.register(
    r"programs", HomeAcademicProgramViewSet, basename="home-program"
)
catalog_router.register(r"banks", BankInstitutionViewSet, basename="bank")
catalog_router.register(
    r"spoken-languages", SpokenLanguageViewSet, basename="spoken-language"
)

urlpatterns = [
    # Include ViewSet URLs
    path("api/", include(router.urls)),
    path("catalogs/countries/", CountryCatalogView.as_view(), name="catalog-countries"),
    path("catalogs/", include(catalog_router.urls)),
    path("register/", RegistrationView.as_view(), name="register"),
    path("verify-email/", EmailVerificationView.as_view(), name="verify-email"),
    path(
        "resend-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend_verification",
    ),
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
    path(
        "dashboard/coordinator-workload/",
        CoordinatorWorkloadView.as_view(),
        name="coordinator_workload",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset",
    ),
    # Permissions endpoint for frontend
    path("permissions/", UserPermissionsView.as_view(), name="user_permissions"),
    # Settings endpoints
    path(
        "appearance-settings/",
        AppearanceSettingsView.as_view(),
        name="appearance_settings",
    ),
    path(
        "notification-settings/",
        NotificationSettingsView.as_view(),
        name="notification_settings",
    ),
    path("privacy-settings/", PrivacySettingsView.as_view(), name="privacy_settings"),
    path("user-settings/", UserSettingsView.as_view(), name="user_settings"),
    path("sessions/", UserSessionsView.as_view(), name="sessions"),
    path(
        "sessions/<int:session_id>/revoke/",
        RevokeSessionView.as_view(),
        name="revoke_session",
    ),
    path("delete/", DeleteAccountView.as_view(), name="delete_account"),
]
