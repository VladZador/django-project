from orders.models import Order


# Сделал возвращение None в случае отсутствия заказа для того, чтобы
# в таком случае в корзине была запись "Корзина пуста"
class CurrentOrderMixin:

    def get_object(self):
        try:
            return Order.objects.get(user=self.request.user, is_active=True)
        except Order.DoesNotExist:
            return None
