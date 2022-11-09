from django.core.exceptions import ValidationError
from django.forms import Form, UUIDField
from django.utils.translation import gettext_lazy as _

from .models import Product


class ProductFormMixin(Form):
    product = UUIDField()

    def clean_product(self):
        try:
            product = Product.objects.get(id=self.cleaned_data['product'])
        except Product.DoesNotExist:
            raise ValidationError(_(
                "Sorry, there is no product with this uuid"
            ))
        return product
