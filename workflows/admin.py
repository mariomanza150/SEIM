from django.contrib import admin

from .models import WorkflowDefinition, WorkflowEvent, WorkflowInstance, WorkflowVersion


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    search_fields = ("name", "slug", "description")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(WorkflowVersion)
class WorkflowVersionAdmin(admin.ModelAdmin):
    list_display = ("definition", "version", "status", "published_at", "created_at")
    list_filter = ("status",)
    search_fields = ("definition__name", "definition__slug")
    readonly_fields = ("created_at", "updated_at")


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ("application", "workflow_version", "status", "last_event_at", "created_at")
    search_fields = ("application__id", "workflow_version__definition__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(WorkflowEvent)
class WorkflowEventAdmin(admin.ModelAdmin):
    list_display = ("instance", "event_type", "actor", "created_at")
    search_fields = ("event_type", "instance__application__id")
    readonly_fields = ("created_at", "updated_at")

