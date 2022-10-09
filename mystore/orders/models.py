from django.db import models
from django.contrib.auth import get_user_model

from mystore.mystore.mixins.model_mixins import PKMixin
from mystore.items.models import Product


class Order(PKMixin):
    products = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
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

    def calculate_with_discount(self):
        """
        Calculates the total price of the order when
        the discount is applied.
        :return: total_amount
        """
        if self.discount:
            if self.discount.discount_type == Discount.VALUE:
                self.total_amount = self.total_amount - self.discount.amount
            else:
                self.total_amount = self.total_amount * (1 - self.discount.amount/100)
        return self.total_amount if self.total_amount > 0 else 0


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
        return f"{self.code} | {self.amount} | {self.get_discount_type_display()}"
