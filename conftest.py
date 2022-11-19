import pytest
from faker import Faker
from django.contrib.auth import get_user_model
from django.test.client import Client

from feedbacks.models import Feedback
from products.models import Product, Category

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


@pytest.fixture(scope="function")
def product(db):
    category, _ = Category.objects.get_or_create(name="Test category")
    product, _ = Product.objects.get_or_create(
        name="Lorem",
        description="Ipsum",
        category=category,
        price=20.00,
        currency=980,
        sku="dolor"
    )
    yield product


@pytest.fixture(scope="function")
def feedback(db, faker, user):
    feedback, _ = Feedback.objects.get_or_create(
        text=faker.sentence(),
        user=user,
        rating=faker.pyint(min_value=1, max_value=5)
    )
    yield feedback


@pytest.fixture(scope="function")
def user(db, faker):
    email = faker.email()
    password = faker.password()

    user, _ = User.objects.get_or_create(email=email)
    user.set_password(password)
    user.save()
    yield user


@pytest.fixture(scope="function")
def login_user(db, faker):
    email = faker.email()
    password = faker.password()

    user, _ = User.objects.get_or_create(email=email)
    user.set_password(password)
    user.save()
    client = Client()
    client.login(username=email, password=password)
    yield client, user
