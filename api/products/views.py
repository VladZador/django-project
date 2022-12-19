from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.products.serializers import ProductSerializer, CategorySerializer
from products.models import Product, Category


class ProductsViewSet(RetrieveModelMixin,
                      ListModelMixin,
                      GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class CategoryViewSet(RetrieveModelMixin,
                      ListModelMixin,
                      GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods="get", url_path="products")
    def get_products(self, request, *args, **kwargs):
        serializer = ProductSerializer(
            self.get_object().product_set,
            many=True
        )
        return Response(serializer.data)
