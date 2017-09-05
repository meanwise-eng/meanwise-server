import elasticsearch
import datetime
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .documents import Influencer
from post.models import Post, Comment
from userprofile.models import UserFriend


@receiver(post_save, sender=Post, dispatch_uid='influencers.post_save')
def add_interests_and_likes(sender, **kwargs):
    if kwargs['created']:
        post = kwargs['instance']
        influencer = Influencer.get_influencer(post.poster.id)
        influencer.interests_weekly = '%s,%s' % (influencer.interests_weekly, post.interest.name)

        influencer.save()


@receiver(post_save, sender=Comment, dispatch_uid='influencers.comment_save')
def add_comment_popularity(sender, **kwargs):
    if kwargs['created']:
        comment = kwargs['instance']
        post = comment.post

        influencer = Influencer.get_influencer(post.poster.id)

        influencer.popularity_weekly = influencer.popularity_weekly + 5

        influencer.save()


@receiver(m2m_changed,
          sender=Post.liked_by.through,
          dispatch_uid='influencers.post_liked_by_added')
def add_likes(sender, **kwargs):
    post = kwargs['instance']
    influencer = Influencer.get_influencer(post.poster.id)

    influencer.popularity_weekly = influencer.popularity_weekly + 3

    influencer.save()


@receiver(post_save, sender=UserFriend, dispatch_uid='influencers.friend_added')
def add_friends(sender, **kwargs):
    user_friend = kwargs['instance']

    if user_friend.status == UserFriend.STATUS_ACCEPTED:
        influencer1 = Influencer.get_influencer(user_friend.user.id)
        influencer2 = Influencer.get_influencer(user_friend.friend.id)

        influencer1.friends += 1
        influencer2.friends += 1

        influencer1.save()
        influencer2.save()
