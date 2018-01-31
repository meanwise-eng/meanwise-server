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

            try:
                user_topic = UserTopic.objects.get(user=post.poster, topic=post.topic,
                                                   interest=post.interest.name, is_work=None)
            except UserTopic.DoesNotExist:
                user_topic = None

            try:
                user_topic_with_category = UserTopic.objects.get(user=post.poster, topic=post.topic,
                    interest=post.interest.name, is_work=post.is_work)
            except UserTopic.DoesNotExist:
                user_topic_with_category = None

            if user_topic is None:
                user_topic = UserTopic(user=post.poster, topic=post.topic,
                                   interest=post.interest.name)
                user_topic.popularity = 1
            if user_topic_with_category is None:
                user_topic_with_category = UserTopic(user=post.poster, topic=post.topic,
                                   interest=post.interest.name, is_work=post.is_work)
                user_topic_with_category.popularity = 1
            user_topic.popularity += popularity
            user_topic_with_category.popularity += popularity

            if user_topic:
                posts = Post.objects.filter(topic=post.topic, poster=post.poster).order_by('-created_on')[:5]
                serializer = PostSummarySerializer(posts, many=True)
                user_topic.top_posts = serializer.data
                user_topic.save()

            if user_topic_with_category:
                posts_with_category = Post.objects.filter(topic=post.topic, poster=post.poster,
                                                          is_work=post.is_work).order_by('-created_on')[:5]
                serializer_with_category = PostSummarySerializer(posts_with_category, many=True)
                user_topic_with_category.top_posts = serializer.data
                user_topic_with_category.save()
