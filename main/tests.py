import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_main_page(client):
    response = client.get(reverse("main"))
    assert response.status_code == 200
    assert b"Hello! And welcome" in response.content
    breakpoint()


@pytest.mark.django_db
def test_contact_us_page(client, faker):
    response = client.get(reverse("contact_us"))
    assert response.status_code == 200
    assert b"Send us an email!" in response.content

    data = {
        "email": faker.email(),
        "text": faker.sentence(),
    }
    response = client.post(reverse("contact_us"), data=data)
