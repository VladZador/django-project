import logging
from bs4 import BeautifulSoup

from mystore.api_clients import BaseClient

logger = logging.getLogger(__name__)


class BufetParser(BaseClient):
    base_url = "https://bufet.ua/menyu/"

    def parse(self) -> list:
        response = self.get_request(
            method="get",
        )
        soup = BeautifulSoup(response, features="html.parser")
        product_list = []
        for prod_elem in soup.find_all("li", {"class": "span3"}):
            try:
                name = prod_elem.find(
                    "a", {"class": "product-name"}
                ).text.strip()
                product_list.append({
                    "name": name,
                    "description": name,
                    "image": prod_elem.find("img").attrs["src"],
                    "category": prod_elem.find("a", {"rel": "tag"}).text,
                    "price": prod_elem.find("div", {"class": "price"}).text,
                    "sku": name
                })
            except (AttributeError, KeyError) as err:
                logger.error(err)
        return product_list


bufet_parser = BufetParser()
