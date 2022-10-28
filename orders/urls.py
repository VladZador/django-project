from django.urls import path

from .views import (
    cancel_discount, OrderDetailView, remove_product_from_cart,
    remove_all_products, DiscountAddView, RecalculateCartView, pay_the_order,
    Ordering, OrderDisplayView
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
        remove_product_from_cart,
        name="remove_product"
    ),
    path("cart/remove-all/", remove_all_products, name="remove_all_products"),
    path(
        "cart/add-discount/",
        DiscountAddView.as_view(),
        name="add_discount"
    ),
    path("cart/cancel-discount", cancel_discount, name="cancel_discount"),
    path("cart/make_order/", Ordering.as_view(), name="make_order"),
    path("cart/order/", OrderDisplayView.as_view(), name="order"),
    path("cart/order/pay-order", pay_the_order, name="pay_order"),
]
