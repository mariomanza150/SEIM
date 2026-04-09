import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View

from accounts.models import Profile, Role, User

from .models import DataOperationLog, BulkOperation, DataExport, DataImport, DemoDataSet, DataPermission


def _deny_and_redirect(request, message, redirect_name='admin:index'):
    messages.error(request, message)
    return redirect(redirect_name)


def _queue_operation(*, user, operation_type, model_name, operation_details=None, file_path=None):
    return DataOperationLog.objects.create(
        user=user,
        operation_type=operation_type,
        model_name=model_name,
        operation_details=operation_details or {},
        file_path=file_path,
        status='PENDING',
    )


def _normalize_csv_value(value):
    if value is None:
        return ""
    return str(value).strip()


def _derive_username(email, row_number):
    local_part = email.split("@", 1)[0].strip().lower()
    candidate = "".join(char if char.isalnum() or char == "_" else "_" for char in local_part) or f"student_{row_number}"

    if not User.objects.filter(username=candidate).exists():
        return candidate

    suffix = 2
    while User.objects.filter(username=f"{candidate}_{suffix}").exists():
        suffix += 1
    return f"{candidate}_{suffix}"


def _execute_student_import(import_config, uploaded_file, acting_user):
    log = DataOperationLog.objects.create(
        user=acting_user,
        operation_type='IMPORT',
        model_name=import_config.model_name,
        operation_details={
            'source': 'data_management_ui',
            'import_id': str(import_config.id),
            'import_name': import_config.name,
            'format': import_config.format,
            'field_mapping': import_config.field_mapping,
            'validation_rules': import_config.validation_rules,
        },
        file_path=uploaded_file.name,
        status='IN_PROGRESS',
    )

    created_count = 0
    updated_count = 0
    skipped_count = 0
    row_errors = []
    default_password = import_config.validation_rules.get('default_password', 'ChangeMe123!')
    student_role, _ = Role.objects.get_or_create(name='student')

    decoded_file = uploaded_file.read().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(decoded_file))

    with transaction.atomic():
        for row_number, row in enumerate(reader, start=2):
            email = _normalize_csv_value(row.get('email'))
            if not email:
                skipped_count += 1
                row_errors.append(f'Row {row_number}: missing required email value.')
                continue

            username = _normalize_csv_value(row.get('username')) or _derive_username(email, row_number)
            first_name = _normalize_csv_value(row.get('first_name'))
            last_name = _normalize_csv_value(row.get('last_name'))
            language = _normalize_csv_value(row.get('language')) or None
            language_level = _normalize_csv_value(row.get('language_level')) or None
            gpa_value = _normalize_csv_value(row.get('gpa'))

            defaults = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
            }
            user, created = User.objects.get_or_create(email=email, defaults=defaults)

            if created:
                user.set_password(_normalize_csv_value(row.get('password')) or default_password)
                user.save()
                created_count += 1
            else:
                fields_to_update = []
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                    fields_to_update.append('first_name')
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                    fields_to_update.append('last_name')
                if username and user.username != username and not User.objects.filter(username=username).exclude(id=user.id).exists():
                    user.username = username
                    fields_to_update.append('username')
                if fields_to_update:
                    user.save(update_fields=fields_to_update)
                updated_count += 1

            user.roles.add(student_role)

            profile, _ = Profile.objects.get_or_create(user=user)
            profile_updates = []
            if language is not None and profile.language != language:
                profile.language = language
                profile_updates.append('language')
            if language_level is not None and profile.language_level != language_level:
                profile.language_level = language_level
                profile_updates.append('language_level')
            if gpa_value:
                try:
                    parsed_gpa = float(gpa_value)
                except ValueError:
                    skipped_count += 1
                    row_errors.append(f'Row {row_number}: invalid GPA value "{gpa_value}".')
                else:
                    if profile.gpa != parsed_gpa:
                        profile.gpa = parsed_gpa
                        profile_updates.append('gpa')
            if profile_updates:
                profile.save(update_fields=profile_updates)

    log.record_count = created_count + updated_count
    log.status = 'COMPLETED' if not row_errors else 'FAILED'
    log.error_message = "\n".join(row_errors) if row_errors else ""
    log.operation_details.update({
        'created_count': created_count,
        'updated_count': updated_count,
        'skipped_count': skipped_count,
        'errors': row_errors,
    })
    log.save(update_fields=['record_count', 'status', 'error_message', 'operation_details'])
    return log

