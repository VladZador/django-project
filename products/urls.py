from django.urls import path

from .views import (
    ProductListView, ProductDetailView, export_csv, export_csv_detail,
    add_to_cart
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path(
        'products/<uuid:pk>/',
        ProductDetailView.as_view(),
        name="product_detail"
    ),
    path('products/csv/', export_csv, name="product_list_export_csv"),
    path(
        'products/<uuid:pk>/csv/',
        export_csv_detail,
        name="product_detail_export_csv"
    ),
    path('products/add-to-cart/<uuid:pk>/', add_to_cart, name="add_to_cart")
]
