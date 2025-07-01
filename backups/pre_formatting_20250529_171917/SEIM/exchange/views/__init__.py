"""
Views package for the exchange application.
Consolidates all view functions and classes from modular view files.
Maintains backward compatibility by importing all view functions.
"""

# Administrative views
from .admin_views import pending_approvals
# Analytics views
from .analytics_views import analytics_view, export_report_view
# API views (DataTables and bulk actions)
from .api_views import (ActivityDataTableView, BulkActionView,
                        DocumentDataTableView, ExchangeDataTableView,
                        PendingApprovalsDataTableView)
# Authentication views (API and template-based)
from .auth_views import (ChangePasswordView, CustomAuthToken, RegisterView,
                         login_view, logout_view, profile_view, update_profile)
# Batch processing views
from .batch_views import (batch_document_verification, batch_notifications,
                          batch_processing, batch_status_update,
                          download_csv_template, export_csv, import_csv)
# Dashboard views
from .dashboard_views import dashboard
# Document management views
from .document_views import (document_detail, document_list, document_list_api,
                             download_document, reject_document,
                             upload_document, verify_document)
# Exchange CRUD views
from .exchange_views import (add_comment, create_exchange, edit_exchange,
                             exchange_detail, exchange_list, exchange_list_api)
# Health check views
from .health_views import health_check
# Notification views
from .notification_views import notification_list, notification_settings
# Template-based views (Class-based and function-based)
from .template_views import (CustomLoginView, CustomLogoutView, HomeView,
                             RegistrationView, create_exchange_view,
                             dashboard_view, exchange_detail_view,
                             exchange_edit_view, exchange_list_view,
                             pending_approvals_view)
# Workflow transition views
from .workflow_views import (approve_exchange, complete_exchange,
                             reject_exchange, review_exchange, submit_exchange)

# Note: Some template_views functions may overlap with other modules.
# In case of conflicts, the original modular versions take precedence.
# profile_view is available in both auth_views and template_views - using auth_views version

# Export all view functions and classes for backward compatibility
__all__ = [
    # Dashboard
    "dashboard",
    # Exchange CRUD
    "exchange_list",
    "exchange_detail",
    "create_exchange",
    "edit_exchange",
    "exchange_list_api",
    "add_comment",
    # Workflow transitions
    "submit_exchange",
    "review_exchange",
    "approve_exchange",
    "reject_exchange",
    "complete_exchange",
    # Administrative
    "pending_approvals",
    # Notifications
    "notification_list",
    "notification_settings",
    # Analytics
    "analytics_view",
    "export_report_view",
    # API views (class-based)
    "ExchangeDataTableView",
    "BulkActionView",
    "DocumentDataTableView",
    "PendingApprovalsDataTableView",
    "ActivityDataTableView",
    # Authentication (API)
    "CustomAuthToken",
    "RegisterView",
    "login_view",
    "logout_view",
    "profile_view",
    "update_profile",
    "ChangePasswordView",
    # Batch processing
    "batch_processing",
    "batch_status_update",
    "batch_document_verification",
    "import_csv",
    "download_csv_template",
    "export_csv",
    "batch_notifications",
    # Document management
    "upload_document",
    "document_list",
    "document_detail",
    "download_document",
    "verify_document",
    "reject_document",
    "document_list_api",
    # Health check
    "health_check",
    # Template-based views (class-based)
    "CustomLoginView",
    "CustomLogoutView",
    "RegistrationView",
    "HomeView",
    # Template-based views (function-based) - these may duplicate existing functions
    "dashboard_view",
    "exchange_list_view",
    "exchange_detail_view",
    "create_exchange_view",
    "exchange_edit_view",
    "pending_approvals_view",
]
