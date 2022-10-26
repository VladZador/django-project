from django.urls import path

from .views import OrderDetailView, remove_product_from_cart

urlpatterns = [
    path("cart/", OrderDetailView.as_view(), name='cart'),
    path("cart/remove/<uuid:pk>/", remove_product_from_cart, name="remove_product"),

]
