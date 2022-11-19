from django.urls import reverse

from .models import CurrencyHistory
from .tasks import get_currencies

#
# def test_get_currencies_task(client):
#     assert not CurrencyHistory.objects.exists()
#     get_currencies()
#     assert CurrencyHistory.objects.exists()
