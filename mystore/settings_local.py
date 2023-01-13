from django.conf import settings
import environ

env = environ.Env(
    DEBUG=(bool, False)
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': settings.BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': env("CACHE_LOCATION"),
    }
}
