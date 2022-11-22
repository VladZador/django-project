import csv
from io import StringIO

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, RedirectView

from orders.models import Order
from .forms import AddToCartForm, UpdateFavoriteProductsForm, CsvImportForm
from .models import Product, Category


class ProductListView(ListView):
    model = Product

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related("user_set__favorite_products")
        return qs


class ProductDetailView(DetailView):
    model = Product


class AddToCartView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("product_list")

    def get_order_object(self):
        return Order.objects.get_or_create(
            user=self.request.user,
            is_active=True
        )[0]

    def post(self, request, *args, **kwargs):
        form = AddToCartForm(request.POST,  instance=self.get_order_object())
        if form.is_valid():
            form.save()
            messages.success(self.request, "Product added to your cart!")
        return self.get(request, *args, **kwargs)


class UpdateFavoriteProductsView(LoginRequiredMixin, RedirectView):

    def post(self, request, *args, **kwargs):
        form = UpdateFavoriteProductsForm(
            request.POST,
            user=request.user,
            action=kwargs["action"]
        )
        if form.is_valid():
            form.save(kwargs["action"])
            if kwargs["action"] == "add":
                messages.info(
                    self.request,
                    "Product is added to your favorite products list!",
                )
            else:
                messages.info(
                    self.request,
                    "Product is removed from your favorite products list",
                )
        return self.get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        try:
            return self.request.headers["Referer"]
        except KeyError:
            return reverse_lazy("favorite_products")


class FavouriteProductsView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = "favorite_products_list"
    template_name = "products/favorite_products.html"

    def get_queryset(self):
        return self.request.user.favorite_products.all()\
            .prefetch_related("user_set__favorite_products")


@login_required
def export_csv(request, *args, **kwargs):
    """Creates a csv file with products data from the database."""
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename="products.csv"'
        },
    )
    writer = _create_csv_writer(response)
    for product in Product.objects.iterator():
        _write_csv_row(writer, product)
    messages.success(request, "csv file created!")
    return response


@login_required
def export_csv_detail(request, *args, **kwargs):
    """
    Creates a csv file with data of the specified product from the database.
    """
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment;'
                                   f'filename="product-{kwargs["pk"]}.csv"'
        },
    )
    writer = _create_csv_writer(response)
    product = Product.objects.get(pk=kwargs["pk"])
    _write_csv_row(writer, product)
    messages.success(request, "csv file created!")
    return response


def _create_csv_writer(response):
    """Creates a csv writer object with the product info headers."""
    fieldnames = [
        "name",
        "description",
        "category",
        "price",
        "currency",
        "sku",
        "image",
    ]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    return writer


def _write_csv_row(writer, product_instance):
    """Adds parameters to be passed to the csv writer object."""
    writer.writerow(
        {
            "name": product_instance.name,
            "description": product_instance.description,
            "category": product_instance.category,
            "price": product_instance.price,
            "currency": product_instance.currency,
            "sku": product_instance.sku,
            "image": settings.DOMAIN + product_instance.image.url,
        }
    )
    return writer


@staff_member_required
def import_products_from_csv(request):
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
            _create_products_from_csv(request, file_data)
            return HttpResponseRedirect(
                reverse_lazy("admin:products_product_changelist")
            )
    form = CsvImportForm()
    context = {"form": form}
    return render(
        request,
        template_name="admin/products/product/products_import_csv.html",
        context=context)


def _create_products_from_csv(request, file_data):
    """
    Creates product instances from the parsed "file_data", adds them to
    the database. Blank image is inserted into the image field.
    If there is no category for a passed category name in the database,
    a new one with blank image is created.

    :return: None
    """
    # todo: Remove image adding. Without it, use get_or_create for the Category
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
