import datetime

from time import sleep

from django.core.management.base import BaseCommand

import elasticsearch

from post.models import Post, UserTopic
from userprofile.models import UserProfile


class Command(BaseCommand):
    help = 'Recalculate the user topics'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        posts = Post.objects.filter(is_deleted=False).update(
            is_deleted=True,
            legacy_deleted=True
        )

        userprofiles = UserProfile.objects.exclude(profile_boosts=None)
        for userprofile in userprofiles:
            userprofile.profile_boosts.all().delete()

        user_topics = UserTopic.objects.all().delete()
