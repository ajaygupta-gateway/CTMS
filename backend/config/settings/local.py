"""
Local development settings.

Overrides base settings.
"""
from django.core.cache.backends.redis import RedisCache

from .base import *


ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ctms',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',   
        'PORT': '5432',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "local-dev-cache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "rate_limit": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}


