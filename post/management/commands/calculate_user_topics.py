import datetime

from time import sleep

from django.core.management.base import BaseCommand

import elasticsearch

from post.models import Post, UserTopic
from post.documents import PostDocument, post as post_index
from post.serializers import PostSummarySerializer


class Command(BaseCommand):
    help = 'Recalculate the user topics'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        #UserTopic.objects.all().delete()
        posts = Post.objects.filter(is_deleted=False)

        for post in posts:
            popularity = 1
            popularity += post.liked_by.count()
            popularity += post.comments.count()

            topic_text = post.topic.upper()

            try:
                user_topic = UserTopic.objects.get(user=post.poster, topic=topic_text,
                                                   is_work=None)
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

            posts = Post.objects.filter(
                topic=topic_text, poster=post.poster, is_deleted=False
            ).order_by('-created_on')[:5]
            serializer = PostSummarySerializer(posts, many=True)
            user_topic.top_posts = serializer.data
            user_topic.save()

            posts_with_category = Post.objects.filter(topic=topic_text, poster=post.poster,
                                                      is_deleted=False, is_work=post.is_work
            ).order_by('-created_on')[:5]
            serializer_with_category = PostSummarySerializer(posts_with_category, many=True)
            user_topic_with_category.top_posts = serializer_with_category.data
            user_topic_with_category.save()
