import datetime

from meanwise_backend.eventsourced import handle_event

from django.contrib.auth.models import User # type: ignore
from post.models import Post, PostLiked
from credits.models import Critic, Credits

from .critic import create_critic, Criticized


@handle_event(eventType=PostLiked, category='mw_post_post')
def handle_post_liked(event: PostLiked):
    post = Post.objects.get(post_uuid=event.metadata['aggregateId'])

    user = User.objects.get(id=event.data['liked_by'])

    skill = post.topic

    create_critic(criticizer=user.id, criticized=post.poster.id, post_id=post.id,
                  rating=3, skill=skill)


@handle_event(eventType=Criticized, category='mw_credits_credits')
def increase_read_model_credits(event: Criticized):
    skill = event.data['skill']
    criticizer = event.data['criticizer']
    criticized = event.metadata['aggregateId']
    try:
        credits = Credits.objects.get(user_id=criticized, skill=skill)
    except Credits.DoesNotExist:
        credits = Credits.objects.create(user_id=criticized, skill=skill, credits=0)
    else:
        credits.credits += event.data['skill_endorsements']
        credits.save()

    try:
        credits = Credits.objects.get(user_id=criticized, skill='overall')
    except Credits.DoesNotExist:
        credits = Credits.objects.create(user_id=criticized, skill='overall', credits=0)
    else:
        credits.credits += event.data['overall_endorsements']
        credits.save()
