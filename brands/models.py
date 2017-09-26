import sys
from PIL import Image
from io import BytesIO

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.uploadedfile import InMemoryUploadedFile

from boost.models import Boost


class Brand(models.Model):

    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to='brand_logos')
    logo_thumbnail = models.ImageField(upload_to='brand_thumbnails')
    profile_image = models.ImageField(upload_to='brand_profiles', null=True)
    profile_color = models.CharField(max_length=7, default='#000000')
    description = models.CharField(max_length=500)
    compact_display_image = models.ImageField(upload_to='brand_compact_display')

    boosts = GenericRelation(Boost, related_query_name='brand')

    created_on = models.DateTimeField(auto_now_add=True)
    last_update_on = models.DateTimeField(auto_now=True)

    def save(self):
        im = Image.open(self.logo)
        output = BytesIO()
        im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
        self.logo = InMemoryUploadedFile(
            output, 'ImageField', self.logo.name, 'image/jpeg', sys.getsizeof(output), None)

        im = Image.open(self.logo)
        output = BytesIO()
        size = (48, 48)
        im.thumbnail(size)
        im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
        self.logo_thumbnail = InMemoryUploadedFile(
            output, 'ImageField', self.logo.name, 'image/jpeg', sys.getsizeof(output), None)

        if self.profile_image:
            im = Image.open(self.profile_image)
            output = BytesIO()
            im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
            self.profile_image = InMemoryUploadedFile(
                output, 'ImageField', self.profile_image.name, 'image/jpeg', sys.getsizeof(output), None)

        super().save()

    def __str__(self):
        return "%s" % (self.name, )


class BrandMember(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_query_name='members')

    def __str__(self):
        return "%s %s for %s" % (self.user.userprofile.first_name,
                                 self.user.userprofile.last_name,
                                 self.brand.name)
