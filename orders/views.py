from django.db.models import F
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, RedirectView
from django.utils.translation import gettext_lazy as _

from products.models import Product
from .forms import DiscountInputForm, RecalculateCartForm
from .models import Order


class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/cart.html"

    # Сделал возвращение None в случае отсутствия заказа для того, чтобы
    # в таком случае в корзине была запись "Корзина пуста"
    def get_object(self, **kwargs):
        try:
            return Order.objects.get(user=self.request.user, is_active=True)
        except Order.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update(
            {"order": self.get_object(),
             "products_relation": self.get_queryset()}
        )
        return context

    def get_queryset(self):
        if self.get_object():
            return self.get_object().products.through.objects\
                .select_related("product")\
                .annotate(full_price=F("product__price") * F("quantity"))


class RecalculateCartView(RedirectView):
    url = reverse_lazy('cart')

    def get_object(self, **kwargs):
        return Order.objects.get(user=self.request.user, is_active=True)

    def post(self, request, *args, **kwargs):
        form = RecalculateCartForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
        return self.get(request, *args, **kwargs)


class DiscountAddView(RedirectView):
    url = reverse_lazy("cart")

    def post(self, request, *args, **kwargs):
        form = DiscountInputForm(
            request.POST,
            instance=Order.objects.get(user=self.request.user, is_active=True)
        )
        if form.is_valid():
            form.save()
        return self.get(request, *args, **kwargs)


def cancel_discount(request, *args, **kwargs):
    order = Order.objects.get(user=request.user, is_active=True)
    order.discount = None
    order.save()
    return redirect("cart")


def remove_product_from_cart(request, *args, **kwargs):
    try:
        order = Order.objects.get(user=request.user, is_active=True)
        product = Product.objects.get(pk=kwargs["pk"])
        order.products.remove(product)
        order.save()
        return redirect("cart")
    except Product.DoesNotExist:
        raise Http404(_("Sorry, there is no product with this uuid"))


def remove_all_products(request, *args, **kwargs):
    order = Order.objects.get(user=request.user, is_active=True)
    order.delete()
    return redirect("cart")


def pay_the_order(request, *args, **kwargs):
    ...
