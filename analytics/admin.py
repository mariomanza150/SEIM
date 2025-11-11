from django.contrib import admin

from .models import DashboardConfig, Metric, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by")
    search_fields = ("name", "created_by__email")


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "report", "calculated_at")
    search_fields = ("name", "report__name")
    list_filter = ("report",)


@admin.register(DashboardConfig)
class DashboardConfigAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__email",)
