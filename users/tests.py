import re

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import CustomAuthenticationForm, RegistrationForm, \
    RegistrationPhoneConfirmForm

User = get_user_model()


def test_login_user(client, faker, user_and_password):
    user, password = user_and_password
    url = reverse("login")

    # Get login page with login form
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context["form"], CustomAuthenticationForm)
    # todo: change isinstance() to checking type("some_form")

    # Post only password into login form
    data = {"password": faker.password()}
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["__all__"][0] \
           == 'Email or phone number is required'

    # Post only username into login form
    data = {"username": faker.email()}
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["password"][0] \
           == 'This field is required.'

    # Post only phone number into login form
    data = {"phone": faker.phone_number()}
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["password"][0] \
           == 'This field is required.'

    # Post wrong password into login form
    data = {
        "username": user.email,
        "password": faker.password(),
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["__all__"][0] == \
           "Please enter a correct email address and password. " \
           "Note that both fields may be case-sensitive."

    # Post wrong email into login form
    data = {
        "username": faker.email(),
        "password": password,
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["__all__"][0] == \
           "Please enter a correct email address and password. " \
           "Note that both fields may be case-sensitive."

    # Post wrong phone number into login form
    data = {
        "phone": faker.phone_number(),
        "password": password,
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["__all__"][0] == \
           "Please enter a correct email address and password. " \
           "Note that both fields may be case-sensitive."

    # Post correct email and password into login form
    data = {
        "username": user.email,
        "password": password,
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert f"Welcome, {user.get_username()}!" \
           in [m.message for m in list(response.context['messages'])]
    client.logout()

    # Post correct phone and password into login form
    data = {
        "phone": user.phone,
        "password": password,
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert f"Welcome, {user.get_username()}!" \
           in [m.message for m in list(response.context['messages'])]


def test_registration_and_confirmation(client, faker, user_and_password):
    url = reverse("registration")

    # Get registration page with the registration form
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context["form"], RegistrationForm)

    # Post empty data into registration form
    response = client.post(url, data={})
    assert response.status_code == 200
    assert response.context["form"].errors["email"][0] == \
           'This field is required.'
    assert response.context["form"].errors["password1"][0] == \
           'This field is required.'
    assert response.context["form"].errors["password2"][0] == \
           'This field is required.'

    # Post data of existing user into registration form
    user, password = user_and_password
    data = {
        "email": user.email,
        "password1": password,
        "password2": password,
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["email"][0] == \
           'User with this Email address already exists.'

    # Post different passwords into registration form
    data = {
        "email": faker.email(),
        "password1": faker.password(),
        "password2": faker.password(),
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["password2"][0] \
           == "The two password fields didn’t match."

    # Post correct data; check that user is created,
    # but is not active and is not admin
    email = faker.email()
    password = faker.password()
    data = {
        "email": email,
        "password1": password,
        "password2": password,
    }
    assert not mail.outbox

    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert User.objects.filter(
        email=email,
        is_active=False,
        is_staff=False,
        is_superuser=False
    ).exists()
    assert len(mail.outbox) == 1
    assert "Check your email for confirmation" \
           in [m.message for m in list(response.context['messages'])]

    # Parse the link in the mail and accessing confirmation page.
    # After that the user's "is_active" status has to be True
    uidb64, token = re.search(
        "registration/(.*)/(.*)/confirm", mail.outbox[0].body
    ).groups()

    # Accessing wrong confirmation link (wrong uid)
    wrong_confirm_url = reverse(
        "registration_confirm",
        kwargs={
            "uidb64": urlsafe_base64_encode(force_bytes(faker.pyint())),
            "token": token
        }
    )
    response = client.get(wrong_confirm_url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") for i in response.redirect_chain)
    assert not User.objects.filter(
        email=data["email"],
        is_active=True,
    )
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Accessing wrong confirmation link (wrong token)
    wrong_confirm_url = reverse(
        "registration_confirm",
        kwargs={
            "uidb64": uidb64,
            "token": default_token_generator.make_token(user)
        }
    )
    response = client.get(wrong_confirm_url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") for i in response.redirect_chain)
    assert not User.objects.filter(
        email=data["email"],
        is_active=True,
    )
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Accessing correct confirmation link
    confirm_mail_url = reverse(
        "registration_confirm",
        kwargs={"uidb64": uidb64, "token": token}
    )
    response = client.get(confirm_mail_url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") for i in response.redirect_chain)
    assert User.objects.filter(
        email=data["email"],
        is_active=True,
    ).exists()
    # todo: change assertion for filters: add exists() where possible

    assert "success" \
           in [m.level_tag for m in list(response.context['messages'])]

    # todo: change assertion for messages from checking its message text to
    #  its level tag:
    #  assert "success" in \
    #  [m.level_tag for m in list(response.context['messages'])]


def test_registration_with_phone_number(client, faker):
    url = reverse("registration")

    # Post correct data with the phone number
    email = faker.email()
    password = faker.password()
    data = {
        "email": email,
        "password1": password,
        "password2": password,
        "phone": faker.phone_number()
    }
    assert not mail.outbox

    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert User.objects.filter(
        email=email,
        is_active=False,
        is_staff=False,
        is_superuser=False
    ).exists()
    assert len(mail.outbox) == 1
    assert "success" \
           in [m.level_tag for m in list(response.context['messages'])]

    # Parse the link in the mail and accessing confirmation page.
    # After that the user's "is_active" status has to be True
    uidb64, token = re.search(
        "registration/(.*)/(.*)/confirm", mail.outbox[0].body
    ).groups()
    confirm_mail_url = reverse(
        "registration_confirm",
        kwargs={"uidb64": uidb64, "token": token}
    )
    response = client.get(confirm_mail_url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("registration_phone_confirm")
               for i in response.redirect_chain)
    assert User.objects.filter(
        email=data["email"],
        is_active=True,
    ).exists()

    # Accessing phone confirmation page using GET method
    confirm_phone_url = reverse('registration_phone_confirm')
    response = client.get(confirm_phone_url)
    assert response.status_code == 200
    assert isinstance(response.context["form"], RegistrationPhoneConfirmForm)

    # Post wrong code type into the form
    response = client.post(confirm_phone_url, data={"code": faker.word()})
    assert response.status_code == 200
    assert response.context["form"].errors["code"]

    # Post invalid code into the form
    response = client.post(
        confirm_phone_url, data={"code": faker.pyint()}
    )
    assert response.status_code == 200
    assert not User.objects.filter(email=email, is_phone_valid=True).exists()
    assert "error" in [m.level_tag for m in list(response.context['messages'])]

    # Accessing phone confirmation page using POST method
    user = User.objects.get(email=email)
    code = cache.get(f"{user.id}_code")
    response = client.post(confirm_phone_url, data={"code": code}, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") for i in response.redirect_chain)
    assert User.objects.filter(email=email, is_phone_valid=True).exists()
    assert "success" \
           in [m.level_tag for m in list(response.context['messages'])]
