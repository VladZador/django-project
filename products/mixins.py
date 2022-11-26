from django.core.exceptions import ValidationError
from django.forms import Form, UUIDField
from django.utils.translation import gettext_lazy as _

from .models import Product


# This mixin was used for AddToCartForm and UpdateFavoriteProductsForm, but
# I had to separate a logic of "clean_product" for the second one, so currently
# this mixin is not used.
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
