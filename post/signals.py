import logging
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

from .models import Post, Comment
from .documents import PostDocument

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@receiver(m2m_changed, sender=Post.liked_by.through, dispatch_uid='post.liked')
def update_post_index(sender, **kwargs):
    post = kwargs['instance']
    post_doc = PostDocument.get(id=post.id)
    post_doc.num_likes = post.liked_by.count()
    post_doc.save()


@receiver(post_save, sender=Comment, dispatch_uid='post.commented')
@receiver(post_delete, sender=Comment, dispatch_uid='post.comment_deleted')
def update_post_index_num_comments(sender, **kwargs):
    comment = kwargs['instance']
    post_doc = PostDocument.get(id=comment.post.id)
    post_doc.num_comments = Comment.objects.filter(post=comment.post)\
        .filter(is_deleted=False).count()
    post_doc.save()
