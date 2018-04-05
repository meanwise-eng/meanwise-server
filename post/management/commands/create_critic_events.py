import datetime
import logging

from time import sleep

from django.core.management.base import BaseCommand
from django.db import transaction

import requests
from meanwise_backend.eventsourced import EventStoreClient

import elasticsearch

from userprofile.models import UserProfile
from post.models import Post
from credits.models import Critic
from credits.critic import create_critic

logger = logging.getLogger('meanwise_backend.%s' % __name__)


class Command(BaseCommand):
    help = 'Create events for critics'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for critic in Critic.objects.all().order_by('id'):
            print("Processing critic %s" % critic.id)

            try:
                criticizer = UserProfile.objects.get(user__id=critic.from_user_id)
            except UserProfile.DoesNotExist:
                logger.error("Not a valid userprofile (%d) in critic (%d)" % (critic.from_user_id,
                                                                              critic.id))
                continue
            else:
                criticizer = criticizer.profile_uuid

            try:
                criticized = UserProfile.objects.get(user__id=critic.to_user_id)
            except UserProfile.DoesNotExist:
                logger.error("Not a valid userprofile (%d) in critic (%d)" % (critic.to_user_id,
                                                                              critic.id))
                continue
            else:
                criticized = criticized.profile_uuid

            try:
                post = Post.objects.get(id=critic.post_id)
            except Post.DoesNotExist:
                logger.error("Not a valid post (%d) in critic (%d)" % (critic.post_id, critic.id))
                continue
            else:
                post_uuid = post.post_uuid
                skill = post.topic

            rating = 3

            try:
                create_critic(criticizer=criticizer, criticized=criticized, post_id=post_uuid,
                              rating=rating, skill=skill)
            except Exception as e:
                logger.error(e)
