from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, UsernameField
)
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.forms import CharField, TextInput, Form, IntegerField
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from .tasks import send_confirmation_mail


User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    """
    Overrides AuthenticationForm in order to include a phone number
    as a second option for authentication.
    """
    # The username field is actually an email. And since we want to use either
    # email or phone, we make both of these field optional.
    username = UsernameField(widget=TextInput(attrs={'autofocus': True}),
                             required=False)
    phone = CharField(required=False)

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
    field instead of username. Also, a mail is sent to the email.
    """
    class Meta:
        model = User
        fields = ("email", "phone")
        field_classes = {
            'email': UsernameField,
            'phone': UsernameField,
        }
        help_texts = {
            'phone': "Optional"
        }

    def clean(self):
        self.instance.is_active = False
        return super().clean()

    def save(self, commit=True):
        """
        Extends save() method by adding a "send_confirmation_mail" task.
        """
        user = super().save(commit=commit)
        context = {
            'email': user.email,
            'domain': settings.DOMAIN,
            'site_name': "MyStore",
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'subject': "Confirm registration",
        }
        send_confirmation_mail.delay(user.email, context)
        return user


class RegistrationPhoneConfirmForm(Form):
    code = IntegerField()

    @staticmethod
    def save(user_id):
        user = User.objects.get(id=user_id)
        user.is_phone_valid = True
        user.save(update_fields=("is_phone_valid",))
