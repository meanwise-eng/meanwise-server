from __future__ import unicode_literals

from django.db import models
from django.utils.text import slugify
from company.models import Company

from taggit.managers import TaggableManager

RICH_TEXT_LEN = 512


class Leader(models.Model):
    name    = models.CharField(max_length=64)
    role    = models.CharField(max_length=64)
    # image =
    about   = models.TextField(blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Page(models.Model):
    # Overview
    name          = models.CharField(max_length=64, blank=False, unique=True)
    public        = models.BooleanField(default=True, blank=True)
    slug          = models.SlugField(max_length=70, unique=True, verbose_name=('Slug'),
                                   default='', null=True, blank=True)
    biography     = models.CharField(max_length=512)

    # Culture
    video         = models.TextField(blank=True)
    tags          = TaggableManager(blank=True)
    about_culture = models.TextField(blank=True)
    about_company = models.TextField(blank=True)

    def __str__(self):
        return self.company

    def __unicode__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug and not self.id:
            self.slug = slugify(self.name)
        super(Page, self).save(*args, **kwargs)

