"""
Local settings

- Run in Debug mode

- Use console backend for emails

- Add Django Debug Toolbar
- Add django-extensions as app
"""
import logging


from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env(
    "DJANGO_SECRET_KEY", default="AyoU_fB9l=z`rZ%Tg}Q1ez2U!6~P]W{JW4owBX|)sZ)*pWi0[j"
)

# raven sentry client
# See https://docs.sentry.io/clients/python/integrations/django/
INSTALLED_APPS += [
    "raven.contrib.django.raven_compat",
]

# Mail settings
# ------------------------------------------------------------------------------

EMAIL_PORT = 1025

EMAIL_HOST = "localhost"
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
INSTALLED_APPS += [
    "debug_toolbar",
]

INTERNAL_IPS = [
    "127.0.0.1",
    "10.0.2.2",
]

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += [
    "django_extensions",
]

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Your local stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
XERO_CONSUMER_SECRET = env("XERO_CONSUMER_SECRET")
XERO_CONSUMER_KEY = env("XERO_CONSUMER_KEY")

# Sentry Configuration
SENTRY_DSN = env("DJANGO_SENTRY_DSN")
SENTRY_CLIENT = env(
    "DJANGO_SENTRY_CLIENT", default="raven.contrib.django.raven_compat.DjangoClient"
)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "root": {
        "level": "WARNING",
        "handlers": [
            "sentry",
        ],
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        },
    },
    "handlers": {
        "sentry": {
            "level": "ERROR",
            "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": [
                "console",
            ],
            "propagate": False,
        },
        "raven": {
            "level": "DEBUG",
            "handlers": [
                "console",
            ],
            "propagate": False,
        },
        "sentry.errors": {
            "level": "DEBUG",
            "handlers": [
                "console",
            ],
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": [
                "console",
                "sentry",
            ],
            "propagate": False,
        },
    },
}
SENTRY_CELERY_LOGLEVEL = env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)
RAVEN_CONFIG = {
    "CELERY_LOGLEVEL": env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO),
    "DSN": SENTRY_DSN,
}

DATABASES["default"] = env.db("DATABASE_URL")
