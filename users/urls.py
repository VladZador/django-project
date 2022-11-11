from django.urls import path, include
from django.contrib.auth import urls

from users.views import SignupView, CustomLoginView

urlpatterns = [
    path("account/login/", CustomLoginView.as_view(), name="login"),
    path("account/", include(urls)),
    path("account/signup/", SignupView.as_view(), name="signup"),
]
