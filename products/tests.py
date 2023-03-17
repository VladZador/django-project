from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from orders.models import Order
from .forms import CsvImportForm
from .models import Product, Category


def test_product_list_page_with_no_products(client):
    # Open "products list" page with no objects present
    response = client.get(reverse("product_list"))
    assert response.status_code == 200
    assert not response.context["product_list"]


def test_product_list_page(client, product_factory):
    product = product_factory()

    # Open "products list" page
    response = client.get(reverse("product_list"))
    assert response.status_code == 200
    assert product in response.context["page_obj"].object_list


def test_products_filtering(client, product_factory, faker):
    product1 = product_factory()
    product2 = product_factory()

    # Filtering by gibberish data
    name = faker.word()
    response = client.get(
        reverse("product_list") + "?name__icontains=" + name
        + "?category=" + faker.uuid4()
    )
    assert response.status_code == 200
    assert response.context['search_data'].get('name')
    assert not response.context['search_data'].get('category')
    assert not any(response.context["object_list"].values()[i]["id"] == product1.id
                   for i in range(len(response.context["object_list"].values())))
    assert not any(response.context["object_list"].values()[i]["id"] == product2.id
                   for i in range(len(response.context["object_list"].values())))

    # Filtering by one of the products
    response = client.get(
        reverse("product_list") +
        "?category=" + str(product1.category.id) +
        "&name__icontains=" + product1.name +
        "&price__gt=" + str(float(product1.price) - 1) +
        "&price__lt=" + str(float(product1.price) + 1)
    )
    assert response.status_code == 200
    assert response.context['search_data'].get('price is greater than')
    assert response.context['search_data'].get('price is less than')
    assert any(response.context["object_list"].values()[i]["id"] == product1.id
               for i in range(len(response.context["object_list"].values())))
    assert not any(response.context["object_list"].values()[i]["id"] == product2.id
                   for i in range(len(response.context["object_list"].values())))


def test_product_detail_page(client, faker, product_factory):
    product = product_factory()

    # Open 404 page when passing wrong uuid
    response = client.get(reverse("product_detail", kwargs={"pk": faker.uuid4()}))
    assert response.status_code == 404

    # Open "product detail" page
    response = client.get(reverse("product_detail", kwargs={"pk": product.id}))
    assert response.status_code == 200
    assert response.context["product"] == product


def test_add_to_cart_page_as_unregistered_user(client, faker):
    url = reverse("add_to_cart")

    # Accessing "Add product to the cart" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)

    # Accessing "Add product to the cart" page using the POST method
    data = {"product": faker.uuid4()}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_add_to_favorites_page_as_unregistered_user(client, faker):
    url = reverse("update_favorite_products", kwargs={"action": "add"})

    # Accessing "Add product to the favorites" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)

    # Accessing "Add product to the favorites" page using the POST method
    data = {"product": faker.uuid4()}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_remove_from_favorites_page_as_unregistered_user(client, faker):
    url = reverse("update_favorite_products", kwargs={"action": "remove"})

    # Accessing "Remove product from the favorites" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)

    # Accessing "Remove product from the favorites" page using the POST method
    data = {"product": faker.uuid4()}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_favorite_products_page_as_unregistered_user(client):
    url = reverse("favorite_products")

    # Open redirected login page
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_product_list_export_csv_page_as_unregistered_user(client):
    url = reverse("product_list_export_csv")

    # Open redirected login page
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_product_detail_export_csv_page_as_unregistered_user(client, faker):
    url = reverse("product_detail_export_csv", kwargs={"pk": faker.uuid4()})

    # Open redirected login page
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_import_products_from_csv_page_as_unregistered_user(client):
    url = reverse("admin:import_products_csv")

    # Open redirected login page - it requires staff status
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("admin:login") + f"?next={url}" for i in response.redirect_chain)


def test_add_to_cart_page_as_user(login_user, faker, product_factory):
    product = product_factory()
    client, user = login_user
    url = reverse("add_to_cart")
    success_url = reverse("product_list")

    # Accessing "Add product to the cart" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert not Order.objects.exists()

    # Accessing "Add product to the cart" page using the POST method with wrong uuid
    data = {"product": faker.uuid4()}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert "error" in [m.level_tag for m in list(response.context['messages'])]
    assert Order.objects.exists()
    order = Order.objects.get(user=user)
    assert not order.products.all()
    order.delete()

    # Accessing "Add product to the cart" page using the POST method with correct uuid
    data = {"product": product.id}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert Order.objects.exists()
    order = Order.objects.get(user=user)
    assert order.products.filter(id=product.id).exists()
    assert "success" in [m.level_tag for m in list(response.context['messages'])]


