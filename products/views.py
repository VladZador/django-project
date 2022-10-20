import csv

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import ListView, DetailView

from .models import Product


class ProductListView(ListView):
    model = Product


class ProductDetailView(DetailView):
    model = Product


@login_required
def export_csv(request, *args, **kwargs):
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
    return response


def _create_csv_writer(response):
    fieldnames = ["name", "description", "category", "price", "sku", "image"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    return writer


def _write_csv_row(writer, product_instance):
    writer.writerow(
        {
            "name": product_instance.name,
            "description": product_instance.description,
            "category": product_instance.category,
            "price": product_instance.price,
            "sku": product_instance.sku,
            "image": settings.DOMAIN + product_instance.image.url,
        }
    )
    return writer


def import_csv(request, *args, **kwargs):
    pass
