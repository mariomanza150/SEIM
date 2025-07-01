from django.contrib import admin
from ..models import ExchangeProgram

@admin.register(ExchangeProgram)
class ExchangeProgramAdmin(admin.ModelAdmin):
    pass
