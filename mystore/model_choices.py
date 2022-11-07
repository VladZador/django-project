from django.db import models


class Currencies(models.IntegerChoices):
    USD = 840, "USD"
    EUR = 978, "EUR"
    UAH = 980, "UAH"
