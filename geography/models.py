from __future__ import unicode_literals

from django.db import models
from django_countries.fields import CountryField

from common.cache import SerializerCacheManager


class Location(models.Model):
    name = models.CharField(max_length=128)
    city = models.CharField(max_length=64, blank=True, default='')
    area = models.CharField(max_length=128, blank=True, default='')
    country = models.CharField(max_length=64, default='')
    description = models.CharField(max_length=256)
    place_id = models.CharField(max_length=50, blank=True,
                                default='', db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=270, unique=True)
    searchable = models.BooleanField(default=True)

    objects = models.Manager()
    cache = SerializerCacheManager()

    def __unicode__(self):
        return self.description


class City(models.Model):
    city = models.CharField(max_length=128)
    area = models.CharField(max_length=128, blank=True, default='')
    country = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    place_id = models.CharField(max_length=50, blank=True,
                                default='', db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=270, unique=True)
    searchable = models.BooleanField(default=True)

    def __unicode__(self):
        return self.description
