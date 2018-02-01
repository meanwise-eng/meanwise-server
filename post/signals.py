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
def resave_post_docs_so_topic_is_saved(sender, **kwargs):
    post = kwargs['instance']

    if post.is_deleted:
        return

    try:
        post_doc = PostDocument.get(id=post.id)
    except elasticsearch.NotFoundError:
        post_doc = PostDocument()

    post_doc.set_from_post(post)
    post_doc.save()


@receiver(post_save, sender=Post, dispatch_uid='post.post_saved_user_topic')
def update_user_topic(sender, **kwargs):
    post = kwargs['instance']

    popularity = 1
    popularity += post.liked_by.count()
    popularity += post.comments.count()

    if kwargs['created'] == False:
        return

    topic_text = post.topic.upper()
    try:
        user_topic = UserTopic.objects.get(user=post.poster, topic=topic_text, is_work=None)
    except UserTopic.DoesNotExist:
        user_topic = UserTopic(user=post.poster, topic=topic_text)
        user_topic.popularity = 1

    try:
        user_topic_with_category = UserTopic.objects.get(user=post.poster, topic=topic_text,
            is_work=post.is_work)
    except UserTopic.DoesNotExist:
        user_topic_with_category = UserTopic(user=post.poster, topic=topic_text, is_work=post.is_work)
        user_topic_with_category.popularity = 1

    user_topic.popularity += popularity
    user_topic_with_category.popularity += popularity

    posts = Post.objects.filter(topic=topic_text, poster=post.poster).order_by('-created_on')[:5]
    serializer = PostSummarySerializer(posts, many=True)
    user_topic.top_posts = serializer.data

    posts_with_category = Post.objects.filter(topic=topic_text, poster=post.poster,
                                              is_work=post.is_work).order_by('-created_on')[:5]
    serializer_with_category = PostSummarySerializer(posts_with_category, many=True)
    user_topic_with_category.top_posts = serializer_with_category.data

    user_topic.save()
    user_topic_with_category.save()

@receiver(post_delete, sender=Post, dispatch_uid='post.post_deleted_user_post')
def reduce_topic_popularity(sender, **kwargs):
    post = kwargs['instance']

    popularity = 1
    popularity += post.liked_by.count()
    popularity += post.comments.count()

    topic_text = post.topic.upper()
    try:
        user_topic = UserTopic.objects.get(user=post.poster, topic=topic_text, is_work=None)
    except UserTopic.DoesNotExist:
        user_topic = None

    try:
        user_topic_with_category = UserTopic.objects.get(user=post.poster, topic=topic_text,
            is_work=post.is_work)
    except UserTopic.DoesNotExist:
        user_topic_with_category = None

    if user_topic:
        user_topic.popularity -= popularity

        if user_topic.popularity < 0:
            user_topic.popularity = 0
            posts = Post.objects.filter(
                topic=topic_text, poster=post.poster, is_deleted=False
            ).order_by('-created_on')[:5]
            serializer = PostSummarySerializer(posts, many=True)
            user_topic.top_posts = serializer.data

        user_topic.save()

    if user_topic_with_category:
        user_topic_with_category.popularity -= popularity
        if user_topic_with_category.popularity < 0:
            user_topic_with_category.popularity = 0

            posts_with_category = Post.objects.filter(topic=topic_text, poster=post.poster,
                                                      is_deleted=False, is_work=post.is_work
            ).order_by('-created_on')[:5]
            serializer_with_category = PostSummarySerializer(posts_with_category, many=True)
            user_topic_with_category.top_posts = serializer_with_category.data

        user_topic_with_category.save()
