import datetime

from meanwise_backend.eventsourced import handle_event

from django.contrib.auth.models import User
from .models import Post, PostLiked
from credits.models import Critic, Credits


@handle_event(eventType=PostLiked, category='mw_post_post')
def handle_post_liked(event: PostLiked):
    post = Post.objects.get(post_uuid=event['metadata']['aggregateId'])

    user = User.objects.get(id=event['data']['liked_by'])

    skills = [post.topic]
    critic = Critic.objects.create(from_user_id=user.id, to_user_id=post.poster.id,
                                   post_id=post.id, user_credits=0, rating=3,
                                   skills=skills, created_on=datetime.datetime.now())

    for skill in (skills + ['overall']):
        try:
            credits = Credits.objects.get(user_id=post.poster.id, skill=skill)
        except Credits.DoesNotExist:
            credits = Credits.objects.create(user_id=post.poster.id, skill=skill, credits=0)

        credits.credits += 1
        credits.save()
