from django.contrib import admin

from .models import Category, Product
from mystore.mixins.admin_mixin import ThumbnailAdminMixin


@admin.register(Category)
class CategoryAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    list_display = ("name", "created_at")


@admin.register(Product)
class ProductAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    filter_horizontal = ("products", )
    list_display = ("name", "price", "created_at")
    list_filter = ("price", "created_at")
