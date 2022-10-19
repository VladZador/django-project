from django.urls import path

from .views import feedbacks_view


urlpatterns = [
    path("feedbacks/", feedbacks_view, name='feedbacks'),
]
