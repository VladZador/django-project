from django.contrib import admin
from django.core.cache import cache
from django.db import models


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        """
        Pass, so that the only created instance could only be changed,
        not deleted.
        """
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)


class SingletonModelAdmin(admin.ModelAdmin):
    """Prevents Django admin users from adding or deleting instances."""

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
