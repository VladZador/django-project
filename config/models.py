from django.db import models

from mystore.mixins.singleton import SingletonModel
from mystore.settings import env


class Config(SingletonModel):
    contact_form_email = models.EmailField(default=env("ADMIN_EMAIL"))
