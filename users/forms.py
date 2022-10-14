"""This module contains login form. But it is not used in the project due to
much simpler login/logout implementation by urls in django.contrib.auth."""
from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.user = None

    def is_valid(self):
        if not self.errors:
            user = authenticate(
                username=self.cleaned_data["username"],
                password=self.cleaned_data["password"]
            )
            if not user:
                self.errors.update({"user": "Wrong username or password"})
        return super().is_valid()
