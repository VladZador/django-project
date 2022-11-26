from django.core import mail
from django.urls import reverse

from main.forms import ContactForm


def test_main_page(client):
    # Open main page
    response = client.get(reverse("main"))
    assert response.status_code == 200


def test_contact_us_page(client, faker):
    # Get "contact us" page
    response = client.get(reverse("contact_us"))
    assert response.status_code == 200
    assert isinstance(response.context["form"], ContactForm)

    # Wrong form input: empty data
    response = client.post(reverse("contact_us"), data={})
    assert response.status_code == 200
    assert response.context["form"].errors["email"][0] == "This field is required."
    assert response.context["form"].errors["text"][0] == "This field is required."
    assert not mail.outbox

    # Wrong form input: Not an email in the email field
    data = {
        "email": faker.word(),
        "text": faker.sentence(),
    }
    response = client.post(reverse("contact_us"), data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["email"][0] == "Enter a valid email address."
    assert not mail.outbox

    # Correct form input
    data = {
        "email": faker.email(),
        "text": faker.sentence(),
    }
    response = client.post(reverse("contact_us"), data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert data["email"] in mail.outbox[0].body
    assert data["text"] in mail.outbox[0].body
