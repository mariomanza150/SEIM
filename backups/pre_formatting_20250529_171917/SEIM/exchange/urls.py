from django.urls import path

from . import views

app_name = "exchange"

urlpatterns = [
    # Main views
    path("", views.dashboard, name="dashboard"),
    path("exchanges/", views.exchange_list, name="exchange-list"),
    path("exchanges/create/", views.create_exchange, name="create-exchange"),
    path("exchanges/<int:pk>/", views.exchange_detail, name="exchange-detail"),
    path("exchanges/<int:pk>/edit/", views.edit_exchange, name="edit-exchange"),
    path("exchanges/<int:pk>/documents/", views.document_list, name="document-list"),
    path(
        "exchanges/<int:pk>/documents/<int:doc_id>/",
        views.document_detail,
        name="document-detail",
    ),
    path("exchanges/pending/", views.pending_approvals, name="pending-approvals"),
    # Document uploads
    path(
        "exchanges/<int:pk>/upload-document/",
        views.upload_document,
        name="upload-document",
    ),
    path(
        "documents/<int:pk>/download/",
        views.download_document,
        name="download-document",
    ),
    path("documents/<int:pk>/verify/", views.verify_document, name="verify-document"),
    path("documents/<int:pk>/reject/", views.reject_document, name="reject-document"),
    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.profile_view, name="profile"),
    # Workflow actions
    path("exchanges/<int:pk>/submit/", views.submit_exchange, name="submit-exchange"),
    path(
        "exchanges/<int:pk>/approve/", views.approve_exchange, name="approve-exchange"
    ),
    path("exchanges/<int:pk>/reject/", views.reject_exchange, name="reject-exchange"),
    path("exchanges/<int:pk>/review/", views.review_exchange, name="review-exchange"),
    path("exchanges/<int:pk>/add-comment/", views.add_comment, name="add-comment"),
    path(
        "exchanges/<int:pk>/complete/",
        views.complete_exchange,
        name="complete-exchange",
    ),
    # Notifications
    path("notifications/", views.notification_list, name="notification-list"),
    path(
        "notifications/settings/",
        views.notification_settings,
        name="notification-settings",
    ),
    # Analytics and reporting
    path("analytics/", views.analytics_view, name="analytics"),
    path("reports/export/", views.export_report_view, name="export-report"),
    # Batch processing
    path("batch/", views.batch_processing, name="batch-processing"),
    path("batch/status-update/", views.batch_status_update, name="batch-status-update"),
    path(
        "batch/document-verification/",
        views.batch_document_verification,
        name="batch-document-verification",
    ),
    path("batch/import-csv/", views.import_csv, name="import-csv"),
    path("batch/export-csv/", views.export_csv, name="export-csv"),
    path(
        "batch/download-csv-template/",
        views.download_csv_template,
        name="download-csv-template",
    ),
    path(
        "batch/send-notifications/",
        views.batch_notifications,
        name="batch-notifications",
    ),
    # API endpoints for AJAX
    path("api/exchanges/", views.exchange_list_api, name="exchange-list-api"),
    path("api/documents/", views.document_list_api, name="document-list-api"),
    # DataTables API endpoints
    path(
        "api/exchanges/datatable/",
        views.ExchangeDataTableView.as_view(),
        name="exchanges-datatable",
    ),
    path(
        "api/documents/datatable/",
        views.DocumentDataTableView.as_view(),
        name="documents-datatable",
    ),
    path(
        "api/pending-approvals/datatable/",
        views.PendingApprovalsDataTableView.as_view(),
        name="pending-approvals-datatable",
    ),
    path(
        "api/activity/datatable/",
        views.ActivityDataTableView.as_view(),
        name="activity-datatable",
    ),
    # Bulk Actions
    path("api/bulk-action/", views.BulkActionView.as_view(), name="bulk-action"),
    # Health check
    path("health/", views.health_check, name="health-check"),
    # API Authentication
    path("api/auth/token/", views.CustomAuthToken.as_view(), name="api-token-auth"),
    path("api/auth/register/", views.RegisterView.as_view(), name="api-register"),
    path("api/auth/logout/", views.logout_view, name="api-logout"),
    path("api/auth/profile/", views.update_profile, name="update-profile"),
    path(
        "api/auth/change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password",
    ),
]
