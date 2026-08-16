from django.urls import path

from .api_views import (
    DataManagementCatalogView,
    DataManagementExecuteView,
    DataManagementLogsView,
    DataManagementResourcesView,
)

urlpatterns = [
    path("catalog/", DataManagementCatalogView.as_view(), name="catalog"),
    path("logs/", DataManagementLogsView.as_view(), name="logs"),
    path("resources/", DataManagementResourcesView.as_view(), name="resources"),
    path("execute/", DataManagementExecuteView.as_view(), name="execute"),
]
