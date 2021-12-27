import os
from celery import Celery
from django.conf import settings
import logging
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal

from bene.xeroapp.update_models_from_xero import reload_data


client = Client(settings.SENTRY_DSN)

# register a custom filter to filter out duplicate logs
register_logger_signal(client)

# The register_logger_signal function can also take an optional argument
# `loglevel` which is the level used for the handler created.
# Defaults to `logging.ERROR`
register_logger_signal(client, loglevel=logging.INFO)

# hook into the Celery error handler
register_signal(client)

# The register_signal function can also take an optional argument
# `ignore_expected` which causes exception classes specified in Task.throws
# to be ignored
register_signal(client, ignore_expected=True)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
app = Celery("bene")

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings")
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


@app.task(bind=True)
def reload_task(self, xero_values):
    reload_data(xero_values)
