from django.conf import settings
from django.db import models
from core.models import UUIDModel, TimeStampedModel

class DataOperationLog(UUIDModel, TimeStampedModel):
    """
    Log of all data operations performed through the data management system.
    """
    OPERATION_TYPES = [
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('BULK_UPDATE', 'Bulk Update'),
        ('BULK_DELETE', 'Bulk Delete'),
        ('DEMO_SETUP', 'Demo Setup'),
        ('DB_RESET', 'Database Reset'),
        ('CLEANUP', 'Cleanup'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='data_operations')
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    model_name = models.CharField(max_length=100)
    record_count = models.IntegerField(default=0)
    operation_details = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default='PENDING', choices=[
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ])
    error_message = models.TextField(blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_operation_type_display()} - {self.model_name} - {self.status}"

class BulkOperation(UUIDModel, TimeStampedModel):
    """
    Definition of bulk operations that can be performed.
    """
    OPERATION_TYPES = [
        ('USER_IMPORT', 'User Import'),
        ('USER_EXPORT', 'User Export'),
        ('USER_RESET_PASSWORDS', 'Reset User Passwords'),
        ('USER_DEACTIVATE', 'Deactivate Users'),
        ('PROGRAM_IMPORT', 'Program Import'),
        ('PROGRAM_EXPORT', 'Program Export'),
        ('APPLICATION_PROCESS', 'Process Applications'),
        ('DEMO_DATA_SETUP', 'Setup Demo Data'),
        ('DATABASE_RESET', 'Reset Database'),
        ('DATA_CLEANUP', 'Cleanup Data'),
    ]

    name = models.CharField(max_length=200)
    operation_type = models.CharField(max_length=50, choices=OPERATION_TYPES)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    requires_confirmation = models.BooleanField(default=True)
    max_records = models.IntegerField(default=0)  # 0 = no limit
    allowed_roles = models.JSONField(default=list)  # List of role names allowed to perform
    custom_filters = models.JSONField(default=dict)  # Custom filters for the operation

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class DataExport(UUIDModel, TimeStampedModel):
    """
    Configuration for data exports.
    """
    EXPORT_FORMATS = [
        ('JSON', 'JSON'),
        ('CSV', 'CSV'),
        ('EXCEL', 'Excel'),
    ]

    name = models.CharField(max_length=200)
    model_name = models.CharField(max_length=100)
    format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    include_fields = models.JSONField(default=list)
    filters = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='data_exports')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_format_display()})"

class DataImport(UUIDModel, TimeStampedModel):
    """
    Configuration for data imports.
    """
    IMPORT_FORMATS = [
        ('JSON', 'JSON'),
        ('CSV', 'CSV'),
        ('EXCEL', 'Excel'),
    ]

    name = models.CharField(max_length=200)
    model_name = models.CharField(max_length=100)
    format = models.CharField(max_length=10, choices=IMPORT_FORMATS)
    field_mapping = models.JSONField(default=dict)
    validation_rules = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='data_imports')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_format_display()})"

class DemoDataSet(UUIDModel, TimeStampedModel):
    """
    Configuration for demo data sets.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    data_config = models.JSONField(default=dict)  # Configuration for generating demo data
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='demo_data_sets')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class DataPermission(UUIDModel, TimeStampedModel):
    """
    Granular data permissions for users and roles.
    """
    PERMISSION_TYPES = [
        ('VIEW', 'View'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
    ]

    role = models.ForeignKey('accounts.Role', on_delete=models.CASCADE, related_name='data_permissions')
    model_name = models.CharField(max_length=100)
    permission_type = models.CharField(max_length=10, choices=PERMISSION_TYPES)
    custom_filters = models.JSONField(default=dict)  # Custom filters for this permission
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['role', 'model_name', 'permission_type']
        ordering = ['role__name', 'model_name']

    def __str__(self):
        return f"{self.role.name} - {self.model_name} - {self.get_permission_type_display()}"