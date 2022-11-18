from django.contrib import admin
from django.urls import path

from .models import Category, Product
from mystore.mixins.admin_mixin import ThumbnailAdminMixin
from .views import import_products_from_csv


@admin.register(Category)
class CategoryAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    list_display = ("name", "created_at")


@admin.register(Product)
class ProductAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    filter_horizontal = ("products", )
    list_display = ("name", "price", "created_at")
    list_filter = ("price", "created_at")

    def get_urls(self):
        """Adds custom url to the admin urls list."""
        urls = super().get_urls()
        new_urls = [path(
            "import_csv/",
            self.import_csv,
            name="import_products_csv"
        ), ]
        return new_urls + urls

    @staticmethod
    def import_csv(request):
        return import_products_from_csv(request)
