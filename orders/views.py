from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, TemplateView
from django.utils.translation import gettext_lazy as _

from products.models import Product
from .forms import DiscountInputForm, RecalculateCartForm
from .mixins import CurrentOrderMixin


# todo: update views so that they don't contain save() logic with the orders.
#  It should be done in the forms.py

@method_decorator(login_required, name='dispatch')
class OrderDetailView(CurrentOrderMixin, TemplateView):
    template_name = "orders/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update(
            {"order": self.get_object(),
             "products_relation": self.get_queryset()}
        )
        return context

    def get_queryset(self):
        if self.get_object():
            return self.get_object().get_products_through()

    def post(self, *args, **kwargs):
        return self.get(self, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class RecalculateCartView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy('cart')

    def post(self, request, *args, **kwargs):
        form = RecalculateCartForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DiscountAddView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("cart")

    def post(self, request, *args, **kwargs):
        form = DiscountInputForm(
            request.POST,
            instance=self.get_object()
        )
        if form.is_valid():
            form.save()
        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DiscountCancelView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("cart")

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.discount = None
        order.save()
        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ProductRemoveView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("cart")

    def get(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            product = Product.objects.get(pk=kwargs["pk"])
            order.products.remove(product)
            order.save()
            return super().get(request, *args, **kwargs)
        except Product.DoesNotExist:
            raise Http404(_("Sorry, there is no product with this uuid"))


@method_decorator(login_required, name='dispatch')
class AllProductsRemoveView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("cart")

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.delete()
        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class OrderDisplayView(OrderDetailView):
    """
    Has the same attributes as its parent class, only the different template.
    """
    template_name = "orders/order.html"


@method_decorator(login_required, name='dispatch')
class OrderPayment(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("product_list")

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.is_paid = True
        order.is_active = False
        order.total_amount = order.calculate_with_discount()
        order.save()
        return super().get(request, *args, **kwargs)
