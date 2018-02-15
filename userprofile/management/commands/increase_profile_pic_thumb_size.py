import datetime
import logging

from time import sleep

from django.core.management.base import BaseCommand
from django.db import transaction

import sys
from PIL import Image
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from post.models import Post, UserTopic
from userprofile.models import UserProfile
from credits.models import Critic, Credits

logger = logging.getLogger('meanwise_backend.%s' % __name__)


class Command(BaseCommand):
    help = 'Increase profile picture thumbnail size.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        userprofiles = UserProfile.objects.all()

        for userprofile in userprofiles:
            if userprofile.profile_photo:
                with transaction.atomic():
                    thumb_im = Image.open(userprofile.profile_photo_thumbnail)

                    if thumb_im.width == 96:
                        logger.info("Userprofile: %s thumbnail is already 96x96." % userprofile.id)
                        continue

                    logger.info("Userprofile: %s resizing thumbnail" % userprofile.id)

                    im = Image.open(userprofile.profile_photo)
                    thumbnail_size = (96, 96)
                    thumbnail_output = BytesIO()
                    im.thumbnail(thumbnail_size)
                    im.save(thumbnail_output, format='JPEG', quality=100, optimize=True)
                    userprofile.profile_photo_thumbnail = InMemoryUploadedFile(
                        thumbnail_output,
                        'models.ImageField',
                        userprofile.profile_photo.name,
                        'image/jpeg',
                        sys.getsizeof(thumbnail_output),
                        None
                    )

                    userprofile.save()
                    logger.info("Userprofile: %s thumbnail updated" % userprofile.id)
