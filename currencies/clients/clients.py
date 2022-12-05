from mystore.api_clients import BaseClient


class PrivatBankAPI(BaseClient):
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
        return self.get_request(
            "get",
            params={"exchange": "", "json": "", "coursid": 11}
        )


class MonoBankAPI(BaseClient):
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
        return self.get_request("get")


class NationalBankAPI(BaseClient):
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
        return self.get_request("get", params={"json": ""})
