import django_filters

from products.models import Product


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'category': ['exact'],
            'price': ['gt', 'lt'],
        }
