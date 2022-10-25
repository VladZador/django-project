from django.urls import path

from .views import OrderDetailView


urlpatterns = [
    path("cart/", OrderDetailView.as_view(), name='cart'),
]
