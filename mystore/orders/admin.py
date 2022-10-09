from django.contrib import admin

from .models import Order, Discount


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    filter_horizontal = ("products",)
    list_display = ("total_amount", "created_at", "discount", "calculate_with_discount")
    list_filter = ("created_at", "total_amount")
    readonly_fields = ("calculate_with_discount",)

    def get_total_amount(self, obj=None):
        return obj.calculate_with_discount()


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("is_active", "discount_type")
    list_filter = ("discount_type",)
