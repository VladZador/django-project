from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


def test_login_user(client, faker):
    # Creating a user in db
    email = faker.email()
    password = faker.password()
    phone = faker.phone_number()
    user = User.objects.create(
        email=email,
        phone=phone,
        is_phone_valid=True
    )
    user.set_password(password)
    user.save()

    # Get login page
    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200

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
        "username": email,
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
        "username": email,
        "password": password,
    }
    response = client.post(url, data=data)
    assert response.status_code == 302

    # Post correct phone and password into login form
    client.get(url)
    data = {
        "phone": phone,
        "password": password,
    }
    response = client.post(url, data=data)
    assert response.status_code == 302
