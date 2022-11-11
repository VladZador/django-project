from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, UsernameField
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import gettext_lazy as _


class CustomAuthenticationForm(AuthenticationForm):
    """
    Extends AuthenticationForm in order to include a phone number
    as a second option for authentication.
    """
    # The username field is actually an email. And since we want to use either
    # email or phone, we make both of these field optional.
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True}),
                             required=False)
    phone = forms.CharField(required=False)

    def clean(self):
        # Keep in mind, username is actually an email.
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        phone = self.cleaned_data.get('phone')

        if not username and not phone:
            raise ValidationError(_("Email or phone number is required"))

        if password:
            kwargs = {
                "password": password,
                "username": username,
            }
            if phone and not username:
                kwargs.pop("username")
                kwargs.update({"phone": phone})
            self.user_cache = authenticate(self.request, **kwargs)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RegistrationForm(UserCreationForm):
    """
    Custom user creation form. Overrides basic form by making email required
    field instead of username. The email name (without domain name) is used as
    username.
    """
    class Meta:
        model = get_user_model()
        fields = ("email",)
        field_classes = {'email': UsernameField}

    def clean(self) -> dict:
        """
        Creates a username from email name, raises an error if email is empty,
        also checks the database and raises an error if the username already
        exists.

        :return: dict with cleaned user data (email, password, username)
        """
        self.instance.username = self.cleaned_data['email'].split('@')[0]
        if not self.instance.username:
            raise ValidationError(_("Email is empty"))
        try:
            User.objects.get(username=self.instance.username)
            raise ValidationError(_("User with this username already exists"))
        except User.DoesNotExist:
            return self.cleaned_data
