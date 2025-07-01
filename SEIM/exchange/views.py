"""
Main views module for the exchange application.
This file maintains backward compatibility with existing imports
while providing better code organization through the views/ package.

All views have been organized into logical modules:
- dashboard_views: Main dashboard functionality
- exchange_views: Exchange CRUD operations
- workflow_views: Status transitions and workflow
- admin_views: Administrative functions
- notification_views: Notification management
- analytics_views: Analytics and reporting
- api_views: DataTables API endpoints and bulk actions
- auth_views: Authentication (API-based)
- batch_views: Batch processing operations
- document_views: Document management
- health_views: Health check endpoints
- template_views: Template-based views and class-based views

Import from this module continues to work as before:
    from exchange.views import dashboard, exchange_list, etc.
"""

# Import all views from the modular structure for backward compatibility
from .views import *
