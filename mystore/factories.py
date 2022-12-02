import factory
from faker import Faker
from django.contrib.auth import get_user_model

from feedbacks.models import Feedback
from orders.models import Discount, Order
from products.models import Category, Product

User = get_user_model()
fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.LazyFunction(fake.email)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("name",)

    name = factory.LazyFunction(fake.word)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
        django_get_or_create = ("name", "category")

    name = factory.LazyFunction(fake.word)
    category = factory.SubFactory(CategoryFactory)
    price = factory.Sequence(lambda _: fake.pydecimal(
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=10
    ))
    sku = factory.LazyFunction(fake.word)


class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feedback
        django_get_or_create = ("text", "user")

    text = factory.LazyFunction(fake.sentence)
    user = factory.SubFactory(UserFactory)
    rating = factory.Sequence(lambda _: fake.pyint(min_value=1, max_value=5))


class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Discount
        django_get_or_create = ("code",)

    amount = factory.Sequence(lambda _: fake.pyint(min_value=1, max_value=10))
    code = factory.LazyFunction(fake.word)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
