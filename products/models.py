from os import path
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from currencies.models import CurrencyHistory
from mystore.mixins.model_mixins import PKMixin
from mystore.model_choices import Currencies


def upload_image(instance, filename):
    _name, extension = path.splitext(filename)
    return f"images/{instance.__class__.__name__.lower()}/" \
           f"{instance.id}/image{extension}"


class Category(PKMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_image)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Product(PKMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_image)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    currency = models.PositiveSmallIntegerField(
        choices=Currencies.choices,
        default=Currencies.UAH,
    )
    sku = models.CharField(max_length=255)
    products = models.ManyToManyField("Product", blank=True)

    def __str__(self):
        return f"{self.name} | {self.category} | {self.price} {self.get_currency_display}"

    @property
    def exchange_price(self):
        if self.currency == Currencies.UAH:
            return self.price
        else:
            return round(self.price * self.exchange_rate, 2)

    @property
    def exchange_rate(self):
        return CurrencyHistory.objects.filter(currency=self.currency)\
            .order_by("-created_at").first().sale
