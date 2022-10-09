from django.contrib import admin

from .models import Item, Category, Product
from mystore.mixins.admin_mixin import ThumbnailAdminMixin


@admin.register(Item)
class ItemAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_filter = ("created_at",)


@admin.register(Category)
class CategoryAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    list_display = ("name", "created_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ("items", )
    list_display = ("name", "price")
    list_filter = ("price", )

