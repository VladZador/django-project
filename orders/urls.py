from django.urls import path

from .views import OrderDetailView, remove_product_from_cart, remove_all_products

urlpatterns = [
    path("cart/", OrderDetailView.as_view(), name='cart'),
    path("cart/remove/<uuid:pk>/", remove_product_from_cart, name="remove_product"),
    path("cart/remove-all/", remove_all_products, name="remove_all_products"),

]
