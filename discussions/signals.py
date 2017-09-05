import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DiscussionItem
from post.models import Comment

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@receiver(post_save, sender=Comment, dispatch_uid='discussions.create')
def create_discussion(sender, **kwargs):
    if kwargs['created']:
        comment = kwargs['instance']
        discussion = DiscussionItem()
        discussion.comment = comment
        discussion.post = comment.post
        discussion.text = comment.comment_text
        discussion.datetime = comment.created_on
        discussion.type = DiscussionItem.TYPE_COMMENT

        discussion.save()
