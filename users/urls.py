from django.urls import path, include
from django.contrib.auth import urls

from users.views import SignupView

urlpatterns = [
    path("account/", include(urls)),
    path("account/signup/", SignupView.as_view(), name="signup"),
]
