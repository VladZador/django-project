from os import path
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from mystore.mixins.model_mixins import PKMixin


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
    sku = models.CharField(max_length=255)
    products = models.ManyToManyField("Product", blank=True)

    def __str__(self):
        return f"{self.name} | {self.category} | {self.price} | {self.sku}"
