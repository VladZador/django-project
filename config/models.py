from django.db import models
from django.conf import settings

from mystore.mixins.singleton import SingletonModel


class Config(SingletonModel):
    contact_form_email = models.EmailField(default=settings.ADMIN_EMAIL)
