# from django import forms
from django.contrib.auth import get_user_model  # authenticate
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# class LoginForm(forms.Form):
#     """
#     This form is not used in the project due to much simpler login/logout
#     implementation by urls in django.contrib.auth.
#     """
#     username = forms.CharField()
#     password = forms.CharField(
#         widget=forms.PasswordInput()
#     )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(self, *args, **kwargs)
#         self.user = None
#
#     def is_valid(self):
#         if not self.errors:
#             user = authenticate(
#                 username=self.cleaned_data["username"],
#                 password=self.cleaned_data["password"]
#             )
#             if not user:
#                 self.errors.update({"user": "Wrong username or password"})
#         return super().is_valid()


class RegistrationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ("email",)
        field_classes = {'email': UsernameField}

    def clean(self):
        self.instance.username = self.cleaned_data['email'].split('@')[0]
        if not self.instance.username:
            raise ValidationError("Email is empty")
        try:
            User.objects.get(username=self.instance.username)
            raise ValidationError("User with this username already exists")
        except User.DoesNotExist:
            return self.cleaned_data
