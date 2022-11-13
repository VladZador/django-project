from django.urls import path

from .views import MainView, ContactView

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('contact-us/', ContactView.as_view(), name='contact_us'),
]
