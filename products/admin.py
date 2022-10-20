import csv
from io import StringIO

from django import forms
from django.contrib import admin
from django.shortcuts import render
from django.urls import path

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

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path("import_csv/", self.import_csv, name="import_products_csv"), ]
        return new_urls + urls

        # todo: add redirect on the import page
    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_import"]
            file_data = csv.DictReader(StringIO(csv_file.read().decode("utf-8")))
            with open("static_dev/images/blank.png", "rb") as blank_image:
                product_list = []
                for product_data in file_data:
                    breakpoint()
                    product = Product(
                        name=product_data["name"],
                        description=product_data["description"],
                        category=Category.objects.get(name=product_data["category"]),
                        price=product_data["price"],
                        sku=product_data["sku"],
                    )
                    product.image.save("images/blank_image.png", blank_image, save=False)
                    product_list.append(product)
                Product.objects.bulk_create(product_list)

        form = CsvImportForm()
        context = {"form": form}
        return render(request, "admin/products/product/products_import_csv.html", context=context)


class CsvImportForm(forms.Form):
    csv_import = forms.FileField()
