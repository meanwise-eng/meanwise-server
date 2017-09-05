from django.db import models
from django.contrib.postgres.fields import JSONField

from post.models import Post, Comment

class DiscussionManager(models.Manager):

    def create_discussion(self):
        discussion = DiscussionItem()
        return discussion


class DiscussionItem(models.Model):

    objects = DiscussionManager()

    TYPE_COMMENT = 'comment'

    post = models.ForeignKey(Post)
    comment = models.ForeignKey(Comment)
    type = models.CharField(max_length=20)
    text = models.TextField()
    datetime = models.DateTimeField()
