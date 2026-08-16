"""Shared data-management list/execute helpers for Django views and the SPA API."""

import csv
import io

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile, Role, User

from .models import (
    BulkOperation,
    DataExport,
    DataImport,
    DataOperationLog,
    DataPermission,
    DemoDataSet,
)

SPA_DATA_MANAGEMENT = "/seim/admin/data-management"

EXECUTE_PERMISSIONS = {
    "bulk_operation": "UPDATE",
    "data_export": "EXPORT",
    "data_import": "IMPORT",
    "demo_data": "CREATE",
    "database": "DELETE",
    "data_cleanup": "DELETE",
}

SECTION_MODELS = {
    "bulk_operation": BulkOperation,
    "data_export": DataExport,
    "data_import": DataImport,
    "demo_data": DemoDataSet,
}

_DATA_MANAGEMENT_SECTIONS = (
    (
        "bulk_operation",
        _("Bulk operations"),
        _("Queue bulk updates across models."),
    ),
    (
        "data_export",
        _("Data export"),
        _("Export configured datasets."),
    ),
    (
        "data_import",
        _("Data import"),
        _("Import CSV and other configured sources."),
    ),
    (
        "demo_data",
        _("Demo data setup"),
        _("Load demo datasets for testing."),
    ),
    (
        "database",
        _("Database reset"),
        _("Request a database reset (requires confirmation)."),
    ),
    (
        "data_cleanup",
        _("Data cleanup"),
        _("Queue cleanup jobs for orphaned or invalid records."),
    ),
)


class DataManagementError(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code
        super().__init__(message)


def spa_section_url(section=None):
    if section:
        return f"{SPA_DATA_MANAGEMENT}?section={section}"
    return SPA_DATA_MANAGEMENT


def has_data_permission(user, model_name, permission_type):
    if user.is_superuser:
        return True

    return DataPermission.objects.filter(
        role__in=user.roles.all(),
        model_name=model_name,
        permission_type=permission_type,
        is_active=True,
    ).exists()


def data_management_catalog(user):
    """Sections the current user may open (SPA catalog; Django pages redirect here)."""
    sections = []
    for model_name, title, description in _DATA_MANAGEMENT_SECTIONS:
        if has_data_permission(user, model_name, "VIEW"):
            sections.append(
                {
                    "key": model_name,
                    "title": str(title),
                    "description": str(description),
                    "url": spa_section_url(model_name),
                }
            )
    return sections


def queue_operation(
    *, user, operation_type, model_name, operation_details=None, file_path=None
):
    return DataOperationLog.objects.create(
        user=user,
        operation_type=operation_type,
        model_name=model_name,
        operation_details=operation_details or {},
        file_path=file_path,
        status="PENDING",
    )


def _normalize_csv_value(value):
    if value is None:
        return ""
    return str(value).strip()


def _derive_username(email, row_number):
    local_part = email.split("@", 1)[0].strip().lower()
    candidate = (
        "".join(char if char.isalnum() or char == "_" else "_" for char in local_part)
        or f"student_{row_number}"
    )

    if not User.objects.filter(username=candidate).exists():
        return candidate

    suffix = 2
    while User.objects.filter(username=f"{candidate}_{suffix}").exists():
        suffix += 1
    return f"{candidate}_{suffix}"


def execute_student_import(
    import_config, uploaded_file, acting_user, source="data_management_ui"
):
    log = DataOperationLog.objects.create(
        user=acting_user,
        operation_type="IMPORT",
        model_name=import_config.model_name,
        operation_details={
            "source": source,
            "import_id": str(import_config.id),
            "import_name": import_config.name,
            "format": import_config.format,
            "field_mapping": import_config.field_mapping,
            "validation_rules": import_config.validation_rules,
        },
        file_path=uploaded_file.name,
        status="IN_PROGRESS",
    )

    created_count = 0
    updated_count = 0
    skipped_count = 0
    row_errors = []
    default_password = import_config.validation_rules.get(
        "default_password", "ChangeMe123!"
    )
    student_role, _ = Role.objects.get_or_create(name="student")

    decoded_file = uploaded_file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded_file))

    with transaction.atomic():
        for row_number, row in enumerate(reader, start=2):
            email = _normalize_csv_value(row.get("email"))
            if not email:
                skipped_count += 1
                row_errors.append(f"Row {row_number}: missing required email value.")
                continue

            username = _normalize_csv_value(row.get("username")) or _derive_username(
                email, row_number
            )
            first_name = _normalize_csv_value(row.get("first_name"))
            last_name = _normalize_csv_value(row.get("last_name"))
            language = _normalize_csv_value(row.get("language")) or None
            language_level = _normalize_csv_value(row.get("language_level")) or None
            gpa_value = _normalize_csv_value(row.get("gpa"))

            defaults = {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            }
            user, created = User.objects.get_or_create(email=email, defaults=defaults)

            if created:
                user.set_password(
                    _normalize_csv_value(row.get("password")) or default_password
                )
                user.save()
                created_count += 1
            else:
                fields_to_update = []
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                    fields_to_update.append("first_name")
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                    fields_to_update.append("last_name")
                if (
                    username
                    and user.username != username
                    and not User.objects.filter(username=username)
                    .exclude(id=user.id)
                    .exists()
                ):
                    user.username = username
                    fields_to_update.append("username")
                if fields_to_update:
                    user.save(update_fields=fields_to_update)
                updated_count += 1

            user.roles.add(student_role)

            profile, _ = Profile.objects.get_or_create(user=user)
            profile_updates = []
            if language is not None and profile.language != language:
                profile.language = language
                profile_updates.append("language")
            if language_level is not None and profile.language_level != language_level:
                profile.language_level = language_level
                profile_updates.append("language_level")
            if gpa_value:
                try:
                    parsed_gpa = float(gpa_value)
                except ValueError:
                    skipped_count += 1
                    row_errors.append(
                        f'Row {row_number}: invalid GPA value "{gpa_value}".'
                    )
                else:
                    if profile.gpa != parsed_gpa:
                        profile.gpa = parsed_gpa
                        profile_updates.append("gpa")
            if profile_updates:
                profile.save(update_fields=profile_updates)

    log.record_count = created_count + updated_count
    log.status = "COMPLETED" if not row_errors else "FAILED"
    log.error_message = "\n".join(row_errors) if row_errors else ""
    log.operation_details.update(
        {
            "created_count": created_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "errors": row_errors,
        }
    )
    log.save(
        update_fields=["record_count", "status", "error_message", "operation_details"]
    )
    return log


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "on", "yes"}
    return bool(value)


