from django.urls import path, include
from django.contrib.auth import urls

from users.views import SignupView

urlpatterns = [
    path("", include(urls)),
    path("signup/", SignupView.as_view(), name="signup"),
]
