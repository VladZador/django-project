import pytest
from pytest_factoryboy import register
from faker import Faker
from django.contrib.auth import get_user_model
from django.test.client import Client

from mystore.factories import (
    CategoryFactory, DiscountFactory, FeedbackFactory, OrderFactory,
    ProductFactory, UserFactory, CurrencyHistoryFactory
)

fake = Faker()
User = get_user_model()


@pytest.fixture(scope="session")
def faker():
    yield fake


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    from pprint import pp
    __builtins__['pp'] = pp
    # code before tests run
    yield
    del __builtins__['pp']
    # code after tests run


register(UserFactory)
register(CategoryFactory)
register(ProductFactory)
register(FeedbackFactory)
register(DiscountFactory)
register(OrderFactory)
register(CurrencyHistoryFactory)


@pytest.fixture(scope="function")
def user_and_password(db, faker, user_factory):
    user = user_factory(
        phone=faker.phone_number(),
        is_phone_valid=True
    )
    password = faker.password()
    user.set_password(password)
    user.is_active = True
    user.save()
    yield user, password


@pytest.fixture(scope="function")
def login_user(db, user_and_password):
    user, password = user_and_password
    client = Client()
    client.login(username=user.email, password=password)
    yield client, user


@pytest.fixture(scope="function")
def login_user_with_order(db, login_user, order_factory, product_factory):
    client, user = login_user

    order = order_factory(user=user)
    product = product_factory()
    order.products.add(product)
    yield client, user, order, product
