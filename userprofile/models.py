from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib import auth
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save, post_delete

from easy_thumbnails.fields import ThumbnailerImageField
from taggit.managers import TaggableManager

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from common.utils import slugify


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Profession(models.Model):
    text = models.CharField(max_length=128)
    slug = models.SlugField(max_length=70, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    searchable = models.BooleanField(default=True)

    def __str__(self):
        return "Profession id: " + str(self.id) + " text : " + str(self.text)

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = slugify(self.text)
        super(Profession, self).save(*args, **kwargs)


class Skill(models.Model):
    text = models.CharField(max_length=128)
    lower = models.CharField(max_length=128, blank=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    searchable = models.BooleanField(default=True)

    def __str__(self):
        return "Skill id:" + str(self.id) + " text:" + str(self.text)

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.text = self.text.lower()
            self.slug = slugify(self.text)
        if not self.lower:
            self.lower = self.text.lower()
        super(Skill, self).save(*args, **kwargs)


class Interest(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=70, unique=True)
    description = models.CharField(max_length=128)
    published = models.BooleanField(default=False, db_index=True)
    cover_photo = ThumbnailerImageField(upload_to='interest_photos', null=True, blank=True)
    color_code = models.CharField(max_length=7, null=True, blank=True)
    topics = TaggableManager()
    is_deleted = models.BooleanField(default=False)
    vote_count = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Interest id: " + str(self.id) + " name " + str(self.name)

    @property
    def cover_photo_url(self):
        if self.cover_photo:
            return self.cover_photo.url
        else:
            return ''


class UserProfile(models.Model):
    user = models.OneToOneField(User, db_index=True)
    facebook_token = models.CharField(max_length=128, null=True, blank=True)
    username = models.CharField(max_length=25, db_index=True)
    first_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)
    profession = models.ForeignKey(Profession,
                                    blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name='skills', blank=True)
    interests = models.ManyToManyField(Interest,
                                       related_name='interests', blank=True)
    profile_photo = ThumbnailerImageField(upload_to='profile_photos',
                                          blank=True)
    cover_photo = ThumbnailerImageField(upload_to='cover_photos', blank=True)
    bio = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return 'user profile id %s - %s %s %s' % (str(self.id), self.first_name, self.last_name, self.username)

class InviteGroup(models.Model):
    name = models.CharField(max_length=128)
    count = models.IntegerField(default=0)
    invite_code = models.CharField(max_length=128)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return 'invite group id %s - %s  count (%s)' % (str(self.id), self.name, self.count)


