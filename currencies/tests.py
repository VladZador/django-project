from datetime import datetime, timedelta

from .models import CurrencyHistory
from .tasks import get_currencies, get_currencies_from_bank, delete_old_currencies


def test_get_currencies_from_bank_task(mocker):
    # Test get_currencies_from_bank("privat")
    assert not CurrencyHistory.objects.exists()
    get_currency_privat_mocker = mocker.patch("currencies.tasks.CurrencyClient.privat.get_currency")
    get_currency_privat_mocker.return_value = [
            {"ccy": "EUR", "buy": "1", "sale": "2"},
            {"ccy": "USD", "buy": "3", "sale": "4"},
    ]
    assert not get_currency_privat_mocker.call_count

    get_currencies_from_bank("privat")

    assert get_currency_privat_mocker.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=1, sale=2).exists()
    assert CurrencyHistory.objects.filter(currency=840, buy=3, sale=4).exists()
    CurrencyHistory.objects.all().delete()

    # Test get_currencies_from_bank("mono")
    assert not CurrencyHistory.objects.exists()
    get_currency_mono_mocker = mocker.patch("currencies.tasks.CurrencyClient.mono.get_currency")
    get_currency_mono_mocker.return_value = [
        {"currencyCodeA": 978, "currencyCodeB": 980, "rateBuy": 5, "rateSell": 6},
        {"currencyCodeA": 840, "currencyCodeB": 980, "rateBuy": 7, "rateSell": 8},
    ]
    assert not get_currency_mono_mocker.call_count

    get_currencies_from_bank("mono")

    assert get_currency_mono_mocker.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=5, sale=6).exists()
    assert CurrencyHistory.objects.filter(currency=840, buy=7, sale=8).exists()
    CurrencyHistory.objects.all().delete()

    # Test get_currencies_from_bank("national")
    assert not CurrencyHistory.objects.exists()
    get_currency_national_mocker = mocker.patch("currencies.tasks.CurrencyClient.national.get_currency")
    get_currency_national_mocker.return_value = [
        {"r030": 978, "rate": 9},
        {"r030": 840, "rate": 10},
    ]
    assert not get_currency_national_mocker.call_count

    get_currencies_from_bank("national")

    assert get_currency_national_mocker.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=9, sale=9).exists()
    assert CurrencyHistory.objects.filter(currency=840, buy=10, sale=10).exists()
    CurrencyHistory.objects.all().delete()


def test_delete_old_currencies_task(currency_history_factory):
    assert not CurrencyHistory.objects.exists()
    old_currency_history = currency_history_factory()
    new_currency_history = currency_history_factory()
    old_creation_day = datetime.now() - timedelta(days=1)
    old_currency_history.created_at = old_creation_day
    old_currency_history.save(update_fields=("created_at",))

    delete_old_currencies()
    assert not CurrencyHistory.objects.filter(id=old_currency_history.id).exists()
    assert CurrencyHistory.objects.filter(id=new_currency_history.id).exists()


def test_get_currencies_task_first_try(mocker):
    # First try - privat
    assert not CurrencyHistory.objects.exists()
    get_currency_privat_mocker = mocker.patch("currencies.tasks.CurrencyClient.privat.get_currency")
    get_currency_privat_mocker.return_value = [
            {"ccy": "EUR", "buy": "1", "sale": "2"},
            {"ccy": "USD", "buy": "3", "sale": "4"},
    ]
    assert not get_currency_privat_mocker.call_count

    get_currencies()

    assert get_currency_privat_mocker.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=1, sale=2).exists()
    assert CurrencyHistory.objects.filter(currency=840, buy=3, sale=4).exists()


def test_get_currencies_task_second_try(mocker):
    # First try - privat. Returns wrong data
    assert not CurrencyHistory.objects.exists()
    get_currency_privat_mocker = mocker.patch("currencies.tasks.CurrencyClient.privat.get_currency")
    get_currency_privat_mocker.return_value = [
        {"error": "Wrong request"}
    ]
    assert not get_currency_privat_mocker.call_count

    # Second try - mono
    get_currency_mono_mocker = mocker.patch("currencies.tasks.CurrencyClient.mono.get_currency")
    get_currency_mono_mocker.return_value = [
        {"currencyCodeA": 978, "currencyCodeB": 980, "rateBuy": 5, "rateSell": 6},
        {"currencyCodeA": 840, "currencyCodeB": 980, "rateBuy": 7, "rateSell": 8},
    ]
    assert not get_currency_mono_mocker.call_count

    get_currencies()

    assert get_currency_privat_mocker.call_count
    assert get_currency_mono_mocker.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=5, sale=6).exists()
    assert CurrencyHistory.objects.filter(currency=840, buy=7, sale=8).exists()


def test_get_currencies_task_third_try(mocker):
    # First try - privat. Returns wrong data
    assert not CurrencyHistory.objects.exists()
    get_currency_privat_mocker = mocker.patch("currencies.tasks.CurrencyClient.privat.get_currency")
    get_currency_privat_mocker.return_value = [
        {"error": "Wrong request"}
    ]
    assert not get_currency_privat_mocker.call_count

    # Second try - mono. Returns wrong data
    get_currency_mono_mocker = mocker.patch("currencies.tasks.CurrencyClient.mono.get_currency")
    get_currency_mono_mocker.return_value = [
        {"error": "Wrong request"}
    ]
    assert not get_currency_mono_mocker.call_count

    # Third try - national
    get_currency_national_mocker = mocker.patch("currencies.tasks.CurrencyClient.national.get_currency")
    get_currency_national_mocker.return_value = [
        {"r030": 978, "rate": 9},
        {"r030": 840, "rate": 10},
    ]
    assert not get_currency_national_mocker.call_count

    get_currencies()

    assert get_currency_privat_mocker.call_count
    assert get_currency_mono_mocker.call_count
    assert get_currency_national_mocker.call_count
    assert CurrencyHistory.objects.filter(currency=978, buy=9, sale=9).exists()
    assert CurrencyHistory.objects.filter(currency=840, buy=10, sale=10).exists()
