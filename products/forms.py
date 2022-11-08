from django.core.exceptions import ValidationError
from django.forms import Form, FileField, UUIDField
from django.utils.translation import gettext_lazy as _

from .models import Product


class CsvImportForm(Form):
    csv_import = FileField()


class AddToCartForm(Form):
    product = UUIDField()

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean_product(self):
        try:
            product = Product.objects.get(id=self.cleaned_data['product'])
        except Product.DoesNotExist:
            raise ValidationError(_(
                "Sorry, there is no product with this uuid"
            ))
        return product

    def save(self):
        self.instance.products.add(self.cleaned_data["product"])
