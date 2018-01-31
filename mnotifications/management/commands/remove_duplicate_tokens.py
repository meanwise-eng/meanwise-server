import datetime

from time import sleep

from django.core.management.base import BaseCommand

import elasticsearch

from mnotifications.models import ASNSDevice
from post.documents import PostDocument, post as post_index


class Command(BaseCommand):
    help = 'Remove push notifications tokens that are duplicated.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        asns_devices = ASNSDevice.objects.all()

        for asns_device in asns_devices:
            asns_device_dups = ASNSDevice.objects.exclude(id=asns_device.id).filter(
                device__push_token=asns_device.device.push_token).delete()
