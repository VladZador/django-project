from django.urls import path, include
from django.contrib.auth import urls

from users.views import SignupView

urlpatterns = [
    path("", include(urls)),
    path("signup/", SignupView.as_view(), name="signup"),
]

# 1. form (username, email, password, password2)
# 2. save model -> user instance
# 3. login user instance
