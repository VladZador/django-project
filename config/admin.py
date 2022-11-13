from django.contrib import admin

from mystore.mixins.singleton import SingletonModelAdmin
from .models import Config


@admin.register(Config)
class ConfigAdmin(SingletonModelAdmin):
    pass
