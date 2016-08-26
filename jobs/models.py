from __future__ import unicode_literals
import datetime
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from elasticutils import S, Indexable
from elasticutils.contrib.django import MappingType

from account_profile.models import Skill
from common.utils import ListField

from .managers import JobManager

# Create your models here.

JOB_KIND_CHOICES = (
    ('FT', 'Full-time'),
    ('PT', 'Part-time'),
    ('C', 'Contract'),
    ('FL', 'Freelance'),
    ('R', 'Remote')
)


class Job(models.Model):
    """
        Model for Job posts. Stores basic job information and
        optimal values for personality.

        Default values for personality are "middle values".

        attitude: { extrovert: 1.0, introvert: 2.0 },
        consciousness: { sensing: 2.0, intuition: 5.0 },
        openness: { transparent: 5.0, restricted: 1.0 },
        decision-making { judging: 2.0, perceiving: 1.0 },
        agreeableness: { sympathetic: 1.0, affectionate: 4.0 },
        emotional-stability: { anxious: 1.0, calm: 3.0 },
        organizing: { organized: 1.0, unorganized: 3.0 },
        reasoning: { low: 1.0, high: 5.0 } ,
        creativity: { low: 1.0, high: 5.0 } ,
        critical-thinking: { low: 1.0, high: 5.0 }
    """
    title           = models.CharField(max_length=128)
    description     = models.CharField(max_length=512, blank=True)
    role            = models.CharField(max_length=128, blank=True)
    last_update     = models.DateField(default=datetime.date.today, blank=True)
    company         = models.ForeignKey('company.Company', on_delete=models.CASCADE, blank=True)
    compensation    = models.CharField(max_length=128)
    # location        = models.ForeignKey('company.CompanyLocation', 
    #                                     on_delete=models.CASCADE)
    kind            = models.CharField(max_length=2, choices=JOB_KIND_CHOICES,
                                    default='FT')
    skills          = models.ManyToManyField(Skill, blank=True)
    # experiences     = ListField(blank=True, verbose_name=('Experiences'))
    # education       = ListField(blank=True, verbose_name=('Education'))
    # languages       = ListField(blank=True, verbose_name=('Languages'))

    slug            = models.SlugField(max_length=70, unique=True, verbose_name=('Slug'),
                                    default='', null=True, blank=True)

    # Personality analysis
    attitude            = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(2.0)],
                                            default=1.5)
    consciousness       = models.FloatField(validators=[MinValueValidator(2.0), MaxValueValidator(5.0)],
                                            default=3.5)
    openness            = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
                                            default=3.0)
    decision_making     = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(2.0)],
                                            default=1.5)
    agreeableness       = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(4.0)],
                                            default=2.5)
    emotional_stability = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(3.0)],
                                            default=2.0)
    organizing          = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(3.0)],
                                            default=2.0)
    reasoning           = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
                                            default=3.0)
    creativity          = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
                                            default=3.0)
    critical_thinking   = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
                                            default=3.0)

    objects         = JobManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and not self.id:
            self.slug = slugify(self.title)
        super(Job, self).save(*args, **kwargs)

class JobApplication(models.Model):
    """
        NOTE: profile/job are allowed to be blank in order to avoid
              serializer errors. profile and job object will be passed in
              via  --- serializer.save(profile=p, job=j)

              JobApplication will only be created in jobs.views.applyJob
    """
    profile = models.ForeignKey('account_profile.Profile',
                                on_delete=models.CASCADE, blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True)
    # user reference
    # extra fields

class JobMappingType(MappingType, Indexable):
    @classmethod
    def get_model(cls):
        return Job

    @classmethod
    def get_mapping(cls):
        return {
            'properties' : {
                'id': {'type':'integer'},
                'title': {'type': 'string', 'index': 'not_analyzed'},
                'description': {'type': 'string', 'analyzer': 'snowball'},
                'skills': {'type': 'string'}

            }
        }

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """Converts obj into a mapping instance. """
        if obj is None:
            obj = cls.get_model.get(pk=obj_id)
        return {
            'id':           obj.id,
            'title' :       obj.title,
            'description':  obj.description,
            'skills':       [skill.text for skill in obj.skills]
        }


    def get_object(self, pk):
        return self.get_model().objects.get(pk=pk)

    def get_objects_by_skill(self, skill):
        pass

searcher = JobMappingType.search()

