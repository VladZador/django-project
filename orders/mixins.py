from django.core.exceptions import ValidationError
from django.forms import Form
from django.utils.translation import gettext_lazy as _

from orders.models import Order


class CurrentOrderMixin:

    def get_object(self):
        try:
            return Order.objects.get(user=self.request.user, is_active=True)
        except Order.DoesNotExist:
            return None


class CurrentOrderFormMixin(Form):

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean(self):
        if not self.instance:
            raise ValidationError(_("Order doesn't exist"))
        return super().clean()
