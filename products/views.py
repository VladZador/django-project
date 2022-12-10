import csv
from io import StringIO

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
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
        else:
            messages.error(
                self.request,
                "Sorry, there is no product with this uuid"
            )
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
        else:
            messages.error(
                self.request,
                "Sorry, there is no product with this uuid"
            )
        return self.get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        """
        Redirects to the referer, or if there's no any,
        to the 'favorite_products' url.
        """
        return self.request.headers.get(
            "Referer", reverse_lazy("favorite_products")
        )


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
    try:
        product = Product.objects.get(pk=kwargs["pk"])
        _write_csv_row(writer, product)
        return response
    except Product.DoesNotExist:
        messages.error(request, "Sorry, there is no product with this uuid")
        return redirect("product_list")


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
    if product_instance.image:
        image_name = settings.DOMAIN + product_instance.image.url
    else:
        image_name = "No image"
    writer.writerow(
        {
            "name": product_instance.name,
            "description": product_instance.description or "",
            "category": product_instance.category,
            "price": product_instance.price,
            "currency": product_instance.currency,
            "sku": product_instance.sku,
            "image": image_name,
        }
    )
    return writer


@staff_member_required
def import_products_from_csv(request):
    """
    Allows to upload a .csv file, extracts the data, creates and adds
    product instances from the data to the database.
    """
    form = CsvImportForm()
    context = {"form": form}

    if request.method == "POST":
        csv_file = request.FILES.get("csv_import")
        if not csv_file:
            messages.error(
                request,
                "No file uploaded. File '.csv' should be uploaded"
            )
        else:
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
    if not file_data.fieldnames == [
        'name', 'description', 'category', 'price', 'currency', 'sku'
    ]:
        messages.error(
            request,
            "Data has not been imported. Some columns are missing"
        )
    else:
        product_list = []
        for product_data in file_data:
            if len([v for v in product_data.values() if v]) \
                    != len(file_data.fieldnames):
                messages.error(
                    request,
                    "Data has not been imported. "
                    "Some columns are missing or overpopulated"
                )
            else:
                try:
                    product = Product(
                        name=product_data["name"],
                        description=product_data["description"],
                        category=Category.objects.get_or_create(
                            name=product_data["category"]
                        )[0],
                        price=product_data["price"],
                        currency=product_data["currency"],
                        sku=product_data["sku"],
                    )
                    product.full_clean(exclude=("image",))
                    product_list.append(product)
                except ValidationError:
                    messages.error(
                        request,
                        "Data has not been imported. Some data has wrong type"
                    )
        if product_list:
            Product.objects.bulk_create(product_list)
            messages.success(request, "Data has been imported")
