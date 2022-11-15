import csv

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, RedirectView

from orders.models import Order
from .forms import AddToCartForm, UpdateStarredStatusForm
from .models import Product


class ProductListView(ListView):
    model = Product

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related("user_set__starred_products")
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


class UpdateStarredStatusView(LoginRequiredMixin, RedirectView):

    def post(self, request, *args, **kwargs):
        form = UpdateStarredStatusForm(request.POST, user=request.user)
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
        return self.request.headers.get("Referer")


class FavouriteProductsView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = "favorite_products_list"
    template_name = "products/favorite_products.html"

    def get_queryset(self):
        return self.request.user.starred_products.all().prefetch_related("user_set__starred_products")


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
