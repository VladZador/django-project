from django.urls import reverse


def test_cart_page_for_unregistered_user(client):
    # Open redirected login page
    url = reverse("cart")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_order_page_for_unregistered_user(client):
    # Open redirected login page
    url = reverse("order")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_recalculate_cart_page_for_unregistered_user(client):
    # Open redirected login page
    url = reverse("recalculate_cart")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_remove_product_page_for_unregistered_user(client, faker):
    # Open redirected login page
    url = reverse("remove_product", kwargs={"pk": faker.uuid4()})
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_remove_all_products_page_for_unregistered_user(client):
    # Open redirected login page
    url = reverse("remove_all_products")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_add_discount_page_for_unregistered_user(client):
    # Open redirected login page
    url = reverse("add_discount")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_cancel_discount_page_for_unregistered_user(client):
    # Open redirected login page
    url = reverse("cancel_discount")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_pay_order_page_for_unregistered_user(client):
    # Open redirected login page
    url = reverse("pay_order")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)
