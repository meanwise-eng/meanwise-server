from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib.postgres.fields import JSONField

from common.utils import slugify
from common.cache import SerializerCacheManager

from .cache import EventSerializerCachedManager
from .managers import EventManager, CourseMajorManager
from .constants import EventType


class Degree(models.Model):
    '''
    These are pre-defined on the backend
    '''
    text        = models.CharField(max_length=128)
    slug        = models.CharField(max_length=128, unique=True)
    code        = models.CharField(max_length=2)
    created_on  = models.DateTimeField(auto_now_add=True)
    last_updated= models.DateTimeField(auto_now=True)
    published   = models.BooleanField(default=False)
    searchable  = models.BooleanField(default=True)

    objects     = models.Manager()
    cache       = SerializerCacheManager()

    def __unicode__(self):
        return '%s' % self.text

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = slugify(self.text)
        super(Degree, self).save(*args, **kwargs)


class CourseMajor(models.Model):
    '''
    These are populated by Users. But there should me minimum repetition
    '''
    text = models.CharField(max_length=128)
    slug = models.CharField(max_length=128, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    searchable = models.BooleanField(default=True)

    objects = CourseMajorManager()
    cache = SerializerCacheManager()

    def __unicode__(self):
        return '%s' % self.text

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = slugify(self.text)
        super(CourseMajor, self).save(*args, **kwargs)


class Event(models.Model):
    '''
    Info should always exists for these events.
    '''
    type = models.CharField(max_length=2, choices=EventType.choices())
    start_day = models.PositiveIntegerField(blank=True, null=True)
    start_month = models.PositiveIntegerField(blank=True, null=True)
    start_year = models.PositiveIntegerField(blank=True, null=True)
    end_day = models.PositiveIntegerField(blank=True, null=True)
    end_month = models.PositiveIntegerField(blank=True, null=True)
    end_year = models.PositiveIntegerField(blank=True, null=True)
    ongoing = models.BooleanField(default=False)
    description = models.CharField(max_length=1024)
    city = models.ForeignKey('geography.City')
    info = JSONField(default={})
    profile = models.ForeignKey('account_profile.Profile', db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, db_index=True)

    objects = EventManager()
    cache = EventSerializerCachedManager()

    def __unicode__(self):
        return '%s %s' % (self.description, self.profile)

    def delete(self):
        self.deleted = True
        self.save()


def post_event_save(sender, instance, **kwargs):
    # Remove from cache
    Event.cache.clear_cache(instance.profile)

post_save.connect(post_event_save, sender=Event,
                  dispatch_uid='post_event_save')
