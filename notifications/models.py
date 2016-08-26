from __future__ import unicode_literals

import uuid

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import JSONField
from django.utils.timesince import timesince as djtimesince
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.signals import post_save, post_delete

from .managers import NotificationManager, NotificationRedisManager
from .constants import NotificationType


class Notification(models.Model):
    '''
    Each notification is saved in database. Currently notifications are related
    to a particular user.
    All the activities (except private) whose target is this particular user should
    get the notification.

    #NOTE: Only an activity is allowd to create a notification.
    Currently it can only be created via `create_activity` task
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=3, choices=NotificationType.choices())
    data = JSONField(default={}, blank=True)
    read = models.BooleanField(default=False)
    read_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey('account_profile.Profile',
                                related_name='notifications')
    activity = models.ForeignKey('stream.Activity')

    actor_content_type = models.ForeignKey(ContentType,
                                           related_name='notification_actor')
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    target_content_type = models.ForeignKey(ContentType, blank=True,
                                            null=True,
                                            related_name='notification_target')
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType,
                                                   blank=True, null=True)
    action_object_object_id = models.CharField(max_length=255,
                                               blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type',
                                      'action_object_object_id')
    objects = NotificationManager()
    cache = NotificationRedisManager()

    class Meta:
        ordering = ('-created_on', )
        index_together = [['profile'],
                          ['type'],
                          ['created_on']]

    def __unicode__(self):
        ctx = {'actor': self.actor,
               'type': self.get_type_display(),
               'action_object': self.action_object,
               'target': self.target,
               'timesince': self.timesince()
               }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(type)s %(action_object)s on %(target)s %(timesince)s ago') % ctx
            return _('%(actor)s %(type)s %(target)s %(timesince)s ago') % ctx
        if self.action_object:
            return _('%(actor)s %(type)s %(action_object)s %(timesince)s ago') % ctx
        return _('%(actor)s %(type)s %(timesince)s ago') % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        return djtimesince(self.created_on, now).encode('utf8').replace(b'\xc2\xa0', b' ').decode('utf8')


def post_notification_save(sender, instance, created, **kwargs):
    if created:
        Notification.cache.add(instance)


def post_notification_delete(sender, instance, **kwargs):
    Notification.cache.delete(instance)

post_save.connect(post_notification_save, sender=Notification)
post_delete.connect(post_notification_delete, sender=Notification)
