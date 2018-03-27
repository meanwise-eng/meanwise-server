import datetime

from time import sleep

from django.core.management.base import BaseCommand
from django.db import transaction

import requests
from meanwise_backend.eventsourced import EventStoreClient

import elasticsearch

from userprofile.models import UserProfile
from userprofile.profile import ProfileCreated


class Command(BaseCommand):
    help = 'Create events for profiles'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        url = 'http://eventstore:2113/streams/'
        for profile in UserProfile.objects.all().order_by('id'):
            print("Processing profile %s" % profile.profile_uuid)
            headers = {'Accept': 'application/vnd.eventstore.events+json'}
            stream = 'mw_profile_profile-%s' % profile.profile_uuid
            with transaction.atomic():
                r = requests.get('%s%s' % (url, stream), headers=headers)
                if r.status_code == 404:
                    print("Creating ProfileCreated event.")
                    event = ProfileCreated(profile.profile_uuid)
                    eventstore = EventStoreClient.get_default_instance()
                    eventstore.save([event], stream, 1)
                else:
                    print("ProfileCreated event already exists")
