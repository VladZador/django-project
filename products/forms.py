from django.forms import Form, FileField

from .mixins import ProductFormMixin


class CsvImportForm(Form):
    csv_import = FileField()


class AddToCartForm(ProductFormMixin):

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        self.instance = instance

    def save(self):
        self.instance.products.add(self.cleaned_data["product"])


class UpdateFavoriteProductsForm(ProductFormMixin):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, action):
        getattr(
            self.user.favorite_products, action
        )(self.cleaned_data["product"])