def test_add_to_favorites_page_as_user(login_user, faker, product_factory):
    product = product_factory()
    client, user = login_user
    url = reverse("update_favorite_products", kwargs={"action": "add"})
    referer = reverse("product_list")

    # Accessing "Add product to the favorites" page using the GET method
    response = client.get(url, follow=True, HTTP_REFERER=referer)
    assert response.status_code == 200
    assert any(i[0] == referer for i in response.redirect_chain)
    assert not user.favorite_products.all()

    # Accessing "Add product to the favorites" page using the POST method with wrong uuid
    data = {"product": faker.uuid4()}
    response = client.post(url, data=data, follow=True, HTTP_REFERER=referer)
    assert response.status_code == 200
    assert any(i[0] == referer for i in response.redirect_chain)
    assert "error" in [m.level_tag for m in list(response.context['messages'])]
    assert not user.favorite_products.all()

    # Accessing "Add product to the favorites" page using the POST method without the referer
    data = {"product": faker.uuid4()}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("favorite_products") for i in response.redirect_chain)

    # Accessing "Add product to the favorites" page using the POST method with correct uuid
    data = {"product": product.id}
    response = client.post(url, data=data, follow=True, HTTP_REFERER=referer)
    assert response.status_code == 200
    assert any(i[0] == referer for i in response.redirect_chain)
    assert user.favorite_products.filter(id=product.id).exists()
    assert "info" in [m.level_tag for m in list(response.context['messages'])]


def test_remove_from_favorites_page_as_user(login_user, faker, product_factory):
    product = product_factory()
    client, user = login_user
    url = reverse("update_favorite_products", kwargs={"action": "remove"})
    referer = reverse("product_list")

    # Accessing "Remove product from the favorites" page using the GET method
    response = client.get(url, follow=True, HTTP_REFERER=referer)
    assert response.status_code == 200
    assert any(i[0] == referer for i in response.redirect_chain)
    assert not user.favorite_products.all()

    # Accessing "Remove product from the favorites" page using the POST method with wrong uuid
    data = {"product": faker.uuid4()}
    response = client.post(url, data=data, follow=True, HTTP_REFERER=referer)
    assert response.status_code == 200
    assert any(i[0] == referer for i in response.redirect_chain)
    assert "error" in [m.level_tag for m in list(response.context['messages'])]
    assert not user.favorite_products.all()

    # Accessing "Remove product from the favorites" page using the POST method without the referer
    data = {"product": faker.uuid4()}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("favorite_products") for i in response.redirect_chain)

    # Accessing "Remove product from the favorites" page using the POST method with correct uuid,
    # but the product is not in "user.favorite_products"
    data = {"product": product.id}
    response = client.post(url, data=data, follow=True, HTTP_REFERER=referer)
    assert response.status_code == 200
    assert any(i[0] == referer for i in response.redirect_chain)
    assert not user.favorite_products.all()
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Accessing "Remove product from the favorites" page using the POST method with correct uuid
    user.favorite_products.add(product)
    data = {"product": product.id}
    response = client.post(url, data=data, follow=True, HTTP_REFERER=referer)
    assert response.status_code == 200
    assert any(i[0] == referer for i in response.redirect_chain)
    assert not user.favorite_products.filter(id=product.id).exists()
    assert "info" in [m.level_tag for m in list(response.context['messages'])]


def test_favorite_products_page_as_user(login_user, product_factory):
    product = product_factory()
    client, user = login_user
    url = reverse("favorite_products")

    # Open favorite products page when there's no favorite products for current user
    response = client.get(url)
    assert response.status_code == 200
    assert not response.context["page_obj"]

    # Open favorite products page
    user.favorite_products.add(product)
    response = client.get(url)
    assert response.status_code == 200
    assert product in response.context["page_obj"].object_list


