from django.core.management.base import BaseCommand, CommandError

from notifications.models import Notification
from account_profile.models import Profile
from works.models import Work
from works.serializers import NotificationWorkSerializer
from account_profile.serializers import DefaultProfileDetailSerializer, \
        NotificationProfileSerializer


class Command(BaseCommand):
    '''
    This command is used to build cache in redis.
    Currently it supports building profile cache in redis.
    '''
    help = 'Build redis cache. Make sure that for notifications you have deleted all notifications keys'

    def add_arguments(self, parser):
        parser.add_argument(
                    '--profile',
                    action='store_true',
                    default=False,
                    dest='profile',
                    help='Cache profiles.'
                )
        parser.add_argument(
                    '--notification',
                    action='store_true',
                    default=False,
                    dest='notification',
                    help='Cache notifications.'
                )
        parser.add_argument(
                    '--work',
                    action='store_true',
                    default=False,
                    dest='work',
                    help='Cache works.'
                )

    def handle(self, *args, **kwargs):
        if kwargs['profile']:
            for profile in Profile.objects.all():
                Profile.cache.serialized(profile, DefaultProfileDetailSerializer)
                Profile.cache.serialized(profile, NotificationProfileSerializer)

        if kwargs['notification']:
            for notif in Notification.objects.prefetch_related('profile').all():
                Notification.cache.add(notif)

        if kwargs['work']:
            for work in Work.objects.all():
                Work.cache.serialized(work, NotificationWorkSerializer, force_fetch=True)
