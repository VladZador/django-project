from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import FormView  # TemplateView

from .forms import RegistrationForm  # LoginForm


# class LoginView(TemplateView):
#     """
#     This view is not used in the project due to much simpler login/logout
#     implementation by urls in django.contrib.auth.
#     """
#     template_name = "users/login.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context.update({'form': kwargs.get('form') or LoginForm})
#         return context
#
#     def post(self, request, *args, **kwargs):
#         context = self.get_context_data(**kwargs)
#         form = context.get('form')
#         form = form(request.POST)
#         if form.is_valid():
#             login(request, form.user)
#         return self.get(request, form=form, *args, **kwargs)


class SignupView(FormView):
    template_name = "registration/registration.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("items")

    def form_valid(self, form):
        login(self.request, form.save())
        return super().form_valid(form)
