from django.contrib import admin

from .models import (
    BulkOperation,
    DataExport,
    DataImport,
    DataOperationLog,
    DataPermission,
    DemoDataSet,
)


def _has_view_permission(user, model_name):
    if user.is_superuser:
        return True
    return DataPermission.objects.filter(
        role__in=user.roles.all(),
        model_name=model_name,
        permission_type='VIEW',
        is_active=True,
    ).exists()


class PermissionFilteredAdmin(admin.ModelAdmin):
    permission_model_name = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if self.permission_model_name and _has_view_permission(request.user, self.permission_model_name):
            return qs
        return qs.none()

@admin.register(DataOperationLog)
class DataOperationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'operation_type', 'model_name', 'user', 'record_count', 'status', 'created_at']
    list_filter = ['operation_type', 'status', 'created_at']
    search_fields = ['model_name', 'operation_details', 'error_message']
    readonly_fields = ['user', 'operation_type', 'model_name', 'record_count', 'operation_details', 'status', 'error_message', 'file_path', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if DataPermission.objects.filter(role__in=request.user.roles.all(), is_active=True).exists():
            return qs.filter(user=request.user)
        return qs.none()

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(BulkOperation)
class BulkOperationAdmin(PermissionFilteredAdmin):
    permission_model_name = 'bulk_operation'
    list_display = ['name', 'operation_type', 'is_active', 'requires_confirmation', 'max_records', 'created_at']
    list_filter = ['operation_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DataExport)
class DataExportAdmin(PermissionFilteredAdmin):
    permission_model_name = 'data_export'
    list_display = ['name', 'model_name', 'format', 'is_active', 'created_by', 'created_at']
    list_filter = ['format', 'is_active']
    search_fields = ['name', 'model_name']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

@admin.register(DataImport)
class DataImportAdmin(PermissionFilteredAdmin):
    permission_model_name = 'data_import'
    list_display = ['name', 'model_name', 'format', 'is_active', 'created_by', 'created_at']
    list_filter = ['format', 'is_active']
    search_fields = ['name', 'model_name']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

@admin.register(DemoDataSet)
class DemoDataSetAdmin(PermissionFilteredAdmin):
    permission_model_name = 'demo_data'
    list_display = ['name', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

@admin.register(DataPermission)
class DataPermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'model_name', 'permission_type', 'is_active']
    list_filter = ['permission_type', 'is_active', 'role']
    search_fields = ['role__name', 'model_name']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser