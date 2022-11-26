from datetime import timedelta
from time import sleep

from celery import shared_task, states
from celery.result import AsyncResult
from django.utils import timezone

from mystore.celery import app
from mystore.model_choices import Currencies
from .clients.clients import MonoBankAPI, NationalBankAPI, PrivatBankAPI
from .models import CurrencyHistory


@app.task
def delete_old_currencies():
    CurrencyHistory.objects.filter(
        created_at__lt=timezone.now() - timedelta(hours=12)
    ).delete()


class CurrencyClient:
    available_banks = ("privat", "mono", "national")
    privat = PrivatBankAPI()
    mono = MonoBankAPI()
    national = NationalBankAPI()


class CurrenciesCreator:
    @staticmethod
    def privat(currency_dict, currency_history_list):
        if currency_dict["ccy"] in [i.label for i in Currencies]:
            for i in Currencies:
                # Changes the text currency code to an integer code
                if currency_dict["ccy"] == i.label:
                    currency_dict["ccy"] = i.value
            currency_history_list.append(
                CurrencyHistory(
                    currency=currency_dict["ccy"],
                    buy=currency_dict["buy"],
                    sale=currency_dict["sale"],
                )
            )
        return currency_history_list

    @staticmethod
    def mono(currency_dict, currency_history_list):
        if currency_dict["currencyCodeA"] in [i.value for i in Currencies] \
                and currency_dict["currencyCodeB"] == Currencies.UAH.value:
            currency_history_list.append(
                CurrencyHistory(
                    currency=currency_dict["currencyCodeA"],
                    buy=currency_dict["rateBuy"],
                    sale=currency_dict["rateSell"],
                )
            )
        return currency_history_list

    @staticmethod
    def national(currency_dict, currency_history_list):
        if currency_dict["r030"] in [i.value for i in Currencies]:
            currency_history_list.append(
                CurrencyHistory(
                    currency=currency_dict["r030"],
                    buy=currency_dict["rate"],
                    sale=currency_dict["rate"],
                )
            )
        return currency_history_list


@app.task
def get_currencies_from_bank(bank_name: str):
    """
    :param bank_name: "privat", "mono" or "national"
    """
    client = CurrencyClient()
    if bank_name not in client.available_banks:
        raise ValueError('bank name should be "privat", "mono" or "national"')
    currency_list = getattr(client, bank_name).get_currency()
    currency_history_list = []
    creator = CurrenciesCreator()
    try:
        for currency_dict in currency_list:
            currency_history_list = getattr(
                creator, bank_name
            )(currency_dict, currency_history_list)
    except (KeyError, ValueError, TypeError):
        ...
        # todo: Add the errors logging, when we learn about them.
        #  Check if "AsyncResult(id).state" returns failure when
        #  handling the exception
    if currency_history_list:
        CurrencyHistory.objects.bulk_create(currency_history_list)
        delete_old_currencies.delay()


@shared_task
def get_currencies():
    try:
        first_try = get_currencies_from_bank.delay("privat")
        sleep(5)
        if AsyncResult(first_try.id).state == states.FAILURE:
            second_try = get_currencies_from_bank.delay("mono")
            sleep(5)
            if AsyncResult(second_try.id).state == states.FAILURE:
                get_currencies_from_bank.delay("national")
    except ValueError:
        ...
        # todo: Add the errors logging, when we learn about them.
