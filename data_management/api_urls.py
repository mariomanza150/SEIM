from django.urls import path

from .api_views import DataManagementCatalogView, DataManagementLogsView

urlpatterns = [
    path("catalog/", DataManagementCatalogView.as_view(), name="catalog"),
    path("logs/", DataManagementLogsView.as_view(), name="logs"),
]
