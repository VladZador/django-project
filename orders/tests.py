from django.urls import reverse


def _test_get_method_for_unregistered_user(client, url):
    # Open redirected login page
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_cart_page_for_unregistered_user(client):
    url = reverse("cart")
    _test_get_method_for_unregistered_user(client, url)


def test_order_page_for_unregistered_user(client):
    url = reverse("order")
    _test_get_method_for_unregistered_user(client, url)


def test_recalculate_cart_page_for_unregistered_user(client):
    url = reverse("recalculate_cart")
    _test_get_method_for_unregistered_user(client, url)


def test_remove_product_page_for_unregistered_user(client, faker):
    url = reverse("remove_product", kwargs={"pk": faker.uuid4()})
    _test_get_method_for_unregistered_user(client, url)


def test_remove_all_products_page_for_unregistered_user(client):
    url = reverse("remove_all_products")
    _test_get_method_for_unregistered_user(client, url)


def test_add_discount_page_for_unregistered_user(client):
    url = reverse("add_discount")
    _test_get_method_for_unregistered_user(client, url)


def test_cancel_discount_page_for_unregistered_user(client):
    url = reverse("cancel_discount")
    _test_get_method_for_unregistered_user(client, url)


def test_pay_order_page_for_unregistered_user(client):
    url = reverse("pay_order")
    _test_get_method_for_unregistered_user(client, url)
