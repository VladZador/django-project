import pytest
from datetime import datetime, timedelta
from django.urls import reverse

from .models import Order, Discount
from .tasks import delete_old_pending_orders


# Block "unregistered user"

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


# Block "no order"

def test_cart_page_for_user_no_order(login_user):
    client, _ = login_user

    # Open page with no order for current user
    response = client.get(reverse("cart"))
    assert response.status_code == 200
    assert not response.context["order"]


def test_order_page_for_user_no_order(login_user):
    client, _ = login_user

    # Open page with no order for current user
    response = client.get(reverse("cart"))
    assert response.status_code == 200
    assert not response.context["order"]


def test_recalculate_cart_page_for_user_no_order(login_user, faker):
    client, _ = login_user

    # Open redirected "cart" page with no order for current user
    response = client.post(reverse("recalculate_cart"), follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("cart") for i in response.redirect_chain)
    assert not response.context["order"]


def test_remove_product_page_for_user_no_order(login_user, faker):
    client, _ = login_user
    url = reverse("remove_product", kwargs={"pk": faker.uuid4()})

    # Open redirected "cart" page with no order for current user
    response = client.post(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("cart") for i in response.redirect_chain)
    assert not response.context["order"]


def test_remove_all_products_page_for_user_no_order(login_user, faker):
    client, _ = login_user

    # Open redirected "cart" page with no order for current user
    response = client.post(reverse("remove_all_products"), follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("cart") for i in response.redirect_chain)
    assert not response.context["order"]


def test_add_discount_page_for_user_no_order(login_user, faker):
    client, _ = login_user

    # Open redirected "cart" page with no order for current user
    data = {"discount": faker.word()}
    response = client.post(reverse("add_discount"), data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("cart") for i in response.redirect_chain)
    assert not response.context["order"]
    assert "Discount not applied. Most likely, there's no active discount with this code name" \
           in [m.message for m in list(response.context['messages'])]


def test_cancel_discount_page_for_user_no_order(login_user, faker):
    client, _ = login_user

    # Open redirected "cart" page with no order for current user
    response = client.post(reverse("cancel_discount"), follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("cart") for i in response.redirect_chain)
    assert not response.context["order"]


def test_pay_order_page_for_user_no_order(login_user, faker):
    client, user = login_user

    # Open redirected "cart" page with no order for current user
    response = client.post(reverse("pay_order"), follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("product_list") for i in response.redirect_chain)
    assert not Order.objects.filter(user=user, is_active=True)


# Block "ordinary access"

def test_cart_page_for_user(login_user_with_order):
    client, _, order, _ = login_user_with_order

    # Open page with existing order for current user using the GET method
    response = client.get(reverse("cart"))
    assert response.status_code == 200
    assert response.context["order"] == order

    # Open page with existing order for current user using the POST method
    response = client.get(reverse("cart"))
    assert response.status_code == 200
    assert response.context["order"] == order


def test_order_page_for_user(login_user_with_order):
    client, _, order, _ = login_user_with_order

    # Open page with existing order for current user using the GET method
    response = client.get(reverse("order"))
    assert response.status_code == 200
    assert response.context["order"] == order

    # Open page with existing order for current user using the POST method
    response = client.get(reverse("order"))
    assert response.status_code == 200
    assert response.context["order"] == order


