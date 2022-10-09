from django.contrib import admin

from .models import Order, Discount


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    filter_horizontal = ("products",)
    list_display = (
        "total_amount", "created_at", "discount", "get_total_amount"
    )
    list_filter = ("created_at", "total_amount")
    readonly_fields = ("get_total_amount",)

    def get_total_amount(self, obj=None):
        return obj.calculate_with_discount()

    get_total_amount.short_description = "Total amount with discount"


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("code", "is_active", "discount_type")
    list_filter = ("discount_type",)
