from requests import request


class GetCurrencyBaseClient:
    base_url = None

    def _request(self,
                 method: str,
                 params: dict = None,
                 headers: dict = None,
                 data: dict = None):
        try:
            response = request(
                url=self.base_url,
                method=method,
                params=params or {},
                headers=headers or {},
                data=data or {}
            )
        except Exception:
            ...
            # todo: Add the errors logging, when we learn about them
        else:
            return response.json()


class PrivatBankAPI(GetCurrencyBaseClient):
    base_url = "https://api.privatbank.ua/p24api/pubinfo"

    def get_currency(self) -> list:
        """
        [
            {
            "ccy":"EUR",
            "base_ccy":"UAH",
            "buy":"19.20000",
            "sale":"20.00000"
            }
        ]
        """
        return self._request(
            "get",
            params={"exchange": "", "json": "", "coursid": 11}
        )


class MonoBankAPI(GetCurrencyBaseClient):
    base_url = "https://api.monobank.ua/bank/currency"

    def get_currency(self) -> list:
        """
        [
            {
            "currencyCodeA": 840,
            "currencyCodeB": 980,
            "date": 1552392228,
            "rateSell": 27,
            "rateBuy": 27.2,
            "rateCross": 27.1
            }
        ]
        """
        return self._request("get")


class NationalBankAPI(GetCurrencyBaseClient):
    base_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"

    def get_currency(self) -> list:
        """
        [
            {
            "r030":840,
            "txt":"Долар США",
            "rate":36.5686,
            "cc":"USD",
            "exchangedate":"02.11.2022"
            }
        ]
        """
        return self._request(
            "get",
            params={"json": ""}
        )
