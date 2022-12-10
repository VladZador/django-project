from random import randint

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView, RedirectView

from .forms import RegistrationForm, CustomAuthenticationForm, \
    RegistrationPhoneConfirmForm
from .tasks import send_sms

User = get_user_model()


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Welcome, {form.get_user().get_username()}!"
        )
        return super().form_valid(form)


class RegistrationView(FormView):
    template_name = "registration/registration.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("main")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Check your email for confirmation")
        return super().form_valid(form)


class RegistrationConfirmView(RedirectView):
    """
    Confirms an email validity by checking uidb64 code and token passed
    in the url.
    If a phone number was provided during registration, the view "sends" a SMS
    with special auto-generated code and passes it in the cache. Also, it
    passes user_id in the request.session so that it can be later used in the
    RegistrationPhoneConfirmView.
    """
    url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        user = self.get_user(kwargs['uidb64'])

        if user is not None:
            token = kwargs['token']
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save(update_fields=("is_active",))
                messages.success(request, "User activation is successful!")
                if user.phone:
                    code = randint(10000, 99999)
                    cache.set(f"{user.id}_code", code, timeout=60 * 2)
                    send_sms.delay(user.phone, code)
                    self.request.session["user_id"] = str(user.id)
                    return HttpResponseRedirect(
                        reverse_lazy("registration_phone_confirm")
                    )
            else:
                messages.error(request, "Invalid link - activation failed")
        else:
            messages.error(request, "Invalid link - activation failed")
        return super().get(request, *args, **kwargs)

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist,
                ValidationError):
            user = None
        return user


class RegistrationPhoneConfirmView(FormView):
    """
    Checks whether the provided code is equal to the one stored in the cache.
    """
    form_class = RegistrationPhoneConfirmForm
    template_name = "registration/phone_confirm.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user_id = self.request.session["user_id"]
        if cache.get(self.request.session["user_id"] + "_code") \
                == form.cleaned_data["code"]:
            form.save(user_id)
            messages.success(self.request, "Your phone number is confirmed!")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Code is invalid")
            return self.form_invalid(form)
