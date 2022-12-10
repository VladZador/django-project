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
        # todo: change description
        """
        Extends the basic function by log in a newly registered user.
        Since multiple authentication backends are configured, the specified
        `backend` argument must be provided to the login() function.
        """
        user = form.save()
        if form.cleaned_data.get("phone"):
            self.request.session["user_id"] = str(user.id)
            return HttpResponseRedirect(
                reverse_lazy("registration_phone_confirm")
            )
        messages.success(self.request, "Check your email for confirmation")
        return super().form_valid(form)


class RegistrationConfirmView(RedirectView):
    url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        user = self.get_user(kwargs['uidb64'])

        if user is not None:
            token = kwargs['token']
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save(update_fields=("is_active",))
                messages.success(request, "User activation is successful!")
            else:
                messages.error(request, "Activation error")
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
    form_class = RegistrationPhoneConfirmForm
    template_name = "registration/phone_confirm.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user_id = self.request.session["user_id"]
        if cache.get(self.request.session["user_id"] + "_code") \
                == form.cleaned_data["code"]:
            form.save(user_id)
            messages.success(
                self.request,
                "Your phone number is confirmed!\n"
                "Now check your email to complete registration!"
            )
            return super().form_valid(form)
        else:
            messages.error(self.request, "Code is invalid")
            return self.form_invalid(form)
