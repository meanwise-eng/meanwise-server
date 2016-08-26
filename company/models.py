from __future__ import unicode_literals
import datetime
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify

from phonenumber_field.modelfields import PhoneNumberField
from taggit.managers import TaggableManager


from .utils import (INFLUENCE_CHOICES, AMBIGUITY_CHOICES, ACHIEVEMENT_CHOICES,
                    COLLECT_VS_IND, OPENNESS_CHOICES, PUBLIC_VS_PRIVATE)


# Create your models here.

GROWTH_PLAN_CHOICES = (
    ('50%', 'Extreme Growth (Over 50% over this year)'),
    ('15-25%', 'Significant Growth (15-25% over this year)'),
    ('NA', "I don't know")
)

class CompanyCulture(models.Model):
    influence   = models.IntegerField(choices=INFLUENCE_CHOICES, default=2)
    adventurous = models.IntegerField(choices=AMBIGUITY_CHOICES, default=2)
    achievement = models.IntegerField(choices=ACHIEVEMENT_CHOICES, default=2)
    col_ind     = models.IntegerField(choices=COLLECT_VS_IND, default=2)
    openness    = models.IntegerField(choices=OPENNESS_CHOICES, default=2)
    pub_vs_priv = models.IntegerField(choices=PUBLIC_VS_PRIVATE, default=2)


class CompanyLocation(models.Model):
    name    = models.CharField(max_length=128)
    isHQ    = models.BooleanField(default=False)
    lon    = models.DecimalField(max_digits=8, decimal_places=3)
    lat     = models.DecimalField(max_digits=8, decimal_places=3)


class CompanyProfile(models.Model):
    # company_logo
    name                = models.CharField(max_length=128, blank=True)
    company_description = models.CharField(max_length=512, null=True,
                                           verbose_name=('Company Description'))
    company_size        = models.IntegerField(validators=[MinValueValidator(1)],
                                              verbose_name=('Company Size'))
    company_email       = models.CharField(max_length=128)
    industry            = models.CharField(max_length=128)
    date_founded        = models.DateField(default=datetime.date.today)
    company_type        = models.CharField(max_length=128)
    company_vision      = models.TextField()
    growth_plans        = models.CharField(max_length=10, choices=GROWTH_PLAN_CHOICES,
                                           default='NA', db_index=True, null=True)
    tags                = TaggableManager(blank=True)
    offices             = models.ManyToManyField(CompanyLocation, blank=True)
    culture             = models.OneToOneField(CompanyCulture, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.company_email


class Company(models.Model):
    """
        Created when user signs up or decides to make a new Company.
        Has references to CompanyProfile, Page if verified.
    """
    company_name = models.CharField(max_length=128, unique=True, db_index=True,
                                    verbose_name=('Company Name'))
    slug         = models.SlugField(max_length=70, unique=True, verbose_name=('Slug'),
                                    default='', null=True, blank=True)
    profile      = models.OneToOneField(CompanyProfile, on_delete=models.CASCADE, blank=True, null=True)
    page         = models.ForeignKey('pages.Page', on_delete=models.CASCADE, null=True, blank=True)
    verified     = models.BooleanField(default=False, verbose_name=('Verified'))

    def __str__(self):
        return self.company_name

    def __unicode__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.slug and not self.id:
            self.slug = slugify(self.company_name)
        super(Company, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Companies"


class EmailConfirmation(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE,
                                   primary_key=True,
                                   verbose_name=('Company Name'))
    email = models.EmailField(max_length=128, unique=True,
                              db_index=True,
                              verbose_name=('Email'))
    token = models.CharField(max_length=256, unique=True,
                             verbose_name=('Token'))
    confirmed = models.BooleanField(default=False,
                                    verbose_name=('Confirmed'))

    def __str__(self):
        return self .company.company_name
