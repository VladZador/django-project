from django.urls import reverse


def test_products_page_with_no_products(client):
    # Open "products list" page with no objects present
    response = client.get(reverse("product_list"))
    assert response.status_code == 200
    assert b"Sorry, the product list is currently empty" in response.content


def test_product_list_page(client, product):
    # Open "products list" page
    response = client.get(reverse("product_list"))
    assert response.status_code == 200
    assert product.name.encode("utf-8") in response.content
    assert product.description.encode("utf-8") in response.content


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


def test_product_detail_page_wrong_uuid(client, faker):
    # Open 404 page
    response = client.get(reverse("product_detail", kwargs={"pk": faker.uuid4()}))
    assert response.status_code == 404


def test_product_detail_page(client, product):
    # Open "product detail" page
    response = client.get(reverse("product_detail", kwargs={"pk": product.id}))
    assert response.status_code == 200
    assert product.name.encode("utf-8") in response.content
    assert product.description.encode("utf-8") in response.content


def test_product_list_export_csv_page_as_unregistered_user(client):
    url = reverse("product_list_export_csv")

    # Open redirected login page
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_product_detail_export_csv_page_as_unregistered_user(client, product):
    url = reverse("product_detail_export_csv", kwargs={"pk": product.id})

    # Open redirected login page
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)