def _cleanup_options(raw):
    raw = raw or {}
    return {
        "clean_orphaned": _as_bool(raw.get("clean_orphaned")),
        "clean_duplicates": _as_bool(raw.get("clean_duplicates")),
        "clean_invalid": _as_bool(raw.get("clean_invalid")),
    }


def serialize_log(log):
    if log is None:
        return None
    return {
        "id": str(log.id),
        "operation_type": log.operation_type,
        "model_name": log.model_name,
        "status": log.status,
        "record_count": log.record_count,
        "error_message": log.error_message or "",
        "created_at": log.created_at,
        "user": getattr(log.user, "email", None) if log.user else None,
        "operation_details": log.operation_details or {},
    }


def serialize_item(section, obj):
    base = {
        "id": str(obj.id),
        "name": obj.name,
        "description": getattr(obj, "description", "") or "",
    }
    if section == "bulk_operation":
        base.update(
            {
                "operation_type": obj.operation_type,
                "requires_confirmation": obj.requires_confirmation,
            }
        )
    elif section == "data_export":
        base.update({"model_name": obj.model_name, "format": obj.format})
    elif section == "data_import":
        base.update({"model_name": obj.model_name, "format": obj.format})
    elif section == "demo_data":
        base.update({"data_config": obj.data_config or {}})
    return base


def list_section_items(user, section):
    if section not in EXECUTE_PERMISSIONS:
        raise DataManagementError("Unknown data-management section.", 400)
    if not has_data_permission(user, section, "VIEW"):
        raise DataManagementError(
            "You don't have permission to view this section.", 403
        )

    model = SECTION_MODELS.get(section)
    if model is None:
        return []
    return [
        serialize_item(section, obj) for obj in model.objects.filter(is_active=True)
    ]


