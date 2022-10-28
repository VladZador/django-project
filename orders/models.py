from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F, Case, When, Sum

from mystore.mixins.model_mixins import PKMixin
from products.models import Product


class Order(PKMixin):
    products = models.ManyToManyField(Product, through="OrderProductRelation")
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
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

    # todo: check if this is necessary. Maybe without a constraint user
    #  won't be able to pay the second order with the same products and
    #  their quantities
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['user'],
    #                                 condition=models.Q(is_active=True),
    #                                 name='unique_is_active')
    #     ]

    # todo: think about different functions to display total price with and without the discount
    # def calculate_total_amount(self):
    #     """
    #     Calculates the total price of the order with(out) the discount.
    #
    #     :return: total_amount
    #     """
    #     self.total_amount = 0
    #     for product in self.products.all():
    #         self.total_amount += product.price
    #
    #     if self.discount:
    #         if self.discount.discount_type == Discount.VALUE:
    #             self.total_amount = self.total_amount - self.discount.amount
    #         else:
    #             self.total_amount = self.total_amount * \
    #                                 (1 - self.discount.amount/100)
    #     total = self.total_amount.quantize(Decimal('.01'))
    #     return total if total > 0 else 0

    def calculate_total_amount(self):
        """Calculates the total price of the order without the discount."""
        return self.products.through.objects.aggregate(
            total_price=Sum(F('product__price') * F('quantity'))
                ).get('total_price') or 0

    def calculate_with_discount(self):
        """Calculates the total price of the order with the discount."""
        return self.products.through.objects.annotate(
            full_price=F('product__price') * F('quantity')
                ).aggregate(
            total_amount=Case(
                When(
                    order__discount__discount_type=Discount.VALUE,
                    then=Sum(F("full_price")) - F('order__discount__amount')
                ),
                When(
                    order__discount__discount_type=Discount.PERCENT,
                    then=Sum(F("full_price")) * (1 - F('order__discount__amount') / 100)
                ),
                default=Sum(F("full_price")),
                output_field=models.DecimalField()
            )
        ).get('total_amount') or 0


class OrderProductRelation(models.Model):
    """
    Intermediate table to connect the Order and Product models with
    Many-to-Many relation with extra products quantity parameter.
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
