from datetime import datetime, timedelta

from .models import CurrencyHistory
from .tasks import get_currencies, get_currencies_from_bank, delete_old_currencies


# todo №1: Test whether delete_old_currencies is called within this task
# todo №2: Also test whether second and third "get_currencies_from_bank" tasks are called

def test_get_currencies_task(mocker):
    assert not CurrencyHistory.objects.exists()
    get_currency_privat = mocker.patch("currencies.tasks.CurrencyClient.privat.get_currency")
    get_currency_privat.return_value = [
            {"ccy": "EUR", "buy": "1", "sale": "2"},
            {"ccy": "USD", "buy": "3", "sale": "4"},
    ]
    assert not get_currency_privat.call_count

    get_currencies()

    assert get_currency_privat.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=1, sale=2)
    assert CurrencyHistory.objects.filter(currency=840, buy=3, sale=4)


def test_get_currencies_from_bank_task(mocker):
    # Test get_currencies_from_bank("privat")
    assert not CurrencyHistory.objects.exists()
    get_currency_privat = mocker.patch("currencies.tasks.CurrencyClient.privat.get_currency")
    get_currency_privat.return_value = [
            {"ccy": "EUR", "buy": "1", "sale": "2"},
            {"ccy": "USD", "buy": "3", "sale": "4"},
    ]
    assert not get_currency_privat.call_count

    get_currencies_from_bank("privat")

    assert get_currency_privat.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=1, sale=2)
    assert CurrencyHistory.objects.filter(currency=840, buy=3, sale=4)
    CurrencyHistory.objects.all().delete()

    # Test get_currencies_from_bank("mono")
    assert not CurrencyHistory.objects.exists()
    get_currency_mono = mocker.patch("currencies.tasks.CurrencyClient.mono.get_currency")
    get_currency_mono.return_value = [
        {"currencyCodeA": 978, "currencyCodeB": 980, "rateBuy": 5, "rateSell": 6},
        {"currencyCodeA": 840, "currencyCodeB": 980, "rateBuy": 7, "rateSell": 8},
    ]
    assert not get_currency_mono.call_count

    get_currencies_from_bank("mono")

    assert get_currency_mono.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=5, sale=6)
    assert CurrencyHistory.objects.filter(currency=840, buy=7, sale=8)
    CurrencyHistory.objects.all().delete()

    # Test get_currencies_from_bank("national")
    assert not CurrencyHistory.objects.exists()
    get_currency_national = mocker.patch("currencies.tasks.CurrencyClient.national.get_currency")
    get_currency_national.return_value = [
        {"r030": 978, "rate": 9},
        {"r030": 840, "rate": 10},
    ]
    assert not get_currency_national.call_count

    get_currencies_from_bank("national")

    assert get_currency_national.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=9, sale=9)
    assert CurrencyHistory.objects.filter(currency=840, buy=10, sale=10)
    CurrencyHistory.objects.all().delete()


def test_delete_old_currencies_task(currency_history_factory):
    assert not CurrencyHistory.objects.exists()
    old_currency_history = currency_history_factory()
    new_currency_history = currency_history_factory()
    old_creation_day = datetime.now() - timedelta(days=1)
    old_currency_history.created_at = old_creation_day
    old_currency_history.save(update_fields=("created_at",))

    delete_old_currencies()
    assert not CurrencyHistory.objects.filter(id=old_currency_history.id)
    assert CurrencyHistory.objects.filter(id=new_currency_history.id)
