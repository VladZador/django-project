from django.core.exceptions import ValidationError
from django.forms import Form, CharField, IntegerField, UUIDField
from django.utils.translation import gettext_lazy as _

from orders.models import Discount


class RecalculateCartForm(Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.instance = kwargs['instance']
        self.fields = {key: IntegerField() if key.startswith(
            'quantity') else UUIDField() for key in self.data.keys() if
                       key != 'csrfmiddlewaretoken'}

    def save(self):
        """
        {'quantity_0': 2,
        'product_0': UUID('e04bc1aa-dc11-4791-a187-5118ea5ce01a'),
        'quantity_1': 2,
        'product_1': UUID('4e26895f-2056-4c57-ad53-3a09c9861b56'),
        'quantity_2': 3,
        'product_2': UUID('f6177123-adb7-4237-bc3e-8a5d2aabae6e')}
        :return: instance
        """
        for key in self.cleaned_data.keys():
            if key.startswith('product_'):
                index = key.split('_')[-1]
                self.instance.products.through.objects \
                    .filter(product_id=self.cleaned_data[f'product_{index}']) \
                    .update(quantity=self.cleaned_data[f'quantity_{index}'])
        return self.instance


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
