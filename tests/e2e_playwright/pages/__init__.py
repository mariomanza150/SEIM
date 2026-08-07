"""
Page Object Model (POM) for SEIM E2E tests.

This package contains page objects representing major pages in the SEIM application.
"""

from .admin_dashboard_page import AdminDashboardPage
from .analytics_page import AnalyticsPage
from .application_form_page import ApplicationFormPage
from .applications_page import ApplicationsPage
from .auth_page import AuthPage
from .base_page import BasePage
from .coordinator_dashboard_page import CoordinatorDashboardPage
from .dashboard_page import DashboardPage
from .documents_page import DocumentsPage
from .profile_page import ProfilePage
from .programs_page import ProgramsPage
from .settings_page import SettingsPage
from .user_management_page import UserManagementPage

__all__ = [
    "BasePage",
    "AuthPage",
    "DashboardPage",
    "ProgramsPage",
    "ApplicationsPage",
    "ApplicationFormPage",
    "DocumentsPage",
    "ProfilePage",
    "SettingsPage",
    "AdminDashboardPage",
    "CoordinatorDashboardPage",
    "UserManagementPage",
    "AnalyticsPage",
]
