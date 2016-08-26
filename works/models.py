from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.contenttypes.fields import GenericRelation

from hitcount.models import HitCount
from easy_thumbnails.fields import ThumbnailerImageField

from common.utils import slugify
from common.cache import SerializerCached
from common.models import CommentLikeableModel

from .managers import WorkManager
from .constants import WorkItemType, WorkState
from .cache import WorkSerializerCachedManager


class Work(CommentLikeableModel, SerializerCached):
    '''
    A work is a single project/work done by a user.
    '''
    profile = models.ForeignKey('account_profile.Profile')
    title = models.CharField(max_length=128)
    slug = models.SlugField(max_length=140)
    description = models.CharField(max_length=1024, blank=True, default='')
    order = ArrayField(models.IntegerField(), default=[], blank=True)
    state = models.CharField(max_length=2,
                             choices=WorkState.choices(),
                             default=WorkState.DRAFT)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    searchable = models.BooleanField(default=True)
    cover_photo = models.URLField(default='', blank=True)
    skills = models.ManyToManyField('account_profile.Skill')
    hit_count = GenericRelation(HitCount, object_id_field='object_pk',
                                related_query_name='hit_count_relation')
    objects = WorkManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super(Work, self).save(*args, **kwargs)

    @property
    def cover_image_url(self):
        return ''

    @property
    def views_count(self):
        return self.hit_count.get().hits

    @property
    def notification_slug(self):
        return '/%s/work/%s' % (self.profile.username, self.id)

    def delete(self):
        self.state = WorkState.DELETED
        self.save()
        post_delete.send(sender=self.__class__, instance=self)


class Workitem(models.Model):
    '''
    A work item is basically a link(embeded, photo, code) which can be added to
    a work.
    '''
    work = models.ForeignKey(Work, related_name='workitems')
    description = models.CharField(max_length=1024, blank=True, default='')
    type = models.CharField(max_length=3, choices=WorkItemType.choices())
    link = models.CharField(max_length=1024)
    info = JSONField(default={})
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.link


def post_work_save(sender, instance, created, **kwargs):
    from .serializers import WorkSerializer, NotificationWorkSerializer
    Work.cache.serialized(instance, NotificationWorkSerializer,
                          force_fetch=True)


def post_work_delete(sender, instance, **kwargs):
    # Dont clear the cache as this will be needed in notifications.
    # We do not remove notifications if work is marked as deleted
    # from .serializers import NotificationWorkSerializer
    # Work.cache.clear_cache(instance, NotificationWorkSerializer)
    pass


def post_workitem_save(sender, instance, **kwargs):
    pass


def post_workitem_delete(sender, instance, **kwargs):
    work = instance.work
    if instance.id in work.order:
        work.order.remove(instance.id)
        work.save()

# Not using cache for this right now.
post_save.connect(post_work_save, sender=Work)
post_delete.connect(post_work_delete, sender=Work)
post_save.connect(post_workitem_save, sender=Workitem)
post_delete.connect(post_workitem_delete, sender=Workitem)