# Basic permission checking utility
def has_data_permission(user, model_name, permission_type):
    """
    Check if user has specific data permission.
    """
    if user.is_superuser:
        return True

    return DataPermission.objects.filter(
        role__in=user.roles.all(),
        model_name=model_name,
        permission_type=permission_type,
        is_active=True,
    ).exists()


_DATA_MANAGEMENT_SECTIONS = (
    (
        "bulk_operation",
        _("Bulk operations"),
        "data_management:bulk_operations",
        _("Queue bulk updates across models."),
    ),
    (
        "data_export",
        _("Data export"),
        "data_management:data_exports",
        _("Export configured datasets."),
    ),
    (
        "data_import",
        _("Data import"),
        "data_management:data_imports",
        _("Import CSV and other configured sources."),
    ),
    (
        "demo_data",
        _("Demo data setup"),
        "data_management:demo_data_setup",
        _("Load demo datasets for testing."),
    ),
    (
        "database",
        _("Database reset"),
        "data_management:database_reset",
        _("Request a database reset (requires confirmation)."),
    ),
    (
        "data_cleanup",
        _("Data cleanup"),
        "data_management:data_cleanup",
        _("Queue cleanup jobs for orphaned or invalid records."),
    ),
)


class DataManagementIndexView(View):
    """Hub for `/data-management/` when no subpath is given (avoids 404)."""

    @method_decorator(login_required)
    def get(self, request):
        sections = []
        for model_name, title, url_name, description in _DATA_MANAGEMENT_SECTIONS:
            if has_data_permission(request.user, model_name, "VIEW"):
                sections.append(
                    {
                        "title": title,
                        "description": description,
                        "url": reverse(url_name),
                    }
                )
        return render(
            request,
            "data_management/index.html",
            {"sections": sections},
        )


# Basic views
class BulkOperationView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not has_data_permission(request.user, 'bulk_operation', 'VIEW'):
            return _deny_and_redirect(request, "You don't have permission to view bulk operations")

        operations = BulkOperation.objects.filter(is_active=True)
        return render(request, 'data_management/bulk_operations.html', {
            'operations': operations
        })

    @method_decorator(login_required)
    def post(self, request, operation_id):
        if not has_data_permission(request.user, 'bulk_operation', 'UPDATE'):
            return _deny_and_redirect(
                request,
                "You don't have permission to execute bulk operations",
                'data_management:bulk_operations',
            )

        operation = get_object_or_404(BulkOperation.objects.filter(is_active=True), id=operation_id)
        _queue_operation(
            user=request.user,
            operation_type='BULK_UPDATE',
            model_name=operation.operation_type,
            operation_details={
                'source': 'data_management_ui',
                'operation_id': str(operation.id),
                'operation_name': operation.name,
                'requires_confirmation': operation.requires_confirmation,
                'custom_filters': operation.custom_filters,
            },
        )
        messages.success(request, f'Bulk operation "{operation.name}" has been queued.')
        return redirect('data_management:bulk_operations')

class DataExportView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not has_data_permission(request.user, 'data_export', 'VIEW'):
            return _deny_and_redirect(request, "You don't have permission to view data exports")

        exports = DataExport.objects.filter(is_active=True)
        return render(request, 'data_management/data_exports.html', {
            'exports': exports
        })

    @method_decorator(login_required)
    def post(self, request, export_id):
        if not has_data_permission(request.user, 'data_export', 'EXPORT'):
            return _deny_and_redirect(
                request,
                "You don't have permission to export data",
                'data_management:data_exports',
            )

        export_config = get_object_or_404(DataExport.objects.filter(is_active=True), id=export_id)
        _queue_operation(
            user=request.user,
            operation_type='EXPORT',
            model_name=export_config.model_name,
            operation_details={
                'source': 'data_management_ui',
                'export_id': str(export_config.id),
                'export_name': export_config.name,
                'format': export_config.format,
                'include_fields': export_config.include_fields,
                'filters': export_config.filters,
            },
        )
        messages.success(request, f'Export "{export_config.name}" has been queued.')
        return redirect('data_management:data_exports')

