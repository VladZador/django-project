from datetime import timedelta
from time import sleep

from celery import shared_task, states
from celery.result import AsyncResult
from django.utils import timezone

from mystore.celery import app
from .clients.clients import (
    privat_currency_client, mono_currency_client, national_currency_client
)
from .models import CurrencyHistory


@app.task
def delete_old_currencies():
    CurrencyHistory.objects.filter(
        created_at__lt=timezone.now() - timedelta(hours=12)
    ).delete()


@app.task
def get_currencies_privat():
    currency_list = privat_currency_client.get_currency()
    currency_history_list = []
    for currency_dict in currency_list:
        try:
            if currency_dict["ccy"] \
                    in [i[1] for i in CurrencyHistory.CURRENCY_CHOICES]:
                for i in CurrencyHistory.CURRENCY_CHOICES:
                    # Changes the text currency code to an integer code
                    if currency_dict["ccy"] == i[1]:
                        currency_dict["ccy"] = i[0]
                currency_history_list.append(
                    CurrencyHistory(
                        currency=currency_dict["ccy"],
                        buy=currency_dict["buy"],
                        sale=currency_dict["sale"],
                    )
                )
        except (KeyError, ValueError, TypeError):
            ...
            # todo: Add the errors logging, when we learn about them.
            #  Check if "AsyncResult(id).state" returns failure when
            #  handling the exception
    if currency_history_list:
        CurrencyHistory.objects.bulk_create(currency_history_list)
        delete_old_currencies.delay()


@app.task
def get_currencies_mono():
    currency_list = mono_currency_client.get_currency()
    currency_history_list = []
    for currency_dict in currency_list:
        try:
            if currency_dict["currencyCodeA"]\
                    in [i[0] for i in CurrencyHistory.CURRENCY_CHOICES]\
                    and currency_dict["currencyCodeB"] == CurrencyHistory.UAH:
                currency_history_list.append(
                    CurrencyHistory(
                        currency=currency_dict["currencyCodeA"],
                        buy=currency_dict["rateBuy"],
                        sale=currency_dict["rateSell"],
                    )
                )
        except (KeyError, ValueError, TypeError):
            ...
            # todo: Add the errors logging, when we learn about them.
            #  Check if "AsyncResult(id).state" returns failure when
            #  handling the exception
    if currency_history_list:
        CurrencyHistory.objects.bulk_create(currency_history_list)
        delete_old_currencies.delay()


@app.task
def get_currencies_national():
    currency_list = national_currency_client.get_currency()
    currency_history_list = []
    for currency_dict in currency_list:
        try:
            if currency_dict["r030"] \
                    in [i[0] for i in CurrencyHistory.CURRENCY_CHOICES]:
                currency_history_list.append(
                    CurrencyHistory(
                        currency=currency_dict["r030"],
                        buy=currency_dict["rate"],
                        sale=currency_dict["rate"],
                    )
                )
        except (KeyError, ValueError, TypeError):
            ...
            # todo: Add the errors logging, when we learn about them.
            #  Check if "AsyncResult(id).state" returns failure when
            #  handling the exception
    if currency_history_list:
        CurrencyHistory.objects.bulk_create(currency_history_list)
        delete_old_currencies.delay()


# Надеюсь, нормально, что я добавил небольшое ожидание в виде "sleep(5)".
# Мне показалось, что способ с проверкой статуса наиболее оптимальный.
@shared_task
def get_currencies_from_bank():
    first_try = get_currencies_privat.delay()
    sleep(5)
    if AsyncResult(first_try.id).state == states.FAILURE:
        second_try = get_currencies_mono.delay()
        sleep(5)
        if AsyncResult(second_try.id).state == states.FAILURE:
            get_currencies_national.delay()
