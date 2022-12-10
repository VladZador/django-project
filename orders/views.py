from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, TemplateView

from .forms import (
    AllProductsRemoveForm, DiscountCancelForm, DiscountInputForm,
    OrderPaymentForm, ProductRemoveForm, RecalculateCartForm
)
from .mixins import CurrentOrderMixin


@method_decorator(login_required, name='dispatch')
class OrderDetailView(CurrentOrderMixin, TemplateView):
    template_name = "orders/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            "order": self.get_object(),
            "products_relation": self.get_queryset()
        })
        return context

    def get_queryset(self):
        if self.get_object():
            return self.get_object().get_products_through()

    def post(self, *args, **kwargs):
        """Is used to provide access to corresponding url (or urls)
        using the POST method (clicking the buttons, etc.)"""
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
        form = DiscountInputForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
            messages.success(request, "Discount applied!")
        else:
            messages.error(
                request,
                "Discount not applied. "
                "Most likely, there's no active discount with this code name"
            )
        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DiscountCancelView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("cart")

    def post(self, request, *args, **kwargs):
        form = DiscountCancelForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
            messages.info(request, "Discount not applied")
        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ProductRemoveView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("cart")

    def post(self, request, *args, **kwargs):
        form = ProductRemoveForm(
            request.POST,
            instance=self.get_object(),
            product_id=kwargs["pk"]
        )
        if form.is_valid():
            form.save()
        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class AllProductsRemoveView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("cart")

    def post(self, request, *args, **kwargs):
        form = AllProductsRemoveForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class OrderDisplayView(OrderDetailView):
    """
    Has the same attributes as its parent class, only the different template.
    """
    template_name = "orders/order.html"


@method_decorator(login_required, name='dispatch')
class OrderPaymentView(CurrentOrderMixin, RedirectView):
    url = reverse_lazy("product_list")

    def post(self, request, *args, **kwargs):
        form = OrderPaymentForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your order has been successfully processed!"
            )
        return self.get(request, *args, **kwargs)
