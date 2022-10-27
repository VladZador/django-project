from django.core.exceptions import ValidationError
from django.forms import Form, CharField
from django.utils.translation import gettext_lazy as _

from orders.models import Discount


class DiscountInputForm(Form):
    discount = CharField(max_length=32)

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean_discount(self):
        try:
            discount = Discount.objects.get(code=self.cleaned_data['discount'], is_active=True)
        except Discount.DoesNotExist:
            raise ValidationError(_("There's no discount with this code name"))
        return discount

    def save(self):
        self.instance.discount = self.cleaned_data["discount"]
        self.instance.save()
        return self.instance
