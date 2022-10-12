from django.urls import path

from .views import feedbacks


urlpatterns = [
    path("", feedbacks, name='feedbacks'),
]
