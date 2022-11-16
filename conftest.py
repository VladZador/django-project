import pytest
from faker import Faker

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
