from __future__ import unicode_literals

import uuid

from django.db import models
from django.utils.translation import ugettext as _
from django.utils.timesince import timesince as djtimesince
from django.contrib.postgres.fields import JSONField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .constants import VerbType
from .managers import ActivityManager


class Activity(models.Model):
    '''
    Activity is an action that can be populated in Activity Stream or Notification
    Nomenclature based on http://activitystrea.ms/specs/atom/1.0/
    Generalized Format::
    <actor> <verb> <time>
    <actor> <verb> <target> <time>
    <actor> <verb> <action_object> <target> <time>

    If private then only the actor should be able to see this activity.
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_content_type = models.ForeignKey(ContentType, related_name='actor')
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')
    verb = models.CharField(max_length=3, choices=VerbType.choices())

    target_content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                            related_name='target')
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType, blank=True,
                                                   null=True,
                                                   related_name='action_object'
                                                   )
    action_object_object_id = models.CharField(max_length=255,
                                               blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type',
                                      'action_object_object_id')

    data = JSONField(default={}, blank=True)
    is_private = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    objects = ActivityManager()

    class Meta:
        ordering = ('-created_on', )
        verbose_name_plural = 'Activities'
        index_together = [['verb', 'target_object_id', 'target_content_type'],
                          ['created_on']
                          ]

    def __unicode__(self):
        ctx = {'actor': self.actor,
               'verb': self.get_verb_display(),
               'action_object': self.action_object,
               'target': self.target,
               'timesince': self.timesince()
               }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago') % ctx
            return _('%(actor)s %(verb)s %(target)s %(timesince)s ago') % ctx
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(timesince)s ago') % ctx
        return _('%(actor)s %(verb)s %(timesince)s ago') % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        return djtimesince(self.created_on,
                           now).encode('utf8').replace(b'\xc2\xa0',
                                                       b' ').decode('utf8')
