#!/usr/bin/env python
import time
import os
import django
import asyncio
import functools
import signal
import importlib
import inspect

from django.conf import settings
from django.apps import apps

os.environ['DJANGO_SETTINGS_MODULE'] = 'meanwise_backend.settings'

django.setup()

from meanwise_backend.eventsourced import EventStoreClient, EventBus, Command

import logging
logger = logging.getLogger('meanwise_backend.%s' % __name__)
logger.setLevel(logging.DEBUG)

loop = asyncio.get_event_loop()

eventstore_client = EventStoreClient(settings.EVENTSTORE_HOST)
Command.set_eventstore_client(eventstore_client)
eventbus = EventBus(eventstore_client)
EventBus.singleton = eventbus

def ask_exit(signame):
    logger.info("Got signal %s: exit" % signame)
    loop.stop()

for signame in ('SIGINT', 'SIGTERM'):
    loop.add_signal_handler(getattr(signal, signame),
                            functools.partial(ask_exit, signame))

for app_conf in apps.get_app_configs():
    spec = importlib.util.find_spec('%s.eventhandlers' % app_conf.name)

    if spec is not None:
        mod = importlib.import_module('%s.eventhandlers' % app_conf.name)
        logger.info("Loaded %s.eventhandlers" % app_conf.name)


logger.info("Eventhandler running, press Ctrl+C to interrupt.")
logger.info("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())
logger.info("Will start processing events in 3 seconds")
time.sleep(3)

try:
    loop.run_until_complete(eventbus.run(loop))
finally:
    loop.close()
