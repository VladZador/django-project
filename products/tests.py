from django.urls import reverse

from orders.models import Order


def test_product_list_page_with_no_products(client):
    # Open "products list" page with no objects present
    response = client.get(reverse("product_list"))
    assert response.status_code == 200
    assert not response.context["product_list"]


def test_product_list_page(client, product):
    # Open "products list" page
    response = client.get(reverse("product_list"))
    assert response.status_code == 200
    assert response.context["product_list"].filter(id=product.id)


def test_product_detail_page(client, faker, product):
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


def test_product_detail_export_csv_page_as_unregistered_user(client, product):
    url = reverse("product_detail_export_csv", kwargs={"pk": product.id})

    # Open redirected login page
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)


def test_add_to_cart_page_as_user(login_user, faker, product):
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
    assert 'Sorry, there is no product with this uuid' in [m.message for m in list(response.context['messages'])]
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
    assert order.products.filter(id=product.id)
    assert 'Product added to your cart!' in [m.message for m in list(response.context['messages'])]


def test_add_to_favorites_page_as_user(login_user, faker, product):
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
    assert "Sorry, there is no product with this uuid" \
           in [m.message for m in list(response.context['messages'])]
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
    assert user.favorite_products.filter(id=product.id)
    assert 'Product is added to your favorite products list!' \
           in [m.message for m in list(response.context['messages'])]


def test_remove_from_favorites_page_as_user(login_user, faker, product):
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
    assert "Sorry, there is no product with this uuid" \
           in [m.message for m in list(response.context['messages'])]
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
    assert "Sorry, there is no product with this uuid" \
           in [m.message for m in list(response.context['messages'])]

    # Accessing "Remove product from the favorites" page using the POST method with correct uuid
    user.favorite_products.add(product)
    data = {"product": product.id}
    response = client.post(url, data=data, follow=True, HTTP_REFERER=referer)
    assert response.status_code == 200
    assert any(i[0] == referer for i in response.redirect_chain)
    assert not user.favorite_products.filter(id=product.id)
    assert 'Product is removed from your favorite products list' \
           in [m.message for m in list(response.context['messages'])]


def test_favorite_products_page_as_user(login_user, product):
    client, user = login_user
    url = reverse("favorite_products")

    # Open favorite products page when there's no favorite products for current user
    response = client.get(url)
    assert response.status_code == 200
    assert not response.context["favorite_products_list"]

    # Open favorite products page
    user.favorite_products.add(product)
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["favorite_products_list"].filter(id=product.id)


def test_product_list_export_csv_page_as_user(login_user, product):
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


def test_product_detail_export_csv_page_as_user(login_user, faker, product):
    client, _ = login_user

    # Redirect to "product_list" page when passing wrong uuid
    url = reverse("product_detail_export_csv", kwargs={"pk": faker.uuid4()})
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("product_list") for i in response.redirect_chain)
    assert 'Sorry, there is no product with this uuid' \
           in [m.message for m in list(response.context['messages'])]

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
