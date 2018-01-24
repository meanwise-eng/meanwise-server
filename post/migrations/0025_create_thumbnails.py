# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-23 22:29
from __future__ import unicode_literals

from django.db import migrations

from post.models import Post


def create_thumbnails(apps, schema_editor):
    import requests, sys
    from PIL import Image
    from io import BytesIO
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import logging
    logger = logging.getLogger('meanwise_backend.%s' % __name__)

    for post in Post.objects.all().order_by('-created_on'):
        if post.get_post_type() != Post.TYPE_IMAGE:
            continue

        logger.info("Resizing post: %s" % post.id)
        if post.thumbnail:
            logger.info("Thumbnail already exists")
            continue

        logger.info("Image URL: %s" % post.image.url)

        r = requests.get(post.image.url)
        img_file = BytesIO(r.content)
        img = Image.open(img_file)

        target_width = 750 * 0.5
        scaling_ratio = target_width / img.width
        thumb = img.resize((int(img.width*scaling_ratio), int(img.height*scaling_ratio)),
                          Image.BICUBIC)
        thumb_output = BytesIO()
        thumb.save(thumb_output, format='JPEG', quality=95, optimize=True, progressive=True)
        post.thumbnail = InMemoryUploadedFile(thumb_output, 'ImageField', post.image.name,
            'image/jpeg', sys.getsizeof(thumb_output), None)

        post.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('post', '0024_post_thumbnail'),
    ]

    operations = [
        migrations.RunPython(create_thumbnails, migrations.RunPython.noop),
    ]