def test_recalculate_cart_page_for_user(login_user_with_order):
    client, user, order, product = login_user_with_order
    url = reverse("recalculate_cart")
    success_url = reverse("cart")

    # Accessing "Recalculate cart" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)

    # Accessing "Recalculate cart" page using the POST method with correct data
    data = {
        "product_0": product.id,
        "quantity_0": 5
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert order.products.through.objects.get(order=order).quantity == data["quantity_0"]


def test_remove_product_page_for_user(login_user_with_order, faker, product_factory):
    client, user, order, product_1 = login_user_with_order
    product_2 = product_factory()
    order.products.add(product_2)

    correct_url = reverse("remove_product", kwargs={"pk": product_2.id})
    wrong_url = reverse("remove_product", kwargs={"pk": faker.uuid4()})
    success_url = reverse("cart")

    # Accessing "Remove product from the cart" page using the GET method
    response = client.get(correct_url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert order.products.all().count() == 2

    # Accessing "Remove product from the cart" page using the POST method with wrong uuid
    response = client.post(wrong_url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert order.products.all().count() == 2

    # Accessing "Remove product from the cart" page using the POST method
    response = client.post(correct_url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert order.products.all().count() == 1

    # Accessing "Remove product from the cart" page using the POST method with one product left
    response = client.post(
        reverse("remove_product", kwargs={"pk": product_1.id}),
        follow=True
    )
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert not order.products.all()
    with pytest.raises(Order.DoesNotExist) as exc_info:
        order.refresh_from_db()
    assert "Order matching query does not exist" in str(exc_info.value)


def test_remove_all_products_page_for_user(login_user_with_order, product_factory):
    client, user, order, _ = login_user_with_order
    product = product_factory()
    order.products.add(product)

    url = reverse("remove_all_products")
    success_url = reverse("cart")

    # Accessing "Remove all products from the cart" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert order.products.all().count() == 2

    # Accessing "Remove all products from the cart" page using the POST method
    response = client.post(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert not order.products.all()
    with pytest.raises(Order.DoesNotExist) as exc_info:
        order.refresh_from_db()
    assert "Order matching query does not exist" in str(exc_info.value)


def test_add_discount_page_for_user(login_user_with_order, faker, discount_factory):
    client, _, order, product = login_user_with_order

    url = reverse("add_discount")
    success_url = reverse("cart")

    # Accessing "Add discount" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    order.refresh_from_db()
    assert not order.discount

    # Accessing "Add discount" page using the POST method with wrong discount code
    data = {"discount": faker.word()}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    order.refresh_from_db()
    assert not order.discount
    assert "Discount not applied. Most likely, there's no active discount with this code name" \
           in [m.message for m in list(response.context['messages'])]

    # Accessing "Add discount" page using the POST method with correct discount code
    # (discount type = value)
    discount_value = discount_factory()
    data = {"discount": discount_value.code}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    order.refresh_from_db()
    assert order.discount == discount_value
    assert order.calculate_with_discount() == round((product.price - discount_value.amount), 2)

    assert 'Discount applied!' in [m.message for m in list(response.context['messages'])]

    # Accessing "Add discount" page using the POST method with correct discount code
    # (discount type = percent)
    discount_percent = discount_factory(discount_type=Discount.PERCENT)
    data = {"discount": discount_percent.code}
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    order.refresh_from_db()
    assert order.discount == discount_percent
    assert order.calculate_with_discount() == round((product.price * (100 - discount_percent.amount)/100), 2)

    assert 'Discount applied!' in [m.message for m in list(response.context['messages'])]


def test_cancel_discount_page_for_user(login_user_with_order, faker, discount_factory):
    client, _, order, _ = login_user_with_order
    discount = discount_factory()
    order.discount = discount
    order.save(update_fields=("discount",))

    url = reverse("cancel_discount")
    success_url = reverse("cart")

    # Accessing "Cancel discount" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    order.refresh_from_db()
    assert order.discount == discount

    # Accessing "Cancel discount" page using the POST method
    response = client.post(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    order.refresh_from_db()
    assert not order.discount
    assert 'Discount not applied' in [m.message for m in list(response.context['messages'])]


def test_pay_order_page_for_user(login_user_with_order):
    client, _, order, product = login_user_with_order
    url = reverse("pay_order")
    success_url = reverse("product_list")

    # Accessing "Pay order" page using the GET method
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)

    # Accessing "Pay order" page using the POST method
    response = client.post(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == success_url for i in response.redirect_chain)
    assert not order.total_amount
    order.refresh_from_db()
    assert order.is_paid and not order.is_active
    assert order.total_amount == product.price
    assert 'Your order has been successfully processed!' \
           in [m.message for m in list(response.context['messages'])]


def test_delete_old_pending_orders(order_factory):
    assert not Order.objects.exists()
    old_order = order_factory()
    new_order = order_factory()
    old_creation_day = datetime.now() - timedelta(days=3)
    old_order.created_at = old_creation_day
    old_order.save(update_fields=("created_at",))

    delete_old_pending_orders()
    assert not Order.objects.filter(id=old_order.id)
    assert Order.objects.filter(id=new_order.id)
