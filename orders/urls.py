from django.urls import path

from .views import (
    AllProductsRemoveView, DiscountAddView, DiscountCancelView,
    OrderDetailView, OrderDisplayView, OrderPaymentView, ProductRemoveView,
    RecalculateCartView
)

urlpatterns = [
    path("cart/", OrderDetailView.as_view(), name='cart'),
    path(
        "cart/recalculate/",
        RecalculateCartView.as_view(),
        name="recalculate_cart"
    ),
    path(
        "cart/remove/<uuid:pk>/",
        ProductRemoveView.as_view(),
        name="remove_product"
    ),
    path(
        "cart/remove-all/",
        AllProductsRemoveView.as_view(),
        name="remove_all_products"
    ),
    path("cart/add-discount/", DiscountAddView.as_view(), name="add_discount"),
    path(
        "cart/cancel-discount",
        DiscountCancelView.as_view(),
        name="cancel_discount"
    ),
    path("cart/order/", OrderDisplayView.as_view(), name="order"),
    path("cart/order/pay-order", OrderPaymentView.as_view(), name="pay_order"),
]
