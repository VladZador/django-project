import csv
from io import StringIO

from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import path

from .forms import CsvImportForm
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
        """Adds custom url to the admin urls list."""
        urls = super().get_urls()
        new_urls = [path(
            "import_csv/",
            self.import_csv,
            name="import_products_csv"
        ), ]
        return new_urls + urls

    # todo: for now this view is displayed even to unregistered users!
    #  Need to find a way to make it accessible only to admins.
    def import_csv(self, request):
        """
        Allows to upload a .csv file, extracts the data, creates and adds
        product instances from the data to the database.
        """
        if request.method == "POST":
            csv_file = request.FILES["csv_import"]
            if not csv_file.name.endswith(".csv"):
                messages.error(request, "File '.csv' should be uploaded")
            else:
                file_data = csv.DictReader(
                    StringIO(csv_file.read().decode("utf-8"))
                )
                self._create_products_from_file(request, file_data)
        form = CsvImportForm()
        context = {"form": form}
        return render(
            request,
            template_name="admin/products/product/products_import_csv.html",
            context=context)

    @staticmethod
    def _create_products_from_file(request, file_data):
        """
        Creates product instances from the parsed "file_data", adds them to
        the database. Blank image is inserted into the image field.
        If there is no category for a passed category name in the database,
        a new one with blank image is created.

        :return: None
        """
        with open("static/images/blank.png", "rb") as blank_image:
            product_list = []
            for product_data in file_data:
                try:
                    category = Category.objects.get(
                        name=product_data["category"]
                    )
                except KeyError as error:
                    messages.error(request, f"Column {error} is not found")
                except Category.DoesNotExist:
                    category = Category(
                        name=product_data["category"]
                    )
                    category.image.save(
                        "images/blank_image.png",
                        blank_image
                    )
                finally:
                    try:
                        product = Product(
                            name=product_data["name"],
                            description=product_data["description"],
                            category=category,
                            price=product_data["price"],
                            currency=product_data["currency"],
                            sku=product_data["sku"],
                        )
                        product.image.save(
                            "images/blank_image.png",
                            blank_image,
                            save=False
                        )
                        product_list.append(product)
                    except KeyError as error:
                        messages.error(request, f"Column {error} is not found")
                        break
        if product_list:
            Product.objects.bulk_create(product_list)
            messages.success(request, "Data has been imported")
        else:
            messages.error(request, "Data has not been imported")
