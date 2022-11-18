import pytest
from faker import Faker

from products.models import Product, Category

fake = Faker()


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
