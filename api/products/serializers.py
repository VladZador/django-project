from rest_framework.serializers import ModelSerializer

from products.models import Product, Category


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "name", "description", "image", "category", "price", "currency",
            "sku", "products"
        )


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name", "description", "image",
        )
