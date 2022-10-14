from django.urls import path

from .views import items


urlpatterns = [
    path('', items, name='items'),
]
