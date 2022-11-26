from django.contrib.auth import get_user_model
from django.urls import reverse

from .forms import CustomAuthenticationForm, RegistrationForm

User = get_user_model()


def test_login_user(client, faker, user_and_password):
    user, password = user_and_password
    url = reverse("login")

    # Get login page with login form
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context["form"], CustomAuthenticationForm)

    # Post only password into login form
    data = {"password": faker.password()}
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["__all__"][0] == 'Email or phone number is required'

    # Post only username into login form
    data = {"username": faker.email()}
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["password"][0] == 'This field is required.'

    # Post only phone number into login form
    data = {"phone": faker.phone_number()}
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["password"][0] == 'This field is required.'

    # Post wrong password into login form
    data = {
        "username": user.email,
        "password": faker.password(),
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["__all__"][0] == \
           "Please enter a correct email address and password. Note that both fields may be case-sensitive."

    # Post wrong email into login form
    data = {
        "username": faker.email(),
        "password": password,
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["__all__"][0] == \
           "Please enter a correct email address and password. Note that both fields may be case-sensitive."

    # Post wrong phone number into login form
    data = {
        "phone": faker.phone_number(),
        "password": password,
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["__all__"][0] == \
           "Please enter a correct email address and password. Note that both fields may be case-sensitive."

    # Post correct email and password into login form
    data = {
        "username": user.email,
        "password": password,
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert f"Welcome, {user.get_username()}!" in [m.message for m in list(response.context['messages'])]
    client.logout()

    # Post correct phone and password into login form
    data = {
        "phone": user.phone,
        "password": password,
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert f"Welcome, {user.get_username()}!" in [m.message for m in list(response.context['messages'])]


def test_registration(client, faker, user_and_password):
    url = reverse("signup")

    # Get signup page with registration form
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context["form"], RegistrationForm)

    # Post empty data into registration form
    response = client.post(url, data={})
    assert response.status_code == 200
    assert response.context["form"].errors["email"][0] == 'This field is required.'
    assert response.context["form"].errors["password1"][0] == 'This field is required.'
    assert response.context["form"].errors["password2"][0] == 'This field is required.'

    # Post data of existing user into registration form
    user, password = user_and_password
    data = {
        "email": user.email,
        "password1": password,
        "password2": password,
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["email"][0] == 'User with this Email address already exists.'

    # Post different passwords into registration form
    data = {
        "email": faker.email(),
        "password1": faker.password(),
        "password2": faker.password(),
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["password2"][0] == "The two password fields didn’t match."

    # Post correct data; check that user is created and is not admin
    password = faker.password()
    data = {
        "email": faker.email(),
        "password1": password,
        "password2": password,
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert User.objects.filter(email=data["email"])
    user = response.context['user']
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser
    assert f"Welcome on MyStore, {user.get_username()}!" \
           in [m.message for m in list(response.context['messages'])]
