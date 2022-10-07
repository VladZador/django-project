from django.contrib import admin

from .models import Item, Category, Product


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at",) #'image_tag',)
    list_filter = ("created_at",)
    # fields = ('image_tag',)
    # readonly_fields = ('image_tag',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at",) #'image_tag',)
    # fields = ('image_tag',)
    # readonly_fields = ('image_tag',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ("items", )
    list_display = ("name", "price")
    list_filter = ("price", )

