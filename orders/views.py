from django.views.generic import DetailView

from .models import Order


# todo: find a way to pass user to the queryset
class OrderDetailView(DetailView):
    queryset = Order.objects.get(user=request.user, is_active=True)
