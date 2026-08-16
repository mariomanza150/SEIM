from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View

from .operations import DataManagementError, execute_section, spa_section_url


def _deny_and_redirect(request, message, section=None):
    messages.error(request, message)
    return redirect(spa_section_url(section) if section else "admin:index")


def _handle_execute(request, section, **kwargs):
    try:
        result = execute_section(
            request.user, section, source="data_management_ui", **kwargs
        )
    except Http404:
        raise
    except DataManagementError as exc:
        if exc.code == 404:
            raise Http404(exc.message) from exc
        return _deny_and_redirect(request, exc.message, section)
    messages.success(request, result["message"])
    return redirect(spa_section_url(section))


class DataManagementIndexView(View):
    """Legacy hub: send operators to the SPA console."""

    @method_decorator(login_required)
    def get(self, request):
        return redirect(spa_section_url())


class BulkOperationView(View):
    @method_decorator(login_required)
    def get(self, request):
        return redirect(spa_section_url("bulk_operation"))

    @method_decorator(login_required)
    def post(self, request, operation_id):
        return _handle_execute(request, "bulk_operation", item_id=operation_id)


class DataExportView(View):
    @method_decorator(login_required)
    def get(self, request):
        return redirect(spa_section_url("data_export"))

    @method_decorator(login_required)
    def post(self, request, export_id):
        return _handle_execute(request, "data_export", item_id=export_id)


class DataImportView(View):
    @method_decorator(login_required)
    def get(self, request):
        return redirect(spa_section_url("data_import"))

    @method_decorator(login_required)
    def post(self, request, import_id):
        return _handle_execute(
            request,
            "data_import",
            item_id=import_id,
            uploaded_file=request.FILES.get("file"),
        )


class DemoDataSetupView(View):
    @method_decorator(login_required)
    def get(self, request):
        return redirect(spa_section_url("demo_data"))

    @method_decorator(login_required)
    def post(self, request, dataset_id):
        return _handle_execute(request, "demo_data", item_id=dataset_id)


class DatabaseResetView(View):
    @method_decorator(login_required)
    def get(self, request):
        return redirect(spa_section_url("database"))

    @method_decorator(login_required)
    def post(self, request):
        return _handle_execute(request, "database", confirm=request.POST.get("confirm"))


class DataCleanupView(View):
    @method_decorator(login_required)
    def get(self, request):
        return redirect(spa_section_url("data_cleanup"))

    @method_decorator(login_required)
    def post(self, request):
        return _handle_execute(
            request,
            "data_cleanup",
            cleanup_options={
                "clean_orphaned": request.POST.get("clean_orphaned"),
                "clean_duplicates": request.POST.get("clean_duplicates"),
                "clean_invalid": request.POST.get("clean_invalid"),
            },
        )
