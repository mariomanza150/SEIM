"""
Page Object Model (POM) for SEIM E2E tests.

This package contains page objects representing major pages in the SEIM application.
"""

from .base_page import BasePage
from .auth_page import AuthPage
from .dashboard_page import DashboardPage
from .programs_page import ProgramsPage
from .applications_page import ApplicationsPage
from .application_form_page import ApplicationFormPage
from .documents_page import DocumentsPage
from .profile_page import ProfilePage
from .settings_page import SettingsPage
from .admin_dashboard_page import AdminDashboardPage
from .coordinator_dashboard_page import CoordinatorDashboardPage
from .user_management_page import UserManagementPage
from .analytics_page import AnalyticsPage

__all__ = [
    'BasePage',
    'AuthPage',
    'DashboardPage',
    'ProgramsPage',
    'ApplicationsPage',
    'ApplicationFormPage',
    'DocumentsPage',
    'ProfilePage',
    'SettingsPage',
    'AdminDashboardPage',
    'CoordinatorDashboardPage',
    'UserManagementPage',
    'AnalyticsPage',
]

