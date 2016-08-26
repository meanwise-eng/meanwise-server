from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save

from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.signals import saved_file
from easy_thumbnails.signal_handlers import generate_aliases_global

from account_profile.models import Profile


class Interest(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=70, unique=True)
    description = models.CharField(max_length=128)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False, db_index=True)
    cover_photo = ThumbnailerImageField(upload_to='interest_photos')
    color_code = models.CharField(max_length=7)

    def __unicode__(self):
        return self.name

    @property
    def cover_photo_url(self):
        if self.cover_photo:
            return self.cover_photo.url
        else:
            return ''

saved_file.connect(generate_aliases_global)
