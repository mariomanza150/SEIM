from django.urls import path

from .views import (
    BulkOperationView,
    DataCleanupView,
    DataExportView,
    DataImportView,
    DataManagementIndexView,
    DatabaseResetView,
    DemoDataSetupView,
)

app_name = 'data_management'

urlpatterns = [
    path("", DataManagementIndexView.as_view(), name="index"),
    # Bulk operations
    path('bulk-operations/', BulkOperationView.as_view(), name='bulk_operations'),
    path('bulk-operations/execute/<uuid:operation_id>/', BulkOperationView.as_view(), name='execute_bulk_operation'),

    # Data export
    path('data-export/', DataExportView.as_view(), name='data_exports'),
    path('data-export/execute/<uuid:export_id>/', DataExportView.as_view(), name='execute_export'),

    # Data import
    path('data-import/', DataImportView.as_view(), name='data_imports'),
    path('data-import/execute/<uuid:import_id>/', DataImportView.as_view(), name='execute_import'),

    # Demo data setup
    path('demo-data-setup/', DemoDataSetupView.as_view(), name='demo_data_setup'),
    path('demo-data-setup/execute/<uuid:dataset_id>/', DemoDataSetupView.as_view(), name='execute_demo_setup'),

    # Database reset
    path('database-reset/', DatabaseResetView.as_view(), name='database_reset'),
    path('database-reset/execute/', DatabaseResetView.as_view(), name='execute_database_reset'),

    # Data cleanup
    path('data-cleanup/', DataCleanupView.as_view(), name='data_cleanup'),
    path('data-cleanup/execute/', DataCleanupView.as_view(), name='execute_data_cleanup'),
]