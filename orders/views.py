from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, TemplateView
from django.utils.translation import gettext_lazy as _

from products.models import Product
from .forms import DiscountInputForm, RecalculateCartForm
from .models import Order


@method_decorator(login_required, name='dispatch')
class OrderDetailView(TemplateView):
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
            return self.get_object().products.through.objects.filter(order=self.get_object())\
                .select_related("product")\
                .annotate(full_price=F("product__price") * F("quantity"))

    def post(self, *args, **kwargs):
        return self.get(self, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class RecalculateCartView(RedirectView):
    url = reverse_lazy('cart')

    def get_object(self, **kwargs):
        return Order.objects.get(user=self.request.user, is_active=True)

    def post(self, request, *args, **kwargs):
        form = RecalculateCartForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
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


# todo: try to rewrite this views as class-based
@login_required
def cancel_discount(request, *args, **kwargs):
    order = Order.objects.get(user=request.user, is_active=True)
    order.discount = None
    order.save()
    return redirect("cart")


@login_required
def remove_product_from_cart(request, *args, **kwargs):
    try:
        order = Order.objects.get(user=request.user, is_active=True)
        product = Product.objects.get(pk=kwargs["pk"])
        order.products.remove(product)
        order.save()
        return redirect("cart")
    except Product.DoesNotExist:
        raise Http404(_("Sorry, there is no product with this uuid"))


@login_required
def remove_all_products(request, *args, **kwargs):
    order = Order.objects.get(user=request.user, is_active=True)
    order.delete()
    return redirect("cart")


@method_decorator(login_required, name='dispatch')
class Ordering(RedirectView):
    url = reverse_lazy("order")


@method_decorator(login_required, name='dispatch')
class OrderDisplayView(OrderDetailView):
    """
    Has the same attributes as its parent class, only the different template.
    """
    template_name = "orders/order.html"


@login_required
def pay_the_order(request, *args, **kwargs):
    order = Order.objects.get(user=request.user, is_active=True)
    order.is_paid = True
    order.is_active = False
    order.total_amount = order.calculate_with_discount()
    order.save()
    return redirect("product_list")
