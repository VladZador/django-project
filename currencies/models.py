from django.db import models

from mystore.mixins.model_mixins import PKMixin
from mystore.model_choices import Currencies


class CurrencyHistory(PKMixin):
    currency = models.PositiveSmallIntegerField(
        choices=Currencies.choices
    )
    buy = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    sale = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    class Meta:
        verbose_name_plural = "Currency histories"

    def __str__(self):
        return f"{self.get_currency_display()} | {self.sale} | " \
               f"{self.created_at}"
