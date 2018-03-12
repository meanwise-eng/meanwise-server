#!/usr/bin/env python
import os
import logging
import django
import asyncio
import functools
import signal
import importlib
import inspect

from django.conf import settings
from django.apps import apps
from meanwise_backend.eventsourced import EventStoreClient, EventBus

os.environ['DJANGO_SETTINGS_MODULE'] = 'meanwise_backend.settings'

django.setup()

logger = logging.getLogger('mw.eventhandler')
logger.setLevel(logging.DEBUG)

loop = asyncio.get_event_loop()

def ask_exit(signame):
    logger.info("Got signal %s: exit" % signame)
    loop.stop()

for signame in ('SIGINT', 'SIGTERM'):
    loop.add_signal_handler(getattr(signal, signame),
                            functools.partial(ask_exit, signame))

for app_conf in apps.get_app_configs():
    try:
        mod = importlib.import_module('%s.eventhandlers' % app_conf.name)
        print("Loaded %s.eventhandlers" % app_conf.name)
    except ImportError:
        print("No eventhandlers for module %s" % app_conf.name)
        continue

eventbus = EventBus.get_default_instance()

logger.info("Eventhandler running, press Ctrl+C to interrupt.")
logger.info("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())

try:
    loop.run_until_complete(eventbus.run(loop))
finally:
    loop.close()
