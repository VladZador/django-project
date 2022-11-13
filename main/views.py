from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from .forms import ContactForm
from .tasks import send_contact_form


class MainView(TemplateView):
    template_name = "main/index.html"


class ContactView(FormView):
    form_class = ContactForm
    template_name = "main/contact_form.html"
    success_url = reverse_lazy("main")

    def form_valid(self, form):
        send_contact_form.delay(
            form.cleaned_data["email"],
            form.cleaned_data["text"],
        )
        messages.success(self.request, "Thank you for contacting us!")
        return super().form_valid(form)
