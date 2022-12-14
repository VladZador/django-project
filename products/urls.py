from django.urls import path, re_path

from .views import (
    ProductListView, ProductDetailView, export_csv, export_csv_detail,
    AddToCartView, UpdateFavoriteProductsView, FavouriteProductsView,
    AJAXUpdateFavoriteProductsView
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
        "products/(?P<action>add|remove)-favorite/",
        UpdateFavoriteProductsView.as_view(),
        name="update_favorite_products"
    ),
    re_path(
        "products/ajax-(?P<action>add|remove)-favorite/",
        AJAXUpdateFavoriteProductsView.as_view(),
        name="ajax_update_favorite_products"
    ),
    path(
        "products/favorite/",
        FavouriteProductsView.as_view(),
        name="favorite_products"
    ),
]
