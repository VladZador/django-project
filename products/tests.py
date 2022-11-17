from django.urls import reverse


def test_products_page_as_unregistered_user(client, product):
    # Open page
    response = client.get(reverse("product_list"))
    assert response.status_code == 200
    assert product.name.encode("utf-8") in response.content
    assert product.description.encode("utf-8") in response.content

    # Add product to the cart
    add_to_cart_url = reverse("add_to_cart")
    data = {"product": product.id}
    response = client.post(add_to_cart_url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={add_to_cart_url}" for i in response.redirect_chain)

    # Add product to the favorites
    add_to_favorites_url = reverse("star_product", kwargs={"action": "add"})
    data = {"product": product.id}
    response = client.post(add_to_favorites_url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={add_to_favorites_url}" for i in response.redirect_chain)
    breakpoint()
