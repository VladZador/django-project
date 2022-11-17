from django.urls import reverse


def test_products_page_with_no_products(client):
    # Open page
    response = client.get(reverse("product_list"))
    assert response.status_code == 200
    assert b"Sorry, the product list is currently empty" in response.content


def test_product_list_page_as_unregistered_user(client, product):
    response = client.get(reverse("product_list"))

    # Since both "product_list" and "product_detail" should have similar content display,
    # I have separated the tests into a function with common functionality.
    _test_product_content(product, response)

    # Since both "product_list" and "product_detail" have the same views for processing
    # actions with products, I have separated the tests into a function with common functionality.
    _test_product_redirection(client, product)


def _test_product_content(product, response):
    # Open page
    assert response.status_code == 200
    assert product.name.encode("utf-8") in response.content
    assert product.description.encode("utf-8") in response.content


def _test_product_redirection(client, product):
    # Add product to the cart
    url = reverse("add_to_cart")
    _test_get_method_redirection(client, url)
    _test_product_post_method_redirection(client, product, url)

    # Add product to the favorites
    url = reverse("update_favorite_products", kwargs={"action": "add"})
    _test_get_method_redirection(client, url)
    _test_product_post_method_redirection(client, product, url)

    # Remove product from the favorites. It's not reachable from the page, but should be covered.
    url = reverse("update_favorite_products", kwargs={"action": "remove"})
    _test_get_method_redirection(client, url)
    _test_product_post_method_redirection(client, product, url)


def _test_get_method_redirection(client, url):
    # Open redirected login page
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def _test_product_post_method_redirection(client, product, url):
    # Open redirected login page
    data = {"product": product.id}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_product_detail_page_wrong_uuid(client, faker):
    # Open 404 page
    response = client.get(reverse("product_detail", kwargs={"pk": faker.uuid4()}))
    assert response.status_code == 404


def test_product_detail_page_as_unregistered_user(client, product):
    response = client.get(reverse("product_detail", kwargs={"pk": product.id}))

    # Since both "product_list" and "product_detail" should have similar content display,
    # I have separated the tests into a function with common functionality.
    _test_product_content(product, response)

    # Since both "product_list" and "product_detail" have the same views for processing
    # actions with products, I have separated the tests into a function with common functionality.
    _test_product_redirection(client, product)


def test_product_list_export_csv_page_as_unregistered_user(client):
    url = reverse("product_list_export_csv")
    _test_get_method_redirection(client, url)


def test_product_detail_export_csv_page_as_unregistered_user(client, product):
    url = reverse("product_detail_export_csv", kwargs={"pk": product.id})
    _test_get_method_redirection(client, url)


def test_favorite_products_page_as_unregistered_user(client):
    url = reverse("favorite_products")
    _test_get_method_redirection(client, url)
