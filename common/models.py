from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.signals import post_save, post_delete

from stream.constants import VerbType
from stream.utils import create as create_activity, delete as delete_activity


class Comment(models.Model):
    '''
    This is a generic model that can be attached to any model in order to provide
    comment functionality.
    '''
    content_type = models.ForeignKey(ContentType,
                                     related_query_name='comments')
    object_id = models.CharField(max_length=255)
    instance = GenericForeignKey('content_type', 'object_id')
    profile = models.ForeignKey('account_profile.Profile')
    text = models.CharField(max_length=1024)
    deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s by %s' % (self.text, self.profile)

    def delete(self):
        self.deleted = True
        self.save()
        post_delete.send(sender=self.__class__, instance=self)


class Like(models.Model):
    '''
    This is a generic model for storing likes.
    '''
    content_type = models.ForeignKey(ContentType, related_name='likes')
    object_id = models.CharField(max_length=255)
    instance = GenericForeignKey('content_type', 'object_id')
    profile = models.ForeignKey('account_profile.Profile')
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s likes %s' % (self.profile, self.instance)


class CommentableModel(models.Model):
    comments = GenericRelation('common.Comment')

    class Meta:
        abstract = True

    @property
    def comments_count(self):
        if not hasattr(self, '_comments_count'):
            self._comments_count = self.comments.count()
        return self._comments_count


class LikeableModel(models.Model):
    likes = GenericRelation('common.Like')

    class Meta:
        abstract = True

    @property
    def likes_count(self):
        if not hasattr(self, '_likes_count'):
            self._likes_count = self.likes.count()
        return self._likes_count

    def liked_by_current_profile(self, profile):
        return bool(self.likes.filter(profile=profile).count())


class CommentLikeableModel(models.Model):
    comments = GenericRelation('common.Comment')
    likes = GenericRelation('common.Like')

    class Meta:
        abstract = True

    @property
    def likes_count(self):
        if not hasattr(self, '_likes_count'):
            self._likes_count = self.likes.count()
        return self._likes_count

    @property
    def comments_count(self):
        if not hasattr(self, '_comments_count'):
            self._comments_count = self.comments.count()
        return self._comments_count

    def liked_by_current_profile(self, profile):
        return bool(self.likes.filter(profile=profile).count())


def post_like_save(sender, instance, created, **kwargs):
    if instance.profile == instance.instance.profile:
        is_private = True
    else:
        is_private = False
    if created:
        create_activity(instance.profile, verb=VerbType.LIKED,
                        target=instance.instance, is_private=is_private)


def post_like_delete(sender, instance, **kwargs):
    if instance.profile == instance.instance.profile:
        is_private = True
    else:
        is_private = False
    delete_activity(instance.profile, verb=VerbType.LIKED,
                    target=instance.instance, is_private=is_private)


def post_comment_save(sender, instance, created, **kwargs):
    if instance.profile == instance.instance.profile:
        is_private = True
    else:
        is_private = False
    if created:
        create_activity(instance.profile, verb=VerbType.COMMENTED,
                        target=instance.instance, action_object=instance, is_private=is_private)


def post_comment_delete(sender, instance, **kwargs):
    if instance.profile == instance.instance.profile:
        is_private = True
    else:
        is_private = False
    delete_activity(instance.profile, verb=VerbType.COMMENTED,
                    target=instance.instance, action_object=instance, is_private=is_private)


post_save.connect(post_like_save, sender=Like)
post_delete.connect(post_like_delete, sender=Like)
post_save.connect(post_comment_save, sender=Comment)
post_delete.connect(post_comment_delete, sender=Comment)
