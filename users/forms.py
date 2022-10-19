from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
            raise ValidationError("Email is empty")
        try:
            User.objects.get(username=self.instance.username)
            raise ValidationError("User with this username already exists")
        except User.DoesNotExist:
            return self.cleaned_data
