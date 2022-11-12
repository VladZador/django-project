from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import RegistrationForm, CustomAuthenticationForm


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        messages.success(self.request, f"Welcome, {form.get_user().email}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Not logged in")
        return super().form_invalid(form)


class SignupView(FormView):
    template_name = "registration/registration.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("main")

    def form_valid(self, form):
        """
        Extends the basic function by log in a newly registered user.
        Since multiple authentication backends are configured, the specified
        `backend` argument must be provided to the login() function.
        """
        login(
            self.request,
            form.save(),
            backend='django.contrib.auth.backends.ModelBackend',
        )
        messages.success(
            self.request,
            f"Welcome on MyStore, {form.get_user().email}!"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "You were not registered")
        return super().form_invalid(form)
