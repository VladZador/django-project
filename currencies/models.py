from django.db import models

from mystore.mixins.model_mixins import PKMixin


class CurrencyHistory(PKMixin):
    USD = 840
    EUR = 978
    UAH = 980
    CURRENCY_CHOICES = [
        (USD, "USD"),
        (EUR, "EUR"),
        (UAH, "UAH"),
    ]
    currency = models.PositiveSmallIntegerField(
        choices=CURRENCY_CHOICES,
        default=USD,
    )
    buy = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=1
    )
    sale = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=1
    )

    class Meta:
        verbose_name_plural = "Currency histories"

    def __str__(self):
        return f"{self.get_currency_display()} | {self.sale} | " \
               f"{self.created_at}"