class DataImportView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not has_data_permission(request.user, 'data_import', 'VIEW'):
            return _deny_and_redirect(request, "You don't have permission to view data imports")

        imports = DataImport.objects.filter(is_active=True)
        return render(request, 'data_management/data_imports.html', {
            'imports': imports
        })

    @method_decorator(login_required)
    def post(self, request, import_id):
        if not has_data_permission(request.user, 'data_import', 'IMPORT'):
            return _deny_and_redirect(
                request,
                "You don't have permission to import data",
                'data_management:data_imports',
            )

        import_config = get_object_or_404(DataImport.objects.filter(is_active=True), id=import_id)
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return _deny_and_redirect(
                request,
                'Please choose a file to import.',
                'data_management:data_imports',
            )

        if import_config.model_name == 'accounts.user' and import_config.format == 'CSV':
            log = _execute_student_import(import_config, uploaded_file, request.user)
            if log.status == 'COMPLETED':
                messages.success(
                    request,
                    f'Student import completed. Created {log.operation_details["created_count"]} and updated {log.operation_details["updated_count"]} records.',
                )
            else:
                messages.warning(
                    request,
                    f'Student import completed with issues. Imported {log.record_count} records; review the operation log for skipped rows.',
                )
            return redirect('data_management:data_imports')

        _queue_operation(
            user=request.user,
            operation_type='IMPORT',
            model_name=import_config.model_name,
            operation_details={
                'source': 'data_management_ui',
                'import_id': str(import_config.id),
                'import_name': import_config.name,
                'format': import_config.format,
                'field_mapping': import_config.field_mapping,
                'validation_rules': import_config.validation_rules,
            },
            file_path=uploaded_file.name,
        )
        messages.success(request, f'Import "{import_config.name}" has been queued.')
        return redirect('data_management:data_imports')

class DemoDataSetupView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not has_data_permission(request.user, 'demo_data', 'VIEW'):
            return _deny_and_redirect(request, "You don't have permission to view demo data setup")

        datasets = DemoDataSet.objects.filter(is_active=True)
        return render(request, 'data_management/demo_data_setup.html', {
            'datasets': datasets
        })

    @method_decorator(login_required)
    def post(self, request, dataset_id):
        if not has_data_permission(request.user, 'demo_data', 'CREATE'):
            return _deny_and_redirect(
                request,
                "You don't have permission to set up demo data",
                'data_management:demo_data_setup',
            )

        dataset = get_object_or_404(DemoDataSet.objects.filter(is_active=True), id=dataset_id)
        _queue_operation(
            user=request.user,
            operation_type='DEMO_SETUP',
            model_name='demo_data',
            operation_details={
                'source': 'data_management_ui',
                'dataset_id': str(dataset.id),
                'dataset_name': dataset.name,
                'data_config': dataset.data_config,
            },
        )
        messages.success(request, f'Demo data setup "{dataset.name}" has been queued.')
        return redirect('data_management:demo_data_setup')

class DatabaseResetView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not has_data_permission(request.user, 'database', 'VIEW'):
            return _deny_and_redirect(request, "You don't have permission to view database reset")

        return render(request, 'data_management/database_reset.html', {})

    @method_decorator(login_required)
    def post(self, request):
        if not has_data_permission(request.user, 'database', 'DELETE'):
            return _deny_and_redirect(
                request,
                "You don't have permission to reset the database",
                'data_management:database_reset',
            )

        if request.POST.get('confirm') != 'RESET':
            return _deny_and_redirect(
                request,
                "Type 'RESET' to confirm the database reset request.",
                'data_management:database_reset',
            )

        _queue_operation(
            user=request.user,
            operation_type='DB_RESET',
            model_name='database',
            operation_details={
                'source': 'data_management_ui',
                'confirmed': True,
            },
        )
        messages.success(request, 'Database reset has been queued for review.')
        return redirect('data_management:database_reset')

class DataCleanupView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not has_data_permission(request.user, 'data_cleanup', 'VIEW'):
            return _deny_and_redirect(request, "You don't have permission to view data cleanup")

        return render(request, 'data_management/data_cleanup.html', {})

    @method_decorator(login_required)
    def post(self, request):
        if not has_data_permission(request.user, 'data_cleanup', 'DELETE'):
            return _deny_and_redirect(
                request,
                "You don't have permission to clean data",
                'data_management:data_cleanup',
            )

        selected_operations = {
            'clean_orphaned': request.POST.get('clean_orphaned') == 'on',
            'clean_duplicates': request.POST.get('clean_duplicates') == 'on',
            'clean_invalid': request.POST.get('clean_invalid') == 'on',
        }
        if not any(selected_operations.values()):
            return _deny_and_redirect(
                request,
                'Select at least one cleanup operation.',
                'data_management:data_cleanup',
            )

        _queue_operation(
            user=request.user,
            operation_type='CLEANUP',
            model_name='data_cleanup',
            operation_details={
                'source': 'data_management_ui',
                'cleanup_options': selected_operations,
            },
        )
        messages.success(request, 'Data cleanup has been queued.')
        return redirect('data_management:data_cleanup')