from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
import celery
import raven
from raven.contrib.celery import register_signal, register_logger_signal


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meanwise_backend.settings')

from django.conf import settings  # noqa


class Celery(celery.Celery):

    def on_configure(self):
        if not settings.DEBUG:
            client = raven.Client(settings.RAVEN_CONFIG['dsn'])
            # register a custom filter to filter out duplicate logs
            register_logger_signal(client)
            # hook into the Celery error handler
            register_signal(client)


app = Celery('meanwise_backend')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
