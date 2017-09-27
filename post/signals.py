import logging
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

from boost.models import Boost

from .models import Post, Comment
from .documents import PostDocument

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@receiver(m2m_changed, sender=Post.liked_by.through, dispatch_uid='post.liked')
def update_post_index(sender, **kwargs):
    post = kwargs['instance']

    post_save.send(Post, instance=post, created=False)


@receiver(post_save, sender=Comment, dispatch_uid='post.commented')
@receiver(post_delete, sender=Comment, dispatch_uid='post.comment_deleted')
def update_post_index_num_comments(sender, **kwargs):
    comment = kwargs['instance']

    post_save.send(Post, instance=comment.post, created=False)


@receiver(post_save, sender=Boost, dispatch_uid='post.boost_added')
def add_boost_for_post_index(sender, **kwargs):
    boost = kwargs['instance']

    if boost.content_type.model_class() != Post:
        return

    post_save.send(Post, instance=boost.content_object, created=False)


@receiver(post_delete, sender=Boost, dispatch_uid='post.boost_deleted')
def remove_boost_from_post_index(sender, **kwargs):
    boost = kwargs['instance']

    if boost.content_type.model_class() != Post:
        return

    post_save.send(Post, instance=boost.content_object, created=False)
