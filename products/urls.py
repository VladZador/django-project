from django.urls import path, re_path

from .views import (
    ProductListView, ProductDetailView, export_csv, export_csv_detail,
    AddToCartView, UpdateStarredStatusView, FavouriteProductsView
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product_list"),
    path(
        "products/<uuid:pk>/",
        ProductDetailView.as_view(),
        name="product_detail"
    ),
    path("products/csv/", export_csv, name="product_list_export_csv"),
    path(
        "products/<uuid:pk>/csv/",
        export_csv_detail,
        name="product_detail_export_csv"
    ),
    path("products/add-to-cart/", AddToCartView.as_view(), name="add_to_cart"),
    re_path(
        "products/(?P<action>add|remove)/",
        UpdateStarredStatusView.as_view(),
        name="star_product"
    ),
    path("products/favorite/", FavouriteProductsView.as_view(), name="favorite_products"),
]
