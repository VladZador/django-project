from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import RegistrationForm


class SignupView(FormView):
    template_name = "registration/registration.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("main")

    def form_valid(self, form):
        """
        Extends the basic function by log in a newly registered user.
        """
        login(self.request, form.save())
        return super().form_valid(form)
