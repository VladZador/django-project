from django.http import Http404
from django.views.generic import DetailView
from django.utils.translation import gettext_lazy as _

from .models import Order


class OrderDetailView(DetailView):
    model = Order

    def get_object(self, **kwargs):
        try:
            return Order.objects.get(user=self.request.user, is_active=True)
        except Order.DoesNotExist:
            return None
