from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.jwt_views import CustomTokenObtainPairView

from accounts.views import (
    EmailVerificationView,
    LoginView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PermissionViewSet,
    ProfileViewSet,
    RegistrationView,
    RoleViewSet,
    UserSessionViewSet,
    UserSettingsView,
    UserViewSet,
)
from analytics.views import (
    AdminDashboardViewSet,
    DashboardConfigViewSet,
    MetricViewSet,
    ReportViewSet,
    analytics_dashboard_api,
    analytics_export_api,
    analytics_report_detail_api,
)
from documents.views import (
    DocumentCommentViewSet,
    DocumentResubmissionRequestViewSet,
    DocumentTypeViewSet,
    DocumentValidationViewSet,
    DocumentViewSet,
    ExchangeAgreementDocumentViewSet,
)
from exchange.views import (
    ApplicationStatusViewSet,
    ApplicationViewSet,
    CalendarEventViewSet,
    CommentViewSet,
    ExchangeAgreementViewSet,
    ProgramViewSet,
    SavedSearchViewSet,
    TimelineEventViewSet,
    calendar_subscribe_ics,
)
from notifications.views import (
    NotificationPreferenceViewSet,
    NotificationTypeViewSet,
    NotificationViewSet,
    ReminderViewSet,
)

router = routers.DefaultRouter()

# Accounts
router.register(r"users", UserViewSet)
router.register(r"profiles", ProfileViewSet)
router.register(r"roles", RoleViewSet)
router.register(r"permissions", PermissionViewSet)
router.register(r"user-sessions", UserSessionViewSet, basename="user-sessions")

# Exchange
router.register(r"programs", ProgramViewSet)
router.register(
    r"exchange-agreements",
    ExchangeAgreementViewSet,
    basename="exchange-agreement",
)
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"application-statuses", ApplicationStatusViewSet)
router.register(r"comments", CommentViewSet)
router.register(r"timeline-events", TimelineEventViewSet)
router.register(r"saved-searches", SavedSearchViewSet, basename="saved-search")
router.register(r"calendar/events", CalendarEventViewSet, basename="calendar-event")

# Documents
router.register(r"document-types", DocumentTypeViewSet)
router.register(r"documents", DocumentViewSet)
router.register(r"document-validations", DocumentValidationViewSet)
router.register(r"document-resubmissions", DocumentResubmissionRequestViewSet)
router.register(r"document-comments", DocumentCommentViewSet)
router.register(
    r"agreement-documents",
    ExchangeAgreementDocumentViewSet,
    basename="agreement-document",
)

# Notifications
router.register(r"notification-types", NotificationTypeViewSet)
router.register(r"notifications", NotificationViewSet)
router.register(r"notification-preferences", NotificationPreferenceViewSet)
router.register(r"reminders", ReminderViewSet, basename="reminder")

# Analytics
router.register(r"reports", ReportViewSet)
router.register(r"metrics", MetricViewSet)
router.register(r"dashboard-configs", DashboardConfigViewSet)
router.register(r"admin/dashboard", AdminDashboardViewSet, basename="admin-dashboard")

urlpatterns = [
    path(
        "calendar/subscribe.ics",
        calendar_subscribe_ics,
        name="calendar-subscribe-ics",
    ),
    path("", include(router.urls)),
    path("analytics/dashboard/", analytics_dashboard_api, name="analytics-dashboard"),
    path("analytics/export/", analytics_export_api, name="analytics-export"),
    path("analytics/reports/<str:report_type>/", analytics_report_detail_api, name="analytics-report-detail"),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("password-reset-request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("email-verification/", EmailVerificationView.as_view(), name="email-verification"),
    path("user-settings/", UserSettingsView.as_view(), name="user-settings"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
