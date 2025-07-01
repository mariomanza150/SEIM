from django.contrib import admin
from ..models import Exchange

@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    pass
