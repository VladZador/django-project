from orders.models import Order


class CurrentOrderMixin:

    def get_object(self):
        try:
            return Order.objects.get(user=self.request.user, is_active=True)
        except Order.DoesNotExist:
            return None
