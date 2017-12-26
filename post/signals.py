import logging
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

import elasticsearch

from boost.models import Boost

from .models import Post, Comment, UserTopic, Topic
from .documents import PostDocument
from .serializers import PostSummarySerializer

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

@receiver(post_save, sender=Post, dispatch_uid='post.post_saved')
def create_post_index(sender, **kwargs):
    post = kwargs['instance']

    if post.is_deleted:
        return

    try:
        post_doc = PostDocument.get(id=post.id)
    except elasticsearch.NotFoundError:
        post_doc = PostDocument()

    post_doc.set_from_post(post)
    post_doc.save()

@receiver(post_delete, sender=Post, dispatch_uid='post.post_deleted')
def delete_post_index(sender, **kwargs):
    post = kwargs['instance']

    if not post.is_deleted:
        return

    try:
        post_doc = PostDocument.get(id=post.id)
    except elasticsearch.NotFoundError:
        return

    post_doc.delete()


@receiver(m2m_changed, sender=Post.topics.through, dispatch_uid='post.post_saved_user_post')
def update_user_topic(sender, **kwargs):
    post = kwargs['instance']

    popularity = 1
    popularity += post.liked_by.count()
    popularity += post.comments.count()

    if kwargs['reverse'] == True:
        return

    if kwargs['pk_set'] is None:
        return

    for post_topic_id in kwargs['pk_set']:
        topic = Topic.objects.get(pk=post_topic_id)
        try:
            user_topic = UserTopic.objects.get(user=post.poster, topic=topic.text,
                                               interest=post.interest.name)
        except UserTopic.DoesNotExist:
            user_topic = None
            pass

        if kwargs['action'] == 'post_add':
            if user_topic is None:
                user_topic = UserTopic(user=post.poster, topic=topic.text,
                                   interest=post.interest.name)
                user_topic.popularity = 1

            user_topic.popularity += popularity

        if kwargs['action'] == 'post_remove' and user_topic is not None:
            user_topic.popularity -= popularity
            if user_topic.popularity == 0:
                user_topic.popularity = 0

        posts = Post.objects.filter(topics__id=post_topic_id, poster=post.poster).order_by('-created_on')[:5]
        serializer = PostSummarySerializer(posts, many=True)

        user_topic.top_posts = serializer.data
        user_topic.save()

@receiver(post_delete, sender=Post, dispatch_uid='post.post_deleted_user_post')
def reduce_topic_popularity(sender, **kwargs):
    post = kwargs['instance']

    popularity = 1
    popularity += post.liked_by.count()
    popularity += post.comments.count()

    for topic in post.topics.all():
        try:
            user_topic = UserTopic.objects.get(user=post.poster, topic=topic.text,
                                               interest=post.interest.name)
        except UserTopic.DoesNotExist:
            continue

        user_topic.popularity -= popularity
        if user_topic.popularity == 0:
            user_topic.popularity = 0

        user_topic.save()
