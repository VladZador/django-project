from django.contrib import admin

from .models import Order, Discount


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    filter_horizontal = ("products",)
    list_display = ("total_amount", "created_at", "discount")
    list_filter = ("created_at", "total_amount")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("amount", "code", "is_active", "discount_type")
    list_filter = ("discount_type",)

