from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.utils.translation import gettext_lazy as _

from products.models import Product
from .models import Order


# todo: add functionality to calculate total price, add discount,
#  deleting products from order, pay or destroy the order
class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/cart.html"

    def get_object(self, **kwargs):
        try:
            return Order.objects.get(user=self.request.user, is_active=True)
        except Order.DoesNotExist:
            return None


def remove_product_from_cart(request, *args, **kwargs):
    if request.method == 'GET':
        try:
            order = Order.objects.get(user=request.user, is_active=True)
            product = Product.objects.get(pk=kwargs["pk"])
            order.products.remove(product)
            order.save()
            return redirect("cart")
        except Product.DoesNotExist:
            raise Http404(_("Sorry, there is no product with this uuid"))
