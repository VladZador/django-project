import io

from django.core.files.images import ImageFile

from mystore.celery import app
from mystore.api_clients import BaseClient
from products.clients.clients import bufet_parser
from products.models import Category, Product


@app.task
def parse_bufet(product_list: list):
    if product_list:
        for product_dict in product_list:
            category, _ = Category.objects.get_or_create(
                name=product_dict["category"]
            )
            request_client = BaseClient()
            if "https://bufet.ua" in product_dict["image"]:
                image_url = product_dict["image"]
            else:
                image_url = "https://bufet.ua" + product_dict["image"]
            response = request_client.get_request(
                method="get",
                url=image_url,
            )
            image = ImageFile(io.BytesIO(response), name="image.jpg")
            price = "".join(i for i in product_dict["price"] if i.isdigit())
            product, created = Product.objects.get_or_create(
                name=product_dict["name"],
                category=category,
                defaults={
                    "description": product_dict["description"],
                    "image": image,
                    "price": price,
                    "sku": product_dict["sku"],
                }
            )
            if not created:
                product.price = price
                product.image = image
                product.save(update_fields=("price", "image"))


@app.task
def launch_bufet_parsing():
    parse_bufet.delay(bufet_parser.parse())
