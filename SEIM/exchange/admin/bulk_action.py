from django.contrib import admin
from ..models import BulkAction, BulkActionItem, BulkActionLog

@admin.register(BulkAction)
class BulkActionAdmin(admin.ModelAdmin):
    pass

@admin.register(BulkActionItem)
class BulkActionItemAdmin(admin.ModelAdmin):
    pass

@admin.register(BulkActionLog)
class BulkActionLogAdmin(admin.ModelAdmin):
    pass