def test_product_list_export_csv_page_as_user(login_user, product_factory):
    product = product_factory()
    client, _ = login_user
    url = reverse("product_list_export_csv")

    # Access page
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == 'text/csv'
    assert response.headers["content-disposition"] == 'attachment; filename="products.csv"'
    assert b'name,description,category,price,currency,sku,image' in response.content
    assert f"{product.name},{product.description},{product.category},{product.price:.2f}," \
           f"{product.currency},{product.sku},No image".encode("utf-8") \
           in response.content


def test_product_detail_export_csv_page_as_user(login_user, faker, product_factory):
    product = product_factory()
    client, _ = login_user

    # Redirect to "product_list" page when passing wrong uuid
    url = reverse("product_detail_export_csv", kwargs={"pk": faker.uuid4()})
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("product_list") for i in response.redirect_chain)
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Access page when passing correct uuid
    url = reverse("product_detail_export_csv", kwargs={"pk": product.id})
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == 'text/csv'
    assert response.headers["content-disposition"] == \
           f'attachment;filename="product-{product.id}.csv"'
    assert b'name,description,category,price,currency,sku,image' in response.content
    assert f"{product.name},{product.description},{product.category},{product.price:.2f}," \
           f"{product.currency},{product.sku},No image".encode("utf-8") \
           in response.content


def test_import_products_from_csv_page_as_user(login_user, faker):
    client, _ = login_user
    url = reverse("admin:import_products_csv")

    # Open redirected login page - it requires staff status
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("admin:login") + f"?next={url}" for i in response.redirect_chain)


def test_import_products_from_csv_page_as_admin(admin_client, faker):
    url = reverse("admin:import_products_csv")

    # Access page
    response = admin_client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context["form"], CsvImportForm)

    # Post an empty data
    response = admin_client.post(url, follow=True)
    assert response.status_code == 200
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Post a file with wrong extension
    data = {"csv_import": SimpleUploadedFile("file.txt", b"content")}
    response = admin_client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Post a file with dummy data (or some of the headers are missing)
    data = {"csv_import": SimpleUploadedFile("file.csv", b"content", content_type="text/csv")}
    response = admin_client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert not Product.objects.exists()
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Post a file with some absent value data (no product sku)
    future_product = {
        "name": faker.word(),
        "description": faker.sentence(),
        "category": faker.word(),
        "price": faker.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=10),
        "currency": 980,
    }
    file_content = f"name,description,category,price,currency,sku\n" \
                   f"{future_product['name']},{future_product['description']}," \
                   f"{future_product['category']},{future_product['price']}," \
                   f"{future_product['currency']}".encode("utf-8")
    data = {"csv_import": SimpleUploadedFile("file.csv", file_content, content_type="text/csv")}

    response = admin_client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert not Product.objects.exists()
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Post a file with wrong data type (price)
    future_product = {
        "name": faker.word(),
        "description": faker.sentence(),
        "category": faker.word(),
        "price": faker.word(),
        "currency": 980,
        "sku": faker.word(),
    }
    file_content = f"name,description,category,price,currency,sku\n" \
                   f"{future_product['name']},{future_product['description']}," \
                   f"{future_product['category']},{future_product['price']}," \
                   f"{future_product['currency']},{future_product['sku']}".encode("utf-8")
    data = {"csv_import": SimpleUploadedFile("file.csv", file_content, content_type="text/csv")}

    response = admin_client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert not Product.objects.exists()
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Post a file with correct data
    future_product = {
        "name": faker.word(),
        "description": faker.sentence(),
        "category": faker.word(),
        "price": faker.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=10),
        "currency": 980,
        "sku": faker.word()
    }
    file_content = f"name,description,category,price,currency,sku\n" \
                   f"{future_product['name']},{future_product['description']}," \
                   f"{future_product['category']},{future_product['price']}," \
                   f"{future_product['currency']},{future_product['sku']}".encode("utf-8")
    data = {"csv_import": SimpleUploadedFile("file.csv", file_content, content_type="text/csv")}

    response = admin_client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert Category.objects.filter(name=future_product["category"]).exists()
    category = Category.objects.get(name=future_product["category"])
    assert Product.objects.filter(
        name=future_product["name"],
        description=future_product["description"],
        category=category,
        price=future_product["price"],
        currency=future_product["currency"],
        sku=future_product["sku"]
    ).exists()
    assert "success" in [m.level_tag for m in list(response.context['messages'])]
