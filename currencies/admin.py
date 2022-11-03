from django.contrib import admin

from currencies.models import CurrencyHistory


@admin.register(CurrencyHistory)
class CurrencyHistoryAdmin(admin.ModelAdmin):
    list_display = ("currency", "buy", "sale", "created_at")
