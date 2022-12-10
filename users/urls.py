from django.urls import path, include
from django.contrib.auth import urls

from users.views import (
    CustomLoginView, RegistrationView, RegistrationConfirmView,
    RegistrationPhoneConfirmView
)

urlpatterns = [
    path("account/login/", CustomLoginView.as_view(), name="login"),
    path("account/", include(urls)),
    path(
        "account/registration/",
        RegistrationView.as_view(),
        name="registration"
    ),
    path(
        'account/registration/<uidb64>/<token>/confirm/',
        RegistrationConfirmView.as_view(),
        name='registration_confirm'
    ),
    path(
        'account/registration/phone-confirm/',
        RegistrationPhoneConfirmView.as_view(),
        name='registration_phone_confirm'
    ),
]
