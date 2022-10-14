from django.contrib.auth import login, authenticate
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

    def log_the_user(self, request):
        username = request.POST.get('email')[0].split("@")[0]
        password = request.POST.get('password1')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return True

    def form_valid(self, form):
        try:
            self.log_the_user(self.request)
            return super().form_valid(form)
        except IndexError:
            form.errors.update({"email": "Email is empty"})
            return super().form_invalid(form)