def execute_section(
    user,
    section,
    *,
    item_id=None,
    confirm=None,
    cleanup_options=None,
    uploaded_file=None,
    source="spa",
):
    permission = EXECUTE_PERMISSIONS.get(section)
    if permission is None:
        raise DataManagementError("Unknown data-management section.", 400)
    if not has_data_permission(user, section, permission):
        raise DataManagementError(
            "You don't have permission to run this operation.", 403
        )

    if section == "bulk_operation":
        operation = get_object_or_404(
            BulkOperation.objects.filter(is_active=True), id=item_id
        )
        log = queue_operation(
            user=user,
            operation_type="BULK_UPDATE",
            model_name=operation.operation_type,
            operation_details={
                "source": source,
                "operation_id": str(operation.id),
                "operation_name": operation.name,
                "requires_confirmation": operation.requires_confirmation,
                "custom_filters": operation.custom_filters,
            },
        )
        return {
            "log": log,
            "message": f'Bulk operation "{operation.name}" has been queued.',
        }

    if section == "data_export":
        export_config = get_object_or_404(
            DataExport.objects.filter(is_active=True), id=item_id
        )
        log = queue_operation(
            user=user,
            operation_type="EXPORT",
            model_name=export_config.model_name,
            operation_details={
                "source": source,
                "export_id": str(export_config.id),
                "export_name": export_config.name,
                "format": export_config.format,
                "include_fields": export_config.include_fields,
                "filters": export_config.filters,
            },
        )
        return {
            "log": log,
            "message": f'Export "{export_config.name}" has been queued.',
        }

    if section == "data_import":
        import_config = get_object_or_404(
            DataImport.objects.filter(is_active=True), id=item_id
        )
        if not uploaded_file:
            raise DataManagementError("Please choose a file to import.", 400)
        if (
            import_config.model_name == "accounts.user"
            and import_config.format == "CSV"
        ):
            log = execute_student_import(
                import_config, uploaded_file, user, source=source
            )
            if log.status == "COMPLETED":
                message = (
                    f"Student import completed. Created "
                    f"{log.operation_details['created_count']} and updated "
                    f"{log.operation_details['updated_count']} records."
                )
            else:
                message = (
                    f"Student import completed with issues. Imported "
                    f"{log.record_count} records; review the operation log "
                    f"for skipped rows."
                )
            return {"log": log, "message": message}

        log = queue_operation(
            user=user,
            operation_type="IMPORT",
            model_name=import_config.model_name,
            operation_details={
                "source": source,
                "import_id": str(import_config.id),
                "import_name": import_config.name,
                "format": import_config.format,
                "field_mapping": import_config.field_mapping,
                "validation_rules": import_config.validation_rules,
            },
            file_path=uploaded_file.name,
        )
        return {
            "log": log,
            "message": f'Import "{import_config.name}" has been queued.',
        }

    if section == "demo_data":
        dataset = get_object_or_404(
            DemoDataSet.objects.filter(is_active=True), id=item_id
        )
        log = queue_operation(
            user=user,
            operation_type="DEMO_SETUP",
            model_name="demo_data",
            operation_details={
                "source": source,
                "dataset_id": str(dataset.id),
                "dataset_name": dataset.name,
                "data_config": dataset.data_config,
            },
        )
        return {
            "log": log,
            "message": f'Demo data setup "{dataset.name}" has been queued.',
        }

    if section == "database":
        if confirm != "RESET":
            raise DataManagementError(
                "Type 'RESET' to confirm the database reset request.", 400
            )
        log = queue_operation(
            user=user,
            operation_type="DB_RESET",
            model_name="database",
            operation_details={"source": source, "confirmed": True},
        )
        return {"log": log, "message": "Database reset has been queued for review."}

    selected = _cleanup_options(cleanup_options)
    if not any(selected.values()):
        raise DataManagementError("Select at least one cleanup operation.", 400)
    log = queue_operation(
        user=user,
        operation_type="CLEANUP",
        model_name="data_cleanup",
        operation_details={"source": source, "cleanup_options": selected},
    )
    return {"log": log, "message": "Data cleanup has been queued."}
