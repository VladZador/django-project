from django.views.generic import ListView

from .models import Product


class ProductView(ListView):
    model = Product
