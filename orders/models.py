from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F, Case, When, Sum

from mystore.mixins.model_mixins import PKMixin
from products.models import Product


class Order(PKMixin):
    products = models.ManyToManyField(Product, through="OrderProductRelation")
    total_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    discount = models.ForeignKey(
        "Discount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)

    def calculate_total_amount(self):
        """Calculates the total price of the order without the discount."""
        return self.products.through.objects.filter(order=self).aggregate(
            total_price=Sum(F("product__price") * F("quantity"))
                ).get("total_price") or 0

    def calculate_with_discount(self):
        """Calculates the total price of the order with the discount."""
        return self.products.through.objects.filter(order=self).annotate(
            full_price=F("product__price") * F("quantity")
                ).aggregate(
            total_amount=Case(
                When(
                    order__discount__discount_type=Discount.VALUE,
                    then=Sum("full_price") - F("order__discount__amount")
                ),
                When(
                    order__discount__discount_type=Discount.PERCENT,
                    then=Sum("full_price") - (
                            Sum("full_price")
                            * F("order__discount__amount") / 100)
                ),
                default=Sum("full_price"),
                output_field=models.DecimalField()
            )
        ).get("total_amount").quantize(Decimal('.01')) or 0


class OrderProductRelation(models.Model):
    """
    Intermediate table to connect the Order and Product models with
    Many-to-Many-like relation with extra products quantity parameter.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ("order", "product")


class Discount(PKMixin):
    amount = models.DecimalField(max_digits=4, decimal_places=2)
    code = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    VALUE = 1
    PERCENT = 2
    DISCOUNT_CHOICES = [
        (VALUE, "Value"),
        (PERCENT, "Percents"),
    ]
    discount_type = models.PositiveSmallIntegerField(
        choices=DISCOUNT_CHOICES,
        default=VALUE,
    )

    def __str__(self):
        return f"{self.code} | {self.amount} |" \
               f"{self.get_discount_type_display()}"
