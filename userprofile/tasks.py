from __future__ import absolute_import, unicode_literals

import sys
import os
import logging
import tempfile
import uuid

from PIL import Image
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File

from meanwise_backend.celery import app

from userprofile.models import UserProfile

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@app.task
def optimize_cover_photo(user_id):
    up = UserProfile.objects.get(user__id=user_id)

    if up.cover_photo:
        im = Image.open(up.cover_photo)
        output = BytesIO()
        im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
        up.cover_photo = InMemoryUploadedFile(
            output, 'models.ImageField',
            up.cover_photo.name, 'image/jpeg',
            sys.getsizeof(output), None
        )
        
        up.save()
    
@app.task
def optimize_and_generate_thumbnail_for_profile_photo(user_id):
    up = UserProfile.objects.get(user__id=user_id)

    if up.profile_photo:
        im = Image.open(up.profile_photo)
        output = BytesIO()
        im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
        up.profile_photo = InMemoryUploadedFile(
            output, 'models.ImageField',
            up.profile_photo.name, 'image/jpeg',
            sys.getsizeof(output), None
        )

        thumbnail_size = (96, 96)
        thumbnail_output = BytesIO()
        im.thumbnail(thumbnail_size)
        im.save(thumbnail_output, format='JPEG', quality=100, optimize=True)
        up.profile_photo_thumbnail = InMemoryUploadedFile(
            thumbnail_output,
            'models.ImageField',
            up.profile_photo.name,
            'image/jpeg',
            sys.getsizeof(thumbnail_output),
            None
        )

        up.save()
