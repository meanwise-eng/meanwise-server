import logging
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

from .models import Topic, NewTopic
from post.models import Post

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@receiver(post_save, sender=Post, dispatch_uid='post.create_new_topic')
def add_to_new_topic_queue(sender, **kwargs):
    post = kwargs['instance']

    if Topic.objects.filter(slug=post.topic.upper()).count() > 0:
        return

    if NewTopic.objects.filter(text=post.topic).count() > 0:
        return

    topic = NewTopic(text=post.topic)
    topic.save()
